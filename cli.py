import argparse
from argparse_prompt import PromptParser
import search
from time import time
import init
import os
import datetime


# String to bool conversion, so the parsing works accordingly
def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


parser = PromptParser(description='UPA 2022 NoSQL')
# Fetches the data from the source, processes them and loads then into db
parser.add_argument("-g", "--get_data", required=False, help="Download data? True/False", type=str2bool, default=False,
                    prompt=True)

# Finds a connection between two provided stations on specified date and time
parser.add_argument("-s", "--source_station", help="Source station", required=False, type=str, prompt=True)
parser.add_argument("-a", "--arrival_station", help="Destination", required=False, type=str, prompt=True)
parser.add_argument("-f", "--time_from", help="Search from this date and time. Format: YYYY-MM-DD", required=False,
                    type=str,
                    prompt=True)
parser.add_argument("-t", "--time_until", help="Search up to this date and time. Format: YYYY-MM-DD", required=False,
                    type=str,
                    prompt=True)


def validate(date_text):
    try:
        datetime.datetime.strptime(date_text, '%Y-%m-%d')
        return True
    except ValueError:
        raise ValueError("Incorrect data format, should be YYYY-MM-DD")


def reformat_date(date_validated):
    reformatted_date = date_validated + "T00:00:00"
    return reformatted_date


def search_dummy(source, destination, time_from, time_until):
    print(source, destination, time_from, time_until)
    return 0


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
        init.extract_main_data()
        # Upload main 2022 data from xml to db
        init.store_main_data_to_db()

        # Donwload all monthly updates
        if not os.path.exists(init.MONTHS_PATH):
            os.mkdir(init.MONTHS_PATH)
            init.download_monthly_updates()
        elif len(os.listdir(init.MONTHS_PATH)) != len(init.MONTHS_URLS):
            init.download_monthly_updates()

        # # Update DB with monthly updates ie. cancellations and re-routes
        init.update_db_by_all_monthly_updates()
        end = time()
        print(f"Data prepared, elapsed time: {end - start}s")

        if validate(time_from) and validate(time_until):
            rtime_from = reformat_date(time_from)
            rtime_until = reformat_date(time_until)
            # TODO replace dummy with actual search
            search_dummy(source, destination, rtime_from, rtime_until)

    # Data already in DB
    else:
        print(f"Data prepared")

        if validate(time_from) and validate(time_until):
            # TODO replace dummy with actual search
            rtime_from = reformat_date(time_from)
            rtime_until = reformat_date(time_until)
            # TODO replace dummy with actual search
            search_dummy(source, destination, rtime_from, rtime_until)


if __name__ == '__main__':
    args = parser.parse_args()
    main(args)
