import json
import logging
import requests
from flask import Flask, render_template, request, flash, make_response, jsonify, session, redirect
from google.auth.transport import requests as auth_requests
import google.oauth2.id_token

firebase_request_adapter = auth_requests.Request()

app = Flask(__name__)

app.secret_key = 'secret'


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
            claims = google.oauth2.id_token.verify_firebase_token(
                id_token, firebase_request_adapter)

        except ValueError as exc:
            # This will be raised if the token is expired or any other
            # verification checks fail.
            error_message = str(exc)

    url = "https://europe-west2-ad-cain.cloudfunctions.net/dispaly_products_mongoDB"
    mongo_products = requests.get(url)
    jresponse = mongo_products.text
    data = json.loads(jresponse)

    return render_template('index.html', user_data=claims,
                           data=data,
                           error_message=error_message)


@app.route('/login')
def login():
    # Verify Firebase auth.
    id_token = request.cookies.get("token")
    error_message = None
    claims = None

    if id_token:
        try:
            # Verify the token against the Firebase Auth API. This example verifies the token on each page load.
            claims = google.oauth2.id_token.verify_firebase_token(
                id_token, firebase_request_adapter)

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
            claims = google.oauth2.id_token.verify_firebase_token(
                id_token, firebase_request_adapter)

        except ValueError as exc:
            # This will be raised if the token is expired or any other verification checks fail.
            error_message = str(exc)

        return render_template('profile.html', user_data=claims, error_message=error_message)
    else:
        error_message = "You Need to login first!"
        return render_template('login.html', user_data=claims, error_message=error_message)


@app.route('/product=<id>')
def product(id):
    # Verify Firebase auth.
    id_token = request.cookies.get("token")
    error_message = None
    claims = None

    if id_token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(
                id_token, firebase_request_adapter)
        except ValueError as exc:
            error_message = str(exc)

    url = "https://europe-west2-ad-cain.cloudfunctions.net/single_product?id=" + id
    mongo_product = requests.get(url)
    jresponse = mongo_product.text
    data = json.loads(jresponse)

    return render_template('product.html', user_data=claims, data=data, error_message=error_message)


@app.route('/cart/<int:id>')
def add_to_cart(id):
    if 'cart' not in session:
        session['cart'] = []

    session['cart'].append(id)
    print(session)

    flash("Successfully added to cart.")

    return redirect('/index')


@app.route('/removecart/<int:index>')
def remove_from_cart(index):
    session['cart'].pop(index)
    session.modified = True
    return redirect('/cart')


@app.route('/cartclear')
def cartclear():
    session['cart'] = []
    return redirect('/index')


@app.route('/cart')
def cart():
    cart_products = []
    for n in session['cart']:
        product_data = "https://europe-west2-ad-cain.cloudfunctions.net/single_product?id=" + str(n)
        mongo_product = requests.get(product_data)
        jresponse = mongo_product.text
        data = json.loads(jresponse)

        cart_products.append(data)

    return render_template('cart.html', data=cart_products)


if __name__ == '__main__':
    app.run()
