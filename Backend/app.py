from flask import Flask, make_response, request, abort
from flask_restful import Api, Resource, reqparse
from functools import wraps
import subprocess
from urllib.parse import urlparse
import threading

app = Flask(__name__)
api = Api(app)

# Load the API key from a file
with open('api_key.txt', 'r') as file:
    API_KEY = file.read().strip()
    #print("API Key:", API_KEY)

# Decorator to require an API key
def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        received_api_key = request.headers.get('astroapi')
        #print("Received API Key:", received_api_key)
        if received_api_key != API_KEY:
            abort(401)  # Unauthorized access
        return f(*args, **kwargs)
    return decorated_function

#Thread Event 
background_task_status = threading.Event()

#Function to check if the URL is valid
def is_url(url):
  try:
    result = urlparse(url)
    return all([result.scheme, result.netloc])
  except ValueError:
    return False

#Function to scan the URL
def scan_url():
    command = ["python", "feature_extraction_script.py"]
    result = subprocess.run(command, capture_output=True, text=True)
    background_task_status.set()

#Function to test for server connection
@app.route("/")
def showHomePage():
    return "This is the Flask server!"
    
#Class to receive URL from frontend
class Url_From_Frontend(Resource):
    @require_api_key
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('url', type=str)
        args = parser.parse_args()
        received_url = args['url']
        app.config['URL_TO_CHECK'] = received_url
        background_task_status.clear() # Clear any running tasks
        # Now you have the URL from the frontend and can do something with it

        print(is_url(received_url))
        if is_url(received_url):
            #pass url to url.txt, but clear url.txt first to avoid appending
            with open("url.txt", "w") as f:
                f.write(received_url)

            threading.Thread(target=scan_url).start() # Start the background task to scan the URL
            #URL received
            return make_response("URL received", 200)
        else:
            #Invalid URL
            print("Invalid URL")
            return make_response("Invalid URL", 400)

#Class to respond with the URL label
class Respond_Url_Label(Resource):
    @require_api_key
    def get(self):

        background_task_status.wait() # Wait for the background task to finish
        
        with open("url_label.txt", "r") as f:
                label = f.read()

        return make_response(label, 200)

# Add the resources to the API         
api.add_resource(Respond_Url_Label, '/check-url-label')
api.add_resource(Url_From_Frontend, '/get-url-from-frontend')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)