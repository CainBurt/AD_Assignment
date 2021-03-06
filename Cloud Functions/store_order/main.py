from google.cloud import firestore

def store_order(request):

  try:
    # Initialize Firestore DB
    db = firestore.Client()

    #get order details
    user_ref = db.collection('user')
    user_id = request.args.get('uid')
    user_name = request.args.get('name')
    user_email = request.args.get('email')
    user_address = request.args.get('address')
    user_city = request.args.get('city')
    user_county = request.args.get('county')
    user_postcode = request.args.get('zip')
    order_status = "Processing"

    user_cart = request.args.get('cart')

    user_order = {'name': user_name, 'email': user_email, 'address':user_address, 'city': user_city, 'county':user_county, 'postcode':user_postcode, 'products_id': user_cart, 'status': order_status}
    user_ref.document(user_id).collection('orders').add(user_order)

    return f"success"
  except Exception as e:
    return f"An Error Occurred: {e}"
