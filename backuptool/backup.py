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
        archive_type: Literal["zip", "tar", "gztar", "bztar", "xztar"] = "zip",
):
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
    shutil.make_archive(str(target_dir), archive_type, target_dir)
    os.chmod(target_dir, stat.S_IWRITE)
    shutil.rmtree(target_dir, onerror=remove_readonly)

    return archive_type