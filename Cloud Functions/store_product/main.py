import pymongo
from pymongo import MongoClient
from bson.json_util import dumps
import os
import requests
import json

def store_product(request):
    client=MongoClient("mongodb+srv://cain:Password12@advanceddevelopment.tz0f9.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")

    db = client.ADAssignment 
    passed_name = request.args.get("name")
    passed_desc = request.args.get("desc")
    passed_img = request.args.get("img")
    passed_price = request.args.get("price")

    
    json_data = {"id": db.products.count_documents({})+1, "description": passed_desc, "image": passed_img, "name":passed_name, "price":int(passed_price)}
    
    db.products.insert_one(json_data)
  
    return "Product Data submitted!"