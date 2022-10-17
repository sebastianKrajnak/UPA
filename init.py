from pymongo import MongoClient
import zipfile
import json
import xmltodict
import os

from tqdm import tqdm #status bar for load progress

# Create MongoDB client running locally on Docker
client = MongoClient('localhost',27017)
# Create database if it doesn't exist
db = client['timetables']
# Create a collection in a db if it doesn't exist 
collection_name = db["timetables_2022"]

# Extract xml files from zip
if not os.path.exists('data'):
    with zipfile.ZipFile('GVD2022.zip', 'r') as zf:
        zf.extractall('data')

# Upload each xml file to db
for file in tqdm(os.listdir('data')):
    path = os.path.join('data', file)
    with open(path, encoding='utf-8') as xml_file:
        data_dict = xmltodict.parse(xml_file.read(), encoding='utf-8')
        del data_dict['CZPTTCISMessage']['@xmlns:xsd']
        del data_dict['CZPTTCISMessage']['@xmlns:xsi']
        json_data = json.dumps(data_dict,ensure_ascii=False)

        collection_name.insert_one(data_dict)

        #print(json_data)