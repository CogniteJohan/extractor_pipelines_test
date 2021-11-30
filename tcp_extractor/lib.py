from cognite.client import CogniteClient
from cognite.client.data_classes import DataSet


def json_stich_partial_strings(new_string: str, leftover: str) -> dict:
    start_string = leftover
    main_string = new_string.replace("\r", "")
    new_string_split = main_string.split("\n")
    concatenate_both = [start_string + new_string_split[0]]
    concatenate_both.extend(new_string_split[1:])

    datapoints_list: list = concatenate_both[0:-1]
    new_leftover: str = concatenate_both[-1]

    return {"datapoints_list": datapoints_list, "leftover": new_leftover}


def dicts_to_tuples(list_of_dicts: list) -> list:
    list_of_tuples = []
    for item in list_of_dicts:
        list_of_tuples.append((int(round(item["timestamp"] * 1000, 0)), item["value"]))
    return list_of_tuples


def get_data_set_id(ext_id: str, client: CogniteClient) -> int:
    data_set = client.data_sets.retrieve(external_id=ext_id)

    if not data_set:
        data_set_to_insert = DataSet(
            external_id=ext_id, name="Source Time Series", description="Source Time Series ingested by extractor"
        )

        data_set = client.data_sets.create(data_set_to_insert)

    return data_set.id


# TESTING
if __name__ == "__main__":
    pass
