from flask import Flask, request, jsonify
from flask_restful import Api, Resource, reqparse
import validators

app = Flask(__name__)
api = Api(app)

def validate_url(url):
    return validators.url(url)

class Url_From_Frontend(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('url', type=str)
        args = parser.parse_args()
        received_url = args['url']
        app.config['URL_TO_CHECK'] = received_url
        # Now you have the URL from the frontend and can do something with it
        return {"URL": received_url}, 200

class Respond_Url_Status(Resource):
    def get(self):
        url = app.config['URL_TO_CHECK']
        # You'll need to determine how to get the URL to check here
        if url is None:
            return {"Error": "Oops, something went wrong."}, 400
        elif validate_url(url):
            return {"Response": "URL received"}, 200
        else:
            return {"Error": "Invalid URL"}, 400
            

api.add_resource(Respond_Url_Status, '/check-url-status')
api.add_resource(Url_From_Frontend, '/get-url-from-frontend')

if __name__ == '__main__':
    app.run(debug=True)