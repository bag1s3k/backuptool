import shutil
import stat
import os
from collections import defaultdict
from pathlib import Path
from datetime import datetime
from os import PathLike
from typing import Literal, Optional

# ========= GLOBAL DEFAULT VALUES =========== #
_name_format: str = "%Y%m%d_%H%M%S"
_dest: Path = Path.cwd()
_archive_type: Literal["zip", "tar", "gztar", "bztar", "xztar", "noarchive"] = "zip"


# ============= HELP FUNCS =============== #
def remove_readonly(func, path, _):
    """Callback for shutil.rmtree. If exception PermissionError raise,
    will remove read-only flag and try to call the func again"""
    os.chmod(path, stat.S_IWRITE)
    func(path)

class BackupInstance:
    def __init__(self, file: str, date_len: int, name_format: str):
        self.file = file
        self.suffix = self.get_suffix(date_len)
        self.date_type = datetime.strptime(file[:date_len], name_format)

    def get_suffix(self, date_len):
        """ Resolve if backup has suffix
            :param date_len: length of the file name
            :return: If folder return None otherwise suffix"""
        if "." not in self.file:
            return None
        else:
            return self.file[date_len+1:]

def maximum(instances: list[BackupInstance]) -> BackupInstance:
    """ Find the newest date of the day (based on time)
        :param instances: list of days
        :return: newest date"""
    max_value = instances[0]
    for inst in instances:
        if inst.date_type > max_value.date_type:
            max_value = inst
    return max_value

def run_backup(
        source: str | Path = "", # TODO: find project root
        dest: Optional[str | Path] = None,
        ignore: Optional[list[str]] = None,
        name_format: Optional[str] = None, # strftime format string
        archive_type: Optional[Literal["zip", "tar", "gztar", "bztar", "xztar", "noarchive"]] = None,
) -> str:
    """ Create backup of your project
        :param source: Absolute path to your project or project root folder name
        :param dest: target folder for your backups
        :param ignore: list of your files or folders you don't want to have in backup
        :param name_format: strftime format string, default is ISO format
        :param archive_type: Which type of archive you want, if you want to just copy your
        project without using archive use 'noarchive'
        :return Path of your created backup"""
    global _dest, _name_format, _archive_type

    # Fallback values
    dest = Path(dest or _dest)
    name_format = name_format or _name_format
    if archive_type is None:  archive_type = _archive_type
    ignore = ignore or []

    # Update fallback values
    _dest = dest
    _name_format = name_format
    _archive_type = archive_type

    now = datetime.now()
    source = Path(source)
    name_format = now.strftime(name_format)
    dest = dest / name_format

    def ignore_files(_, files):
        return [f for f in files if f in ignore]

    shutil.copytree(source, dest, ignore=ignore_files, dirs_exist_ok=True)

    if archive_type != "noarchive":
        shutil.make_archive(str(dest), archive_type, dest)
        shutil.rmtree(dest, onerror=remove_readonly)

    return str(dest)

def clean_up(
        dest: Optional[str | Path] = None,
        backups_amounts: int = 0,
        name_format: Optional[str] = None, # TODO: auto recognization name format
) -> dict:
    """ Clean up backup folder
        :param dest: target folder of your backups
        :param backups_amounts: how many backups you want to leave
        :param name_format: strftime format string, default is your last used
        :return: dict of: folder content, isbackup, removed files

        if you have never used run_backup before, default is ISO format
        if you want to just copy your project without using archive, use 'None' default is current path"""
    # Fallback values
    dest = Path(dest or _dest)
    name_format = name_format or _name_format

    content = os.listdir(dest)

    isbackup = []
    date_len = len(datetime.now().strftime(name_format))
    for file in content:
        try:
            datetime.strptime(file[:date_len], name_format)
            isbackup.append(file)
        except ValueError:
            continue

    # Create date data structure dict {date: suffix}
    date_content: list[BackupInstance] = []
    for file in isbackup:
        date_content.append(BackupInstance(file, date_len, name_format))

    # Split by just by date (not by time)
    groups = defaultdict(list[BackupInstance])
    for backup in date_content:
        groups[backup.date_type.date()].append(backup)

    # no_duplicity = [max(v, key=lambda f) for v in groups.values()] # Select the newest date of each day
    no_duplicity = []
    for backups in groups.values():
        no_duplicity.append(maximum(backups))

    final = sorted(no_duplicity, key= lambda b: b.date_type)[-backups_amounts:] # take only given amount
    to_remove = [t for t in date_content if t not in final]

    # Delete backups
    for item in to_remove:
        path = dest / item.file
        if item.suffix:
            os.remove(path)
        else:
            shutil.rmtree(path, onerror=remove_readonly)

    return {
        "content": content,
        "isbackup": isbackup,
        "removed": [f.file for f in to_remove]
    }