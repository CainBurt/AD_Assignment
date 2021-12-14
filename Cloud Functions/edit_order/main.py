from google.cloud import firestore
from flask import jsonify

def get_order(request):

  try:
    # Initialize Firestore DB
    db = firestore.Client()

    #get order details
    user_ref = db.collection('user')
    user_id = request.args.get('uid')
    order_id = request.args.get('oid')

    order = user_ref.document(user_id).collection('orders').document(order_id).get()

    return jsonify(order.to_dict())
  except Exception as e:
    return f"An Error Occurred: {e}"
