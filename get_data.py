import os
import sys
import json

from dotenv import load_dotenv
load_dotenv()
MONGO_DB_URL=os.getenv("MONGO_DB_URL")


import certifi
ca = certifi.where()

import pandas as pd
import numpy as np
import pymongo
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logger.logger import logging

class NetworkDataExtract():
    def __init__(self):
        try:
            pass
        except Exception as e:
            raise NetworkSecurityException(e,sys)
    
    def csv_to_json_converter(self,files_path):
        try:
            data = pd.read_csv(files_path)
            data.reset_index(drop=True,inplace=True)
            records = list(json.loads(data.T.to_json()).values())
            return records
        except Exception as e:
            raise NetworkSecurityException(e,sys)
    
    def pushing_data_to_mongoDB(self,records,database,collection):
        try:
            self.database = database
            self.collection = collection
            self.records = records

            self.mongo_client = pymongo.MongoClient(MONGO_DB_URL)
            self.database = self.mongo_client[self.database]
            self.collection = self.database[self.collection]
            self.collection.insert_many(self.records)

            return len(self.records)
        
        except Exception as e:
            raise NetworkSecurityException(e,sys)
        
if __name__ == "__main__":
    File_path = r'D:\Data science\MLOps(krish naik)\Network security\Data\NetworkData.csv'
    Database = 'NetworkSecurity'
    Collection = 'NetworkData'
    networkobj = NetworkDataExtract()
    records = networkobj.csv_to_json_converter(File_path)
    no_of_records = networkobj.pushing_data_to_mongoDB(records,Database,Collection)
    print(f'{no_of_records} records pushed to mongoDB')