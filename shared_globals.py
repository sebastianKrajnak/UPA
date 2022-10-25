def json_extract(obj, key):
    # Recursively fetch values from nested JSON.
    vals = list()

    def extract(obj, vals, key):
        # Recursively search for values of key in JSON tree.
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k == key:
                    vals.append(v)
                elif isinstance(v, (dict, list)):
                    extract(v, vals, key)
        elif isinstance(obj, list):
            for item in obj:
                extract(item, vals, key)
        return vals

    values = extract(obj, vals, key)
    return values
