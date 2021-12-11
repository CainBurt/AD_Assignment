import pymongo
from pymongo import MongoClient
from bson.json_util import dumps
import os
import requests
import json

def delete_single_product(request):
    client=MongoClient("mongodb+srv://cain:Password12@advanceddevelopment.tz0f9.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")

    # connect to the db
    passed_id = request.args.get('id')
    db = client.ADAssignment 
    myquery = {"id":int(passed_id)}
    db.products.delete_one(myquery)
    return "product deleted!"

