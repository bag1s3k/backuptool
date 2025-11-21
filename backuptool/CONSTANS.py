from typing import Literal
from pathlib import Path

from backuptool.decorator import check_params

# Allowed path keyword arguments
PATH_KEYS = {
    "src": str | Path,
    "dst": str | Path
}

# Allowed file keyword arguments
FILE_KEYS = {
    "ignore": list[str],
    "name_format": str,
    "archive_type": Literal['zip', 'tar', 'gztar', 'bztar', 'xztar', 'noarchive'],
    "keep_name": bool | str, # TODO: str, in future there'll be option to create backup with own name
    "backups_amount": int
}

# Every possible keyword argument
EVERY_KEY = {
    **PATH_KEYS,
    **FILE_KEYS
}


@check_params(EVERY_KEY)
def exclude_keys(key_set: dict, exclude: set = None) -> dict:
    """ Exclude specific keys from the given set
        :param key_set: original set of keys
        :param exclude: set with keys to exclude
        :return: new set with exclude keys removed
        """
    if not exclude:
        return {}
    return {k: v for k,v in key_set.items() if k not in exclude}

# Keyword arguments for run func
RUN_KEYS = {
    **PATH_KEYS,
    **exclude_keys(FILE_KEYS, {"backups_amount"}) # TODO: exclude key
}

# Keyword arguments for clean func
CLEAN_KEYS = {
    **exclude_keys(FILE_KEYS, {"src"}),
    **exclude_keys(FILE_KEYS, {"ignore", "keep_name", "archive_type"})
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