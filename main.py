import json
import logging
import requests
from flask import Flask, render_template, request, flash, make_response, jsonify
from google.auth.transport import requests as auth_requests
import google.oauth2.id_token

firebase_request_adapter = auth_requests.Request()

app = Flask(__name__)


@app.route('/')
@app.route('/index')
def home():
    # Verify Firebase auth.
    id_token = request.cookies.get("token")
    error_message = None
    claims = None

    if id_token:
        try:
            # Verify the token against the Firebase Auth API. This example
            # verifies the token on each page load. For improved performance,
            # some applications may wish to cache results in an encrypted
            # session store (see for instance
            # http://flask.pocoo.org/docs/1.0/quickstart/#sessions).
            claims = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)

        except ValueError as exc:
            # This will be raised if the token is expired or any other
            # verification checks fail.
            error_message = str(exc)

    url="https://europe-west2-ad-cain.cloudfunctions.net/dispaly_products_mongoDB"
    mongo_products = requests.get(url)
    jresponse = mongo_products.text
    data = json.loads(jresponse)

    return render_template('index.html', user_data=claims,  
    data=data, 
    error_message=error_message)

#send product data from the mongo db to index
# @app.route('/', methods=['GET'])
# def mongo_products():
#     url="https://europe-west2-ad-cain.cloudfunctions.net/dispaly_products_mongoDB"
#     response = requests.get(url)
#     return(response.content)


@app.route('/login')
def login():
    # Verify Firebase auth.
    id_token = request.cookies.get("token")
    error_message = None
    claims = None

    if id_token:
        try:
            # Verify the token against the Firebase Auth API. This example verifies the token on each page load.
            claims = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)

        except ValueError as exc:
            # This will be raised if the token is expired or any other verification checks fail.
            error_message = str(exc)

        error_message = "You are already logged in!"
        return render_template('index.html', user_data=claims, error_message=error_message)
    else:
        return render_template('login.html', user_data=claims, error_message=error_message)


@app.route('/profile')
def profile():
    # Verify Firebase auth.
    id_token = request.cookies.get("token")
    error_message = None
    claims = None

    if id_token:
        try:
            # Verify the token against the Firebase Auth API. This example verifies the token on each page load
            claims = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)

        except ValueError as exc:
            # This will be raised if the token is expired or any other verification checks fail.
            error_message = str(exc)

        return render_template('profile.html', user_data=claims, error_message=error_message)
    else:
        error_message = "You Need to login first!"
        return render_template('login.html', user_data=claims, error_message=error_message)

# @app.route('/logout')
# def logout():
#     id_token = request.cookies.get("token")
#     if request.cookies.get(id_token):
#         request.set_cookie('token', '', expires=0)
#     return render_template('index.html')

# if __name__ == "__main__": 
#     # Used when running locally only. When deploying to Google App 
#     # Engine, a webserver process such as Gunicorn will serve the app. This 
#     # can be configured by adding an `entrypoint` to app.yaml. 
#     app.run(host="localhost", port=8080, debug=True)
