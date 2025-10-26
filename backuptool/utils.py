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

def find_project_root(target_folder: str | Path) -> Optional[Path]:
    """ Find project root folder (default is current working directory
        :param target_folder: name of project root folder
        :return: project root path"""
    target_folder = Path(target_folder).name
    current = Path(__file__).resolve().parent  # start from current dir

    for parent in [current, *current.parents]:
        candidate = parent / target_folder
        if candidate.exists() and candidate.is_dir():
            return candidate
    return Path().cwd()