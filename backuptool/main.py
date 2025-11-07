import shutil
import os
from collections import defaultdict
from pathlib import Path
from datetime import datetime
from typing import Literal, Optional

from backuptool.backup_instance import BackupInstance
from backuptool.utils import remove_readonly, maximum
from backuptool.utils import config as cng

# ========= GLOBAL DEFAULT VALUES =========== #
_name_format: str = "%Y%m%d_%H%M%S"
_dest: Path = Path.cwd()
_archive_type: Literal["zip", "tar", "gztar", "bztar", "xztar", "noarchive"] = "zip"


def run_backup(
        source: str | Path = Path.cwd(),
        dest: Optional[str | Path] = None,
        ignore: Optional[list[str]] = None,
        name_format: Optional[str] = None, # strftime format string
        archive_type: Optional[Literal["zip", "tar", "gztar", "bztar", "xztar", "noarchive"]] = None,
        config_name: Optional[str | Path] = None,
        keep_name: bool = False
) -> str:
    """ Create backup of your project
        :param source: Absolute path to source or absolute path for file
        :param dest: target folder for your backups
        :param ignore: list of your files or folders you don't want to have in backup
        :param name_format: strftime format string, default is ISO format
        :param archive_type: Which type of archive you want: ["zip", "tar", "gztar", "bzdar", "xztar"] if you want to just copy your folder use 'noarchive'
        project without using archive use 'noarchive'
        :param config_file: Absolut path to config file must be .ini file
        :param keep_name: final file name is name_format + name
        :return: Path of your created backup"""
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
    name_format = now.strftime(name_format)
    isfile = os.path.isfile(source)

    if not isfile: # create backup of folder
        dest_folder = dest / name_format
        def ignore_files(_, files):
            return [f for f in files if f in ignore]
        shutil.copytree(source, dest_folder, ignore=ignore_files, dirs_exist_ok=True)

        if archive_type != "noarchive":
            shutil.make_archive(str(dest_folder), archive_type, dest_folder)
            shutil.rmtree(dest_folder, onerror=remove_readonly)
    else: # create backup of file
        suffix = ""
        for c in source[::-1]:
            if c == ".":
                break
            suffix += c
        dest_folder = f"{dest}/{name_format}.{suffix[::-1]}"
        print(dest_folder)
        shutil.copy(source, dest_folder)

    return str(dest_folder)

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


def run(config_file: Optional[str] = None, **overrides) -> str:
    """ Create backup of your file or folder
        :param config_file: Absolut path to your config file
        :key src: (str, Path) Absolute path of source, it might be file or folder
        :key dst: (str, Path) Absolute path of target folder
        :key ignore: (list[str]) excluded list of files or folders
        :key name_format: (str) strftime string format, default is ISO format
        :key archive_type: (str) allowed archive types: ['zip', 'tar', 'gztar', 'bztar', 'xztar'] or 'nonarchive' stands for do not create archive
        :key keep_name: (bool) result name is name_format + file's/folder's name
        :return: (str) Absolute path of created backup"""
    allowed_params = {
        "src",
        "dst",
        "ignore",
        "name_format",
        "archive_type",
        "keep_name"
    }

    if unknown_params := set(overrides.keys()) - allowed_params:
        raise ValueError(f"Unknown params: {unknown_params}. Allowed: {allowed_params}")

    config = _config_from_default()

    override_config = _configure_config(config, overrides, config_file)

    return _run_process(override_config)


# ===================== MAIN LOGIC ================== #
def _run_process(config: dict) -> str:
    return ""


# ===================== LOAD CONFIG ================ #
def _config_from_file():
    return dict()

def _config_from_default():
    return dict()


# ==================== UTILS =================== #
def _configure_config(current_config: dict, to_override: dict, config_file) -> dict:
    pre_config = current_config
    if config_file:
        pre_config = _override_dict(pre_config, _config_from_file())

    overrides = _override_dict(pre_config, to_override)

    return overrides


def _override_dict(current_dict: dict, new_dict: dict) -> dict:
    overrides = {}
    for k,v in current_dict.items():
        overrides[k] = new_dict[k]

    return overrides