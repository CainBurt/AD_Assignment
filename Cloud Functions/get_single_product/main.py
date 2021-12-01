import pymongo
from pymongo import MongoClient
from bson.json_util import dumps
import os
import requests
import json

def get_single_product(request):
    client=MongoClient("mongodb+srv://cain:Password12@advanceddevelopment.tz0f9.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")

    # connect to the db
    passed_id = request.args.get('id')
    db = client.ADAssignment 
    myCursor = db.products.find({"id": {"$eq": int(passed_id)}})
    list_cur = list(myCursor)
    print(list_cur)
    json_data = dumps(list_cur)
    return json_data