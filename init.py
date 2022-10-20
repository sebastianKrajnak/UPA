from fileinput import filename
import io
from pymongo import MongoClient
import zipfile, gzip, shutil
import json
import xmltodict
import os
import requests
import bs4
from tqdm import tqdm #status bar for load progress

# CONSTANTS
MAIN_URL = 'https://portal.cisjr.cz/pub/draha/celostatni/szdc/2022/GVD2022.zip'
MONTHS_URLS = [
    'https://portal.cisjr.cz/pub/draha/celostatni/szdc/2022/2021-12',
    'https://portal.cisjr.cz/pub/draha/celostatni/szdc/2022/2022-01',
    'https://portal.cisjr.cz/pub/draha/celostatni/szdc/2022/2022-02',
    'https://portal.cisjr.cz/pub/draha/celostatni/szdc/2022/2022-03',
    'https://portal.cisjr.cz/pub/draha/celostatni/szdc/2022/2022-04',
    'https://portal.cisjr.cz/pub/draha/celostatni/szdc/2022/2022-05',
    'https://portal.cisjr.cz/pub/draha/celostatni/szdc/2022/2022-06',
    'https://portal.cisjr.cz/pub/draha/celostatni/szdc/2022/2022-07',
    'https://portal.cisjr.cz/pub/draha/celostatni/szdc/2022/2022-08',
    'https://portal.cisjr.cz/pub/draha/celostatni/szdc/2022/2022-09',
    'https://portal.cisjr.cz/pub/draha/celostatni/szdc/2022/2022-10'
]



# Create MongoDB client running locally on Docker
client = MongoClient('localhost',27017)
# Create database if it doesn't exist
db = client['timetables']
# Create a collection in a db if it doesn't exist 
collection_name = db["timetables_2022"]

# Download and extract main 2022 xml files from zip
if not os.path.exists('data_main'):
    main_data = requests.get(MAIN_URL)
    with zipfile.ZipFile(io.BytesIO(main_data.content)) as zf:
        for member in tqdm(zf.infolist(), desc = 'Extracting main data '):
            zf.extract(member, 'data_main')
""" 
# Upload main 2022 data from xml to db
for file in tqdm(os.listdir('data_main')):
    path = os.path.join('data_main', file)
    with open(path, encoding='utf-8') as xml_file:
        data_dict = xmltodict.parse(xml_file.read(), encoding='utf-8')
        # Remove unnecessary tags
        del data_dict['CZPTTCISMessage']['@xmlns:xsd']
        del data_dict['CZPTTCISMessage']['@xmlns:xsi']
        json_data = json.dumps(data_dict,ensure_ascii=False)

        collection_name.insert_one(data_dict)

        #print(json_data)

item = collection_name.find_one({'CZPTTCISMessage.CZPTTInformation.CZPTTLocation.Location.PrimaryLocationName' : 'Týnec nad Sázavou'})
print(item)
 """

# Donwload all monthly updates
def downloadMonths():
    for month in tqdm(MONTHS_URLS, desc = 'Extracting monthly updates total: '):
        # Create a subfolder for each month
        month_n = month.split("/")[-1]
        path_month = os.path.join('data_monthly_updates', month_n)
        if not os.path.exists(path_month):
            os.mkdir(path_month)
            # Download all gziped files
            r = requests.get(month)
            data = bs4.BeautifulSoup(r.text, "html.parser")
            
            for l in tqdm(data.find_all('a'), desc = 'Extracting '+ month_n ):
                url = 'https://portal.cisjr.cz' + l["href"]
                # The very first link is a return to previous folder link which breaks the conversion
                if l["href"] == '/pub/draha/celostatni/szdc/2022/':
                    continue
                gzip_file = requests.get(url)
                zip_filename = url.split("/")[-1]
                xml_filename = zip_filename.removesuffix('.zip')
                path_xml = os.path.join(path_month, xml_filename)

                
                if '.xml.zip' in zip_filename:
                    # Unpack gzipped files and extract them to seperate folders as seperate xml files
                    with open('data.xml.zip', 'wb') as f:
                        f.write(gzip_file.content)
                    with gzip.open('data.xml.zip', 'r') as f_in, open(path_xml, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                    with open(path_xml, encoding='utf-8') as xml_file:
                        data_dict = xmltodict.parse(xml_file.read(), encoding='utf-8')
                else:
                    with zipfile.ZipFile(io.BytesIO(gzip_file.content)) as zf:
                        zf.extract(filename, path_xml)
                

if not os.path.exists('data_monthly_updates'):
    os.mkdir('data_monthly_updates')
    downloadMonths()
elif os.path.exists('data_monthly_updates') and os.listdir('data_monthly_updates') != len(MONTHS_URLS):
    downloadMonths()