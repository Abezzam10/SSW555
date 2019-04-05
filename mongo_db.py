""" Mongo DB wrapper function"""
from pymongo import MongoClient

class MongoDB(object):
    """ Encapsulation of some basic daily methods """
    
    __instance = None
    DATABASE = "gedcom"

    def __new__(cls, *args, **kwargs):  
        """ Singleton: generate once
            Feel free to use MongoDB() wherever you like 
            [ e.g. mongo_instance = MongoDB() ]
        """
        if cls.__instance is None:
            cls.__instance = super(MongoDB, cls).__new__(cls, *args, **kwargs)
        return cls.__instance

    def __init__(self):
        self.client = MongoClient('mongodb://admin:mongopassword@mongo.jp.gitel.online:27017')

    def __del__(self):
        """ it will finally close the connection at the end of the project"""
        self.client.close()

    def delete_database(self):
        """ wipe out the gedcom database """
        self.client.drop_database(self.DATABASE)

    def drop_collection(self, collection):
        """ drop the whole documents from the specific collection """
        self.client[self.DATABASE].drop_collection(collection)
    
    def get_collection(self, collection):
        """ return a specific collection """
        return self.client[self.DATABASE][collection]
