import shutil
import stat
import os

from collections import defaultdict

from pathlib import Path
from datetime import datetime
from os import PathLike
from typing import Literal

_format: str = "%Y%m%d_%H%M%S"
_dest: str | PathLike[str] = Path.cwd()
_archive_type: Literal["zip", "tar", "gztar", "bztar", "xztar"] | None = "zip"

class BackupClass:
    

def run_backup(
        source: str | PathLike[str]= "", # TODO: find project root
        dest: str | PathLike[str] = _dest,
        ignore: list | None = None,
        name_format: str = _format, # strftime format string
        archive_type: Literal["zip", "tar", "gztar", "bztar", "xztar"] | None = _archive_type,
) -> str:
    """ Create backup of your project
        :param source: Absolute path to your project or project root folder name
        :param dest: target folder for your backups
        :param ignore: list of your files or folders you don't want to have in backup
        :param name_format: strftime format string, default is ISO format
        :param archive_type: Which type of archive you want, if you want to just copy your
        project without using archive use 'None'
        :return Path of your backup"""
    global _format, _dest, _archive_type
    _format = name_format
    _dest = dest
    _archive_type = archive_type

    ignore = ignore or []
    now = datetime.now()
    source = Path(source)
    name_format = now.strftime(name_format)
    dest = Path(dest) / name_format

    def ignore_files(_, files):
        return [f for f in files if f in ignore]

    def remove_readonly(func, path, _):
        os.chmod(path, stat.S_IWRITE)
        func(path)

    shutil.copytree(source, dest, ignore=ignore_files, dirs_exist_ok=True)

    if archive_type is not None:
        shutil.make_archive(str(dest), archive_type, dest)
        shutil.rmtree(dest, onerror=remove_readonly)

    return str(dest)


def clean_up(
        dest: str | PathLike[str] | None = None,
        backups_amounts: int = 0,
        name_format: str | None = None,
        archive_type: Literal["zip", "tar", "gztar", "bztar", "xztar"] | None = "zip",

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
    name_format = name_format or _format
    archive_type = archive_type or _archive_type
    content = os.listdir(dest)
    tmp = datetime.now()
    date_content = [datetime.strptime(t[:len(tmp.strftime(name_format))], name_format) for t in content]

    groups = defaultdict(list)

    for date in date_content:
        groups[date.date()].append(date)

    no_duplicity = [max(v) for v in groups.values()]
    final = no_duplicity[-backups_amounts:]
    to_remove = [t for t in date_content if t not in final]

    for item in to_remove:
        if archive_type:
            os.remove(dest / f"{item.strftime(name_format)}.{archive_type}")
        else:
            os.remove(dest / f"{item.strftime(name_format)}")

    return [
        content,
        [f"{t.strftime(name_format)}.zip" for t in to_remove]
    ]