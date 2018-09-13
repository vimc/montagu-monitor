from datetime import datetime, timezone


def combine_dictionaries(dicts):
    new_dict = {}
    for d in dicts:
        new_dict.update(d)
    return new_dict


def seconds_elapsed_since(timestamp):
    now = datetime.now(timezone.utc).astimezone()
    return (now - timestamp).total_seconds()
