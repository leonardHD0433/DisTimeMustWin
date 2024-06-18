import unittest
from app import app

class RespondUrlStatusTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()

    def test_valid_url(self):
        app.config['URL_TO_CHECK'] = 'https://www.google.com'
        response = self.app.get('/check-url-status')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"Response": "URL received"})

    def test_invalid_url(self):
        app.config['URL_TO_CHECK'] = 'invalid_url'
        response = self.app.get('/check-url-status')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, {"Error": "Invalid URL"})

    def test_missing_url(self):
        app.config['URL_TO_CHECK'] = None
        response = self.app.get('/check-url-status')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, {"Error": "Oops, something went wrong."})

if __name__ == '__main__':
    unittest.main()