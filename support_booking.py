import json


def write_json(path, list_dict):
    '''
    It will search the file based on the path and
    :param path: given json path
    :param list_dict: dictionary
    Save the of the dictionary in the json path document
    '''
    wrapped_data = {
        "booking_places": list_dict
    }
    with open(path, 'w') as f:
        json.dump(wrapped_data, f, indent=2)
