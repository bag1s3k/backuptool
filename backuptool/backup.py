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


def run_backup(
        source: str | PathLike[str]= "", # TODO: find project root
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

def remove_readonly(func, path, _):
    """Callback for shutil.rmtree. If exception PermissionError raise,
    will remove read-only flag and try to call the func again"""
    os.chmod(path, stat.S_IWRITE)
    func(path)

def clean_up(
        dest: Optional[str | Path] = None,
        backups_amounts: int = 0,
        name_format: Optional[str] = None,
        archive_type: Optional[Literal["zip", "tar", "gztar", "bztar", "xztar", "noarchive"]] = None,

) -> list:
    """ Clean up backup folder
        :param dest: target folder of your backups
        :param backups_amounts: how many backups you want to leave
        :param name_format: strftime format string, default is your last used
        if you have never used run_backup before, default is ISO format
        :param archive_type: Which type of archive you want,
        if you want to just copy your project without using archive use 'None' default is current path
    """
    dest = Path(dest or _dest)
    name_format = name_format or _name_format
    archive_type = archive_type or _archive_type

    content = os.listdir(dest)
    date_content = [datetime.strptime(t[:len(datetime.now().strftime(name_format))], name_format) for t in content] # select only part with date not e.g. .zip

    groups = defaultdict(list)

    for date in date_content:
        groups[date.date()].append(date)

    no_duplicity = [max(v) for v in groups.values()]
    final = no_duplicity[-backups_amounts:]
    to_remove = [t for t in date_content if t not in final]

    for item in to_remove:
        if archive_type == "noarchive":
            str_archive_type = ""
        else:
            str_archive_type = f".{archive_type}"
        path = dest / f"{item.strftime(name_format)}{str_archive_type}"
        shutil.rmtree(path, onerror=remove_readonly)

    return [
        content,
        [f"{t.strftime(name_format)}.{archive_type}" for t in to_remove]
    ]