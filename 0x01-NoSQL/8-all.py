#!/usr/bin/env python3
''' List all documents in MongoDB Operations with Python using pymongo'''



def list_all(mongo_collection):
    ''' In a collection, list all documents in MongoDB Operations with Python using pymongo'''

    return [doc for doc in mongo_collection.find()]
