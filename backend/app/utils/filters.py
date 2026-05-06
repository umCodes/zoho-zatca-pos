def filter_fields(data, fields_to_keep):
    return {k: v for k, v in data.items() if k in fields_to_keep}


def filter_list_fields(data, fields_to_keep):
    return [filter_fields(item, fields_to_keep) for item in data]