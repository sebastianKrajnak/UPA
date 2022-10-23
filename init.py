import gzip
import io
import os
import shutil
import zipfile

import bs4
import requests
import xmltodict
from pymongo import MongoClient
from tqdm import tqdm

from search import get_all_trains_on_route  # status bar for load progress

# CONSTANTS
MAIN_URL = "https://portal.cisjr.cz/pub/draha/celostatni/szdc/2022/GVD2022.zip"
MONTHS_URLS = [
    "https://portal.cisjr.cz/pub/draha/celostatni/szdc/2022/2021-12",
    "https://portal.cisjr.cz/pub/draha/celostatni/szdc/2022/2022-01",
    "https://portal.cisjr.cz/pub/draha/celostatni/szdc/2022/2022-02",
    "https://portal.cisjr.cz/pub/draha/celostatni/szdc/2022/2022-03",
    "https://portal.cisjr.cz/pub/draha/celostatni/szdc/2022/2022-04",
    "https://portal.cisjr.cz/pub/draha/celostatni/szdc/2022/2022-05",
    "https://portal.cisjr.cz/pub/draha/celostatni/szdc/2022/2022-06",
    "https://portal.cisjr.cz/pub/draha/celostatni/szdc/2022/2022-07",
    "https://portal.cisjr.cz/pub/draha/celostatni/szdc/2022/2022-08",
    "https://portal.cisjr.cz/pub/draha/celostatni/szdc/2022/2022-09",
    "https://portal.cisjr.cz/pub/draha/celostatni/szdc/2022/2022-10",
]
MONTHS_PATH = "data_monthly_updates"
MAIN_PATH = "data_main"

# Create MongoDB client running locally on Docker
client = MongoClient("localhost", 27017)
# Create database if it doesn't exist
db = client["timetables"]
# Create collections in a db if they don't exist
collection_name = db["timetables_2022"]
name_to_id_collection = db["name_to_id"]


def download_monthly_updates():
    for month in tqdm(MONTHS_URLS, desc="Extracting monthly updates total: "):
        # Create a subfolder for each month
        month_n = month.split("/")[-1]
        path_month = os.path.join(MONTHS_PATH, month_n)
        if os.path.exists(path_month):
            continue

        os.mkdir(path_month)
        # Download all gziped files
        r = requests.get(month)
        data = bs4.BeautifulSoup(r.text, "html.parser")

        for l in tqdm(data.find_all("a"), desc="Extracting " + month_n):
            url = "https://portal.cisjr.cz" + l["href"]
            # The very first link is a return to previous folder link which breaks the conversion
            if l["href"] == "/pub/draha/celostatni/szdc/2022/":
                continue
            extract_month(path_month, url)


def extract_month(path_month, url):
    gzip_file = requests.get(url)
    zip_filename = url.split("/")[-1]
    xml_filename = zip_filename.removesuffix(".zip")
    path_xml = os.path.join(path_month, xml_filename)

    if ".xml.zip" in zip_filename:
        try:
            # Unpack gzipped files and extract them to seperate folders as seperate xml files
            with open("data.xml.zip", "wb") as f:
                f.write(gzip_file.content)
            with gzip.open("data.xml.zip", "r") as f_in, open(path_xml, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)
        except gzip.BadGzipFile:
            with zipfile.ZipFile(io.BytesIO(gzip_file.content)) as zf:
                zf.extractall(path_month)
    else:
        with zipfile.ZipFile(io.BytesIO(gzip_file.content)) as zf:
            zf.extractall(path_month)


def extract_main_data():
    if os.path.exists(MAIN_PATH):
        return

    main_data = requests.get(MAIN_URL)
    with zipfile.ZipFile(io.BytesIO(main_data.content)) as zf:
        for member in tqdm(zf.infolist(), desc="Extracting main data "):
            zf.extract(member, MAIN_PATH)


def store_main_data_to_db():
    for file in tqdm(os.listdir(MAIN_PATH), desc="Creating database: "):
        path = os.path.join(MAIN_PATH, file)
        with open(path, encoding="utf-8") as xml_file:
            data_dict = xmltodict.parse(xml_file.read(), encoding="utf-8")
            # Remove unnecessary tags
            del data_dict["CZPTTCISMessage"]["@xmlns:xsd"]
            del data_dict["CZPTTCISMessage"]["@xmlns:xsi"]

            item = collection_name.insert_one(data_dict)
            item_locations = json_extract(data_dict, "PrimaryLocationName")
            item_locations_in_db = name_to_id_collection.find(
                {"PrimaryLocationName": {"$in": item_locations}}
            )
            item_locations_in_db = [
                item["PrimaryLocationName"] for item in item_locations_in_db
            ]
            item_locations_to_add = [
                item for item in item_locations if item not in item_locations_in_db
            ]
            insert_locations_train_id(item_locations_to_add, item.inserted_id)
            append_locations_train_id(item_locations_in_db, item.inserted_id)

    number_of_documents = name_to_id_collection.count_documents({})
    print(f"Number of documents: {number_of_documents}")
    # items = name_to_id_collection.find({"train_ids.1": {"$exists": True}})
    # print(len(items))


def json_extract(obj, key):
    # Recursively fetch values from nested JSON.
    vals = set()

    def extract(obj, vals, key):
        # Recursively search for values of key in JSON tree.
        if isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(v, (dict, list)):
                    extract(v, vals, key)
                elif k == key:
                    vals.add(v)
        elif isinstance(obj, list):
            for item in obj:
                extract(item, vals, key)
        return vals

    values = extract(obj, vals, key)
    return list(values)


def append_locations_train_id(location_names, train_id):
    if location_names:
        name_to_id_collection.update_many(
            {"PrimaryLocationName": {"$in": location_names}},
            {"$push": {"TrainIds": train_id}},
        )


def insert_locations_train_id(location_names, train_id):
    if location_names:
        name_to_id_collection.insert_many(
            [
                {
                    "PrimaryLocationName": location_name,
                    "TrainIds": [train_id],
                }
                for location_name in location_names
            ]
        )


def truncate_db():
    collection_name.delete_many({})
    name_to_id_collection.delete_many({})


def update_db_by_all_monthly_updates():
    for month_dir in os.listdir(MONTHS_PATH):
        month_path = os.path.join(MONTHS_PATH, month_dir)
        update_for_month(month_dir, month_path)


def update_for_month(month_dir, month_path):
    for file in tqdm(
        os.listdir(month_path), desc=f"Updating database according to {month_dir}: "
    ):
        file_path = os.path.join(month_path, file)
        with open(file_path, encoding="utf-8") as xml_file:
            data_dict = xmltodict.parse(xml_file.read(), encoding="utf-8")
            if "cancel" in file_path:
                del data_dict["CZCanceledPTTMessage"]["@xmlns:xsd"]
                del data_dict["CZCanceledPTTMessage"]["@xmlns:xsi"]
                core_identifier = data_dict["CZCanceledPTTMessage"][
                    "PlannedTransportIdentifiers"
                ][1]["Core"]
            else:
                del data_dict["CZPTTCISMessage"]["@xmlns:xsd"]
                del data_dict["CZPTTCISMessage"]["@xmlns:xsi"]
                core_identifier = data_dict["CZPTTCISMessage"]["Identifiers"][
                    "PlannedTransportIdentifiers"
                ][1]["Core"]
        # print(core_identifier)
        # TODO mozna staci predelat na update_one, find_and_update_one vraci navic puvodni nezmeneny dokument
        collection_name.find_one_and_update(
            {
                "CZPTTCISMessage.Identifiers.PlannedTransportIdentifiers.Core": core_identifier,
                "CZPTTCISMessage.Identifiers.PlannedTransportIdentifiers.ObjectType": "TR",
            },
            {"$set": data_dict},
        )


def print_all_train_routes(loc_from, loc_to):
    find = {"_id": {"$in": all_trains_ids}}
    all_trains = collection_name.find(find)
    all_trains_count = collection_name.count_documents(find)
    print(f"All trains: ")
    for i, train in enumerate(all_trains, start=1):
        print(f"Train {i}:")
        for location in train["CZPTTCISMessage"]["CZPTTInformation"]["CZPTTLocation"]:
            print(location["Location"]["PrimaryLocationName"])
        print()
    print(f"Num of all trains from {loc_from} to {loc_to}: {all_trains_count}")


if __name__ == "__main__":
    # Download and extract main 2022 xml files from zip
    extract_main_data()
    # Upload main 2022 data from xml to db
    # store_main_data_to_db()

    # Donwload all monthly updates
    if not os.path.exists(MONTHS_PATH):
        os.mkdir(MONTHS_PATH)
        download_monthly_updates()
    elif len(os.listdir(MONTHS_PATH)) != len(MONTHS_URLS):
        download_monthly_updates()

    # Update DB with monthly updates ie. cancellations and re-routes
    # update_db_by_all_monthly_updates()
    loc_from = "Vyškov na Moravě"
    loc_to = "Brno hl. n."

    all_trains_ids = get_all_trains_on_route(name_to_id_collection, loc_from, loc_to)
    print_all_train_routes(loc_from, loc_to)

    # truncate_db()
