import argparse
import os
from datetime import datetime
from time import time

from argparse_prompt import PromptParser
from pymongo import MongoClient

from init import (
    MONTHS_PATH,
    MONTHS_URLS,
    create_location_to_train_id_collection,
    download_monthly_updates,
    extract_main_data,
    store_main_data_to_db,
    update_db_by_all_monthly_updates,
)
from search import (
    filter_by_time,
    filter_by_train_activity,
    filter_out_reverse_connections,
    get_all_trains_ids_on_route,
    list_filtered_connections_with_time,
)

# Create MongoDB client running locally on Docker
client = MongoClient("localhost", 27017)
# Create database if it doesn't exist
db = client["timetables"]
# Create collections in a db if they don't exist
collection_name = db["timetables_2022"]
name_to_id_collection = db["name_to_id"]

# String to bool conversion, so the parsing works accordingly
def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ("yes", "true", "t", "y", "1"):
        return True
    elif v.lower() in ("no", "false", "f", "n", "0"):
        return False
    else:
        raise argparse.ArgumentTypeError("Boolean value expected.")


parser = PromptParser(description="UPA 2022 NoSQL")
# Fetches the data from the source, processes them and loads then into db
parser.add_argument(
    "-g",
    "--get_data",
    required=False,
    help="Download data? True/False",
    type=str2bool,
    default=False,
    prompt=True,
)

# Finds a connection between two provided stations on specified date and time
parser.add_argument(
    "-s",
    "--source_station",
    help="Source station",
    required=False,
    type=str,
    prompt=True,
    default="Kladno",
)
parser.add_argument(
    "-a",
    "--arrival_station",
    help="Destination",
    required=False,
    type=str,
    prompt=True,
    default="Praha hl. n.",
)
parser.add_argument(
    "-f",
    "--time_from",
    help="Search from this date and time. Format: YYYY-MM-DD",
    required=False,
    type=str,
    prompt=True,
    default="2022-10-01",
)
parser.add_argument(
    "-t",
    "--time_until",
    help="Search up to this date and time. Format: YYYY-MM-DD",
    required=False,
    type=str,
    prompt=True,
    default="2022-10-05",
)


def validate(date_text):
    try:
        datetime.strptime(date_text, "%Y-%m-%d")
        return True
    except ValueError:
        raise ValueError("Incorrect data format, should be YYYY-MM-DD")


def search_trains(source, destination, time_from, time_until):
    print(source, destination, time_from, time_until)
    all_trains_ids = get_all_trains_ids_on_route(
        name_to_id_collection, source, destination
    )
    find = {"_id": {"$in": all_trains_ids}}
    all_trains = collection_name.find(find)
    routes = filter_out_reverse_connections(all_trains, source, destination)
    routes = filter_by_time(routes, time_from, time_until)
    routes = filter_by_train_activity(routes, source, destination)
    return routes


def main(args):
    # Parsing Arguments
    get_data = args.get_data
    source = args.source_station
    destination = args.arrival_station
    time_from = args.time_from
    time_until = args.time_until

    # Loading into DB, Download and extract if necessary
    if get_data:
        start = time()
        # Download and extract main 2022 xml files from zip
        extract_main_data()
        # Upload main 2022 data from xml to db
        store_main_data_to_db(collection_name)

        # Donwload all monthly updates
        if not os.path.exists(MONTHS_PATH):
            os.mkdir(MONTHS_PATH)
            download_monthly_updates()
        elif len(os.listdir(MONTHS_PATH)) != len(MONTHS_URLS):
            download_monthly_updates()

        # # Update DB with monthly updates ie. cancellations and re-routes
        update_db_by_all_monthly_updates(collection_name)

        create_location_to_train_id_collection(collection_name, name_to_id_collection)
        end = time()
        print(f"Data prepared, elapsed time: {end - start}s")
    else:
        # Data already in DB
        print(f"Data prepared")

    if validate(time_from) and validate(time_until):
        rtime_from = datetime.strptime(time_from, "%Y-%m-%d")
        rtime_until = datetime.strptime(time_until, "%Y-%m-%d")
        trains = search_trains(source, destination, rtime_from, rtime_until)
        list_filtered_connections_with_time(trains)


if __name__ == "__main__":
    args = parser.parse_args()
    main(args)
