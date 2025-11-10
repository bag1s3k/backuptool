from pathlib import Path

DEFAULT_CONFIG = {
    "src": Path.cwd(),
    "dst": Path.cwd(),
    "ignore": [],
    "name_format": "%Y%m%d_%H%M%S",
    "archive_type": "zip",
    "keep_name": False,
    "backups_amount": 0
}