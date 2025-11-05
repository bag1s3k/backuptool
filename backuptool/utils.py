import os
import stat
from pathlib import Path
from typing import Optional

from backuptool.backup_instance import BackupInstance

def remove_readonly(func, path, _):
    """Callback for shutil.rmtree. If exception PermissionError raise,
    will remove read-only flag and try to call the func again"""
    os.chmod(path, stat.S_IWRITE)
    func(path)

def maximum(instances: list[BackupInstance]) -> BackupInstance:
    """ Find the newest date of the day (based on time)
        :param instances: list of days
        :return: newest date"""
    max_value = instances[0]
    for inst in instances:
        if inst.date_type > max_value.date_type:
            max_value = inst
    return max_value