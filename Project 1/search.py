from datetime import datetime
from typing import Dict, Iterable, List

from pandas import date_range

from shared_globals import json_extract


def reformat_time(time_string):
    formatted = time_string[:-14]
    return formatted


def filter_out_reverse_connections(connections_list, origin, destination):
    filtered_connections_list = []
    for train in connections_list:
        bool_flag_1 = False
        for location in train["CZPTTCISMessage"]["CZPTTInformation"]["CZPTTLocation"]:
            loc_name = location["Location"]["PrimaryLocationName"]
            if loc_name == origin:
                bool_flag_1 = True
            if bool_flag_1 == True and loc_name == destination:
                filtered_connections_list.append(train)

    return filtered_connections_list


def list_filtered_connections_with_time(filtered_connections_list):
    for i, train in enumerate(filtered_connections_list, start=1):
        print(f"\nTrain {i}:")
        for location in train["CZPTTCISMessage"]["CZPTTInformation"]["CZPTTLocation"]:
            stop = json_extract(location, "PrimaryLocationName")
            timing_qualifier = json_extract(location, "@TimingQualifierCode")
            spaces = " " * (30 - len(stop[0]))
            if len(timing_qualifier) == 2:
                time_arrival = ""
                time_departure = ""
                for timing in timing_qualifier:
                    if timing == "ALA":
                        time_arrival = json_extract(location, "Time")[0]
                    elif timing == "ALD":
                        time_departure = json_extract(location, "Time")[1]
                print(
                    f"{stop[0]}{spaces}",
                    f"Příjezd: {reformat_time(time_arrival)}\t",
                    f"Odjezd: {reformat_time(time_departure)}",
                )
            elif len(timing_qualifier) == 1:
                if timing_qualifier[0] == "ALA":
                    time_arrival = json_extract(location, "Time")[0]
                    print(f"{stop[0]}{spaces}\tPříjezd: {reformat_time(time_arrival)}")
                elif timing_qualifier[0] == "ALD":
                    time_departure = json_extract(location, "Time")[0]
                    print(f"{stop[0]}{spaces}\tOdjezd: {reformat_time(time_departure)}")


def get_all_trains_ids_on_route(
    name_to_id_collection, station_from: str, station_to: str
) -> List[Dict]:
    try:
        all_trains_from = name_to_id_collection.find_one(
            {"PrimaryLocationName": station_from}
        )["TrainIds"]
        all_trains_to = name_to_id_collection.find_one(
            {"PrimaryLocationName": station_to}
        )["TrainIds"]
    except Exception:
        return []
    return list(set(all_trains_from).intersection(set(all_trains_to)))


def get_dates_by_bitmap(
    time_from: datetime, time_to: datetime, bitmap: str
) -> List[datetime]:
    dates = date_range(time_from, time_to, freq="d")
    bitmap = [True if char == "1" else False for char in bitmap]
    return dates[bitmap]


def filter_by_time(
    train_routes: Iterable,
    time_from: datetime,
    time_to: datetime,
) -> List[Dict]:
    filtered_routes = []
    for route in train_routes:
        bitmap = route["CZPTTCISMessage"]["CZPTTInformation"]["PlannedCalendar"][
            "BitmapDays"
        ]
        route_time_from = route["CZPTTCISMessage"]["CZPTTInformation"][
            "PlannedCalendar"
        ]["ValidityPeriod"]["StartDateTime"].split("T")[0]
        route_time_from = datetime.strptime(route_time_from, "%Y-%m-%d")
        route_time_to = route["CZPTTCISMessage"]["CZPTTInformation"]["PlannedCalendar"][
            "ValidityPeriod"
        ]["EndDateTime"].split("T")[0]
        route_time_to = datetime.strptime(route_time_to, "%Y-%m-%d")

        route_valid_dates = get_dates_by_bitmap(route_time_from, route_time_to, bitmap)
        wanted_dates = date_range(time_from, time_to, freq="d")
        matching_dates = set(route_valid_dates).intersection(set(wanted_dates))
        if matching_dates:
            filtered_routes.append(route)

    return filtered_routes


def filter_by_train_activity(
    train_routes: Iterable,
    station_from: str,
    station_to: str,
) -> List[Dict]:
    filtered_routes = []
    for route in train_routes:
        checked_one_station = False
        locations = json_extract(route, "CZPTTLocation")
        for location in locations[0]:
            loc_name = location["Location"]["PrimaryLocationName"]
            if loc_name == station_from or loc_name == station_to:
                does_stop = False
                try:
                    activities = location["TrainActivity"]
                    if not isinstance(activities, list):
                        activities = [activities]
                    for activity in activities:
                        if "0001" in activity.values():
                            does_stop = True
                except KeyError:
                    break
                if checked_one_station and does_stop:
                    filtered_routes.append(route)
                    break
                elif does_stop:
                    checked_one_station = True
                else:
                    break

    return filtered_routes
