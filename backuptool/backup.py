import shutil
import stat
import os

from pathlib import Path
from datetime import datetime
from os import PathLike
from typing import Literal


def run_backup(
        root_dir: str | PathLike[str]= "", # TODO: find project root
        target_dir: str | PathLike[str] = Path.cwd(),
        ignore: list | None = None,
        name_format: str = "%Y%m%d_%H%M%S", # strftime format string
        archive_type: Literal["zip", "tar", "gztar", "bztar", "xztar"] | None = "zip",
):
    """ Create backup of your project
        :param root_dir: Absolute path to your project or project root folder name
        :param target_dir: target folder for your backups
        :param ignore: list of your files or folders you don't want to have in backup
        :param name_format: strftime format string, default is ISO format
        :param archive_type: Which type of archive you want, if you want to just copy your project without using archive use 'None'
        :return Path to your backup"""
    ignore = ignore or []
    now = datetime.now()
    form = now.strftime(name_format)
    root_dir = Path(root_dir)
    target_dir = Path(target_dir) / form

    def ignore_files(_, files):
        return [f for f in files if f in ignore]

    def remove_readonly(func, path, _):
        os.chmod(path, stat.S_IWRITE)
        func(path)

    shutil.copytree(root_dir, target_dir, ignore=ignore_files, dirs_exist_ok=True)

    if archive_type is not None:
        shutil.make_archive(str(target_dir), archive_type, target_dir)
        shutil.rmtree(target_dir, onerror=remove_readonly)

    return str(target_dir)