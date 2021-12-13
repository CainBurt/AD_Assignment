from google.cloud import firestore
# from bson.json_util import dumps
from flask import jsonify

def get_orders(request):

  try:
    # Initialize Firestore DB
    db = firestore.Client()

    #get order details
    user_ref = db.collection('user')
    user_id = request.args.get('uid')

    orders = user_ref.document(user_id).collection('orders').stream()
    order_list = []
    for u_order in orders:
      order_list.append({'oid': u_order.id, 'order': u_order.to_dict()})

    # json_data = dumps(order_list)

    return jsonify(order_list)
  except Exception as e:
    return f"An Error Occurred: {e}"