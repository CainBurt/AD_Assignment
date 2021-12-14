import json
import requests
from flask import Flask, render_template, request, flash, session, redirect
from google.auth.transport import requests as auth_requests
import google.oauth2.id_token

firebase_request_adapter = auth_requests.Request()

app = Flask(__name__)

app.secret_key = 'wdasfvhtbrnhjyjjikg'


# checks if a user is logged in:
def check_user():
    # Verify Firebase auth.
    id_token = request.cookies.get("token")
    error_message = None
    claims = None
    if id_token:
        try:
            # Verify the token against the Firebase Auth API. This example verifies the token on each page load.
            claims = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
        except ValueError as exc:
            error_message = str(exc)
    return claims, error_message


@app.route('/')
@app.route('/index')
def home():
    # displays all of the products on the home page
    url = "https://europe-west2-ad-cainburt.cloudfunctions.net/display_products_mongoDB"
    mongo_products = requests.get(url)
    jresponse = mongo_products.text
    data = json.loads(jresponse)

    return render_template('index.html', user_data=check_user()[0], data=data, error_message=check_user()[1])


@app.route('/login')
def login():
    # shows the login page if not logged in
    if check_user()[0]:
        error_message = "You are already logged in!"
        return render_template('index.html', user_data=check_user()[0], error_message=error_message)
    else:
        return render_template('login.html', user_data=check_user()[0])


@app.route('/profile', methods=['GET'])
def profile():
    # gets all the orders for the user that is logged in.
    if check_user()[0]:

        user_id = check_user()[0]['user_id']
        product_list = []

        fbase_url = "https://europe-west2-ad-cainburt.cloudfunctions.net/display_orders_firestore?uid=" + user_id
        firebase_product = requests.get(fbase_url)
        firebase_order = firebase_product.text
        fbase_data = json.loads(firebase_order)

        # get the product info from mongoDB for the ids in the order in firestore
        for i in fbase_data:
            for k, v in list(i['order'].items()):
                if k == "products_id":
                    v = json.loads(v)
                    for i in v:
                        url = "https://europe-west2-ad-cainburt.cloudfunctions.net/display_single_product_mongoDB?id=" + str(
                            i)
                        mongo_product = requests.get(url)
                        jresponse = mongo_product.text
                        data = json.loads(jresponse)

                        # filters the ids and names and adds them to a list to return to html
                        for p in data:
                            prods = {'id': p['id'], 'name': p['name']}
                            product_list.append(prods)

        # removes the duplicates from the list of ids and names of products.
        result = []
        for i in range(len(product_list)):
            if product_list[i] not in product_list[i + 1:]:
                result.append(product_list[i])

        return render_template('profile.html', user_data=check_user()[0], orders=fbase_data, productlist=result)
    else:
        error_message = "You Need to login first!"
        return render_template('login.html', user_data=check_user()[0], error_message=error_message)


@app.route('/product/<int:id>')
def product(id):
    # gets all the info of a product from the id
    url = "https://europe-west2-ad-cainburt.cloudfunctions.net/display_single_product_mongoDB?id=" + str(id)
    mongo_product = requests.get(url)
    jresponse = mongo_product.text
    data = json.loads(jresponse)

    return render_template('product.html', user_data=check_user()[0], data=data)


@app.route('/cart/<int:id>')
def add_to_cart(id):
    # creates a cart session if there isnt one and adds the product ids to it
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
    # if cart is empty, redirects to index page if not gets all the data for the products in the cart
    if session['cart']:
        cart_products = []
        for n in session['cart']:
            product_data = "https://europe-west2-ad-cainburt.cloudfunctions.net/display_single_product_mongoDB?id=" + str(
                n)
            mongo_product = requests.get(product_data)
            jresponse = mongo_product.text
            data = json.loads(jresponse)

            cart_products.append(data)

        return render_template('cart.html', data=cart_products, user_data=check_user()[0])
    else:
        return redirect('/index')


@app.route('/order', methods=['GET', 'POST'])
def order():
    # send cart data to order page if logged in and uses the cloud function to get the name and price based on the ids in the cart
    if check_user()[0] is not None:
        product_order = []
        for product_id in session['cart']:
            product = "https://europe-west2-ad-cainburt.cloudfunctions.net/display_single_product_mongoDB?id=" + str(
                product_id)
            mongo_product = requests.get(product)
            jresponse = mongo_product.text
            data = json.loads(jresponse)
            product_order.append(data)

            # send the submitted form data to the cloud function that stores the order in firestore
            if request.method == "POST":
                user_name = request.form['firstname']
                user_email = request.form['email']
                user_address = request.form['address']
                user_city = request.form['city']
                user_county = request.form['county']
                user_postcode = request.form['zip']

                user_cart = request.form['cart']

                user_id = check_user()[0]['user_id']

                url = "https://europe-west2-ad-cainburt.cloudfunctions.net/store_orders_firestore?uid=" + user_id + "&name=" + user_name + "&email=" + user_email + "&address=" + user_address + "&city=" + user_city + "&county=" + user_county + "&zip=" + user_postcode + "&cart=" + user_cart
                requests.get(url)
                session.pop('cart')
                return redirect('/profile')

        return render_template('order.html', data=product_order, user_data=check_user()[0])
    else:
        return redirect('/login')


# handles the new product data and sends to the cloud function to add to the database
@app.route('/newproduct', methods=['GET', 'POST'])
def new_product_form():
    # checks if user is ADMIN
    if check_user()[0] and check_user()[0]['email'] == 'cain.m.burt@gmail.com':
        if request.method == "POST":
            form = request.form
            missing = list()

            # checks empty inputs - if they are returns with an error, if not it sends the data to the cloud func to store the product.
            for k, v in form.items():
                if v == "":
                    missing.append(k)

            if missing:
                feedback = f"Missing fields for {', '.join(missing)}"
                return render_template("/newproduct.html", user_data=check_user()[0], feedback=feedback)
            else:
                name = request.form['name']
                desc = request.form['description']
                image = request.form['image']
                price = request.form['price']

                url = "https://europe-west2-ad-cainburt.cloudfunctions.net/store_product_mongoDB?name=" + name + "&desc=" + desc + "&img=" + image + "&price=" + price
                response = requests.get(url)
                feedback = response.content
            return render_template("/newproduct.html", user_data=check_user()[0], feedback=feedback)
        return render_template('/newproduct.html', user_data=check_user()[0])
    else:
        return render_template('/index.html', error_message="You are not a ADMIN!", user_data=check_user()[0])


@app.route('/deleteproduct/<id>')
def delete_product(id):
    # checks user is admin as only they can delete a product
    if check_user()[0] and check_user()[0]['email'] == 'cain.m.burt@gmail.com':
        url = "https://europe-west2-ad-cainburt.cloudfunctions.net/delete_product_mongoDB?id=" + str(id)
        response = requests.get(url)
        feedback = response.content
        return render_template("/index.html", user_data=check_user()[0], error_message=feedback)
    else:
        return render_template('/index.html', error_message="You are not a ADMIN!", user_data=check_user()[0])


@app.route('/deleteorder/<oid>')
def delete_order(oid):
    # checks user is logged in as they can only delete their own orders.
    if check_user()[0]:
        user_id = check_user()[0]['user_id']

        order_id = oid
        url = "https://europe-west2-ad-cainburt.cloudfunctions.net/delete_order_firebase?uid=" + user_id + "&oid=" + order_id
        response = requests.get(url)
        feedback = response.content
        return render_template('/profile.html', user_data=check_user()[0], feedback=feedback)
    else:
        return render_template('/index.html', error_message="You havent logged in", user_data=check_user()[0])


@app.route('/editproduct/<int:id>', methods=['GET', 'POST'])
def edit_product(id):
    # checks user is admin as only they can edit products
    if check_user()[0] and check_user()[0]['email'] == 'cain.m.burt@gmail.com':
        if request.method == "POST":
            form = request.form
            missing = list()

            # checks empty inputs
            for k, v in form.items():
                if v == "":
                    missing.append(k)

            if missing:
                feedback = f"Missing fields for {', '.join(missing)}"
                return render_template("/newproduct.html", user_data=check_user()[0], feedback=feedback)
            else:
                name = request.form['name']
                desc = request.form['description']
                image = request.form['image']
                price = request.form['price']

                url = "https://europe-west2-ad-cainburt.cloudfunctions.net/edit_product_mongoDB?id=" + str(
                    id) + "&name=" + name + "&desc=" + desc + "&img=" + image + "&price=" + str(price)
                response = requests.get(url)
                feedback = response.content
                print(id, name, desc, image, price)

            return redirect('/product/' + str(id))
        else:
            product = "https://europe-west2-ad-cainburt.cloudfunctions.net/display_single_product_mongoDB?id=" + str(id)
            mongo_product = requests.get(product)
            jresponse = mongo_product.text
            data = json.loads(jresponse)
            return render_template('/edit.html', data=data, user_data=check_user()[0])
    else:
        return render_template('/index.html', error_message="You are not a ADMIN!", user_data=check_user()[0])


@app.route('/editorderdetails/<oid>', methods=['GET', 'POST'])
def edit_order_details(oid):
    # edits the order details by getting the order from firestore based on the logged in users id and the order id
    user_id = check_user()[0]['user_id']
    order_id = oid
    order_list = []
    product_list = []
    url = "https://europe-west2-ad-cainburt.cloudfunctions.net/display_one_order_firestore?uid=" + user_id + "&oid=" + order_id
    product = requests.get(url)
    firebase_order = product.text
    fbase_data = json.loads(firebase_order)
    order_list.append({'oid': order_id, 'order': fbase_data})
    print(order_list)
    # get the product info for the ids
    for i in order_list:
        for k, v in list(i['order'].items()):
            if k == "products_id":
                v = json.loads(v)
                for i in v:
                    url = "https://europe-west2-ad-cainburt.cloudfunctions.net/display_single_product_mongoDB?id=" + str(
                        i)
                    mongo_product = requests.get(url)
                    jresponse = mongo_product.text
                    data = json.loads(jresponse)

                    # filters the ids and names and adds them to a list to return to html
                    for p in data:
                        prods = {'id': p['id'], 'name': p['name']}
                        product_list.append(prods)

    # removes duplicates
    result = []
    for i in range(len(product_list)):
        if product_list[i] not in product_list[i + 1:]:
            result.append(product_list[i])

    # when the edit form is submitted, it sends that to the cloud function to update the order based on the order id and user id
    if request.method == "POST":
        user_id = check_user()[0]['user_id']
        order_id = oid
        name = request.form['name']
        email = request.form['email']
        address = request.form['address']
        city = request.form['city']
        county = request.form['county']
        postcode = request.form['zip']

        url = "https://europe-west2-ad-cainburt.cloudfunctions.net/update_order_details_firestore?uid=" + user_id + "&oid=" + order_id + "&name=" + name + "&email=" + email + "&address=" + address + "&city=" + city + "&county=" + county + "&zip=" + postcode
        response = requests.get(url)
        feedback = response.content
        return render_template('/profile.html', user_data=check_user()[0], feedback=feedback)

    return render_template('editorder.html', user_data=check_user()[0], orders=order_list, productlist=result)


if __name__ == '__main__':
    app.run()
