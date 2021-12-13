from google.cloud import firestore
from flask import jsonify

def delete_order(request):

  try:
    # Initialize Firestore DB
    db = firestore.Client()
    user_ref = db.collection('user')

    #get order details
    user_id = request.args.get('uid')
    order_id = request.args.get('oid')

    orders = user_ref.document(user_id).collection('orders').document(order_id).delete()

    return jsonify({"success": True}), 200
  except Exception as e:
    return f"An Error Occurred: {e}"
