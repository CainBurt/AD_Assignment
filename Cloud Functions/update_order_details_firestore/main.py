from google.cloud import firestore

def update_order(request):

  try:
    # Initialize Firestore DB
    db = firestore.Client()

    #get order details
    user_ref = db.collection('user')
    user_id = request.args.get('uid')
    order_id = request.args.get('oid')

    user_name = request.args.get('name')
    user_email = request.args.get('email')

    user_address = request.args.get('address')
    user_city = request.args.get('city')
    user_county = request.args.get('county')
    user_postcode = request.args.get('zip')

    new_details = {'name': user_name, 'email': user_email, 'address':user_address, 'city': user_city, 'county':user_county, 'postcode':user_postcode}
    user_ref.document(user_id).collection('orders').document(order_id).update(new_details)

    return f"success"
  except Exception as e:
    return f"An Error Occurred: {e}"
