from pathlib import Path

from backuptool.decorator import check_kwargs

# Allowed path keyword arguments
PATH_KEYS = {
    "src",
    "dst",
}

# Allowed file keyword arguments
FILE_KEYS = {
    "ignore",
    "name_format",
    "archive_type",
    "keep_name",
    "backups_amount"
}

# Every possible keyword argument
EVERY_KEY = {
    *PATH_KEYS,
    *FILE_KEYS
}


@check_kwargs(EVERY_KEY)
def exclude_keys(key_set: set, exclude: set = None) -> set:
    """ Exclude specific keys from the given set
        :param key_set: original set of keys
        :param exclude: set with keys to exclude
        :return: new set with exclude keys removed
        """
    result = set()
    result |= key_set
    result -= exclude
    return result

# Keyword arguments for run func
RUN_KEYS = {
    *PATH_KEYS,
    *exclude_keys(FILE_KEYS, {"backups_amount"})
}

# Keyword arguments for clean func
CLEAN_KEYS = {
    *exclude_keys(FILE_KEYS, {"src"}),
    *exclude_keys(FILE_KEYS, {"ignore", "keep_name", "archive_type"})
}

# Default config key-value pairs
DEFAULT_CONFIG = {
    "src": Path.cwd(),
    "dst": Path.cwd(),
    "ignore": [],
    "name_format": "%Y%m%d_%H%M%S",
    "archive_type": "zip",
    "keep_name": False,
    "backups_amount": 0
}