from typing import Any, List


def get_all_trains_on_route(
    name_to_id_collection, station_from: str, station_to: str
) -> List[Any]:
    all_trains_from = name_to_id_collection.find_one(
        {"PrimaryLocationName": station_from}
    )["TrainIds"]
    all_trains_to = name_to_id_collection.find_one({"PrimaryLocationName": station_to})[
        "TrainIds"
    ]
    return list(set(all_trains_from).intersection(set(all_trains_to)))
