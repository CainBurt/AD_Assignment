import pymongo
from pymongo import MongoClient
from bson.json_util import dumps
import os
import requests
import json

def get_product_list(request):
  client=MongoClient("mongodb+srv://cain:Password12@advanceddevelopment.tz0f9.mongodb.net/ADAssignment?retryWrites=true&w=majority")

  db=client.ADAssignment

  myCursor=db.products.find({})

  list_cur=list(myCursor)
  print(list_cur)

  json_data = dumps(list_cur)

  return json_data
