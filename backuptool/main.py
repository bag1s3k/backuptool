import shutil
import os
from collections import defaultdict
from pathlib import Path
from datetime import datetime
from typing import Optional

from backuptool.backup import BackupInstance
from backuptool.utils import remove_readonly, maximum, set_correct_config
from backuptool.decorator import check_kwargs
from backuptool.CONSTANS import DEFAULT_CONFIG


@check_kwargs(DEFAULT_CONFIG)
def run(config_file: Optional[str | Path] = None, **overrides) -> str:
    """ Create backup of your file or folder

        :param config_file: Absolut path to your config file
        :key src: (str, Path) Absolute path of source, it might be file or folder
        :key dst: (str, Path) Absolute path of target folder
        :key ignore: (list[str]) excluded list of files or folders
        :key name_format: (str) strftime string format, default is ISO format
        :key archive_type: (str) allowed archive types: ['zip', 'tar', 'gztar', 'bztar', 'xztar'] or 'nonarchive' stands for do not create archive
        :key keep_name: (bool) result name is name_format + file's/folder's name
        :return: (str) Absolute path of created backup
        """

    # check_kwargs(overrides)

    override_config = set_correct_config(DEFAULT_CONFIG, overrides, config_file)

    # --------------- LOGIC ITSELF --------------- #
    now = datetime.now()
    name_format_datetime = now.strftime(override_config["name_format"])

    if override_config["keep_name"]:
        file_name = override_config["src"].split("/")
        if "." in file_name[-1]:
            file_name = file_name[-1].split(".")[0]
        else:
            file_name = file_name[-1]
    else:
        file_name = ""

    # create backup of folder
    if not os.path.isfile(override_config["src"]):
        print(file_name)
        dest_folder = Path(override_config["dst"]) / Path(f"{name_format_datetime}_{file_name}")

        def ignore_files(_, files):
            return [f for f in files if f in override_config["ignore"]]

        shutil.copytree(
            override_config["src"],
            dest_folder,
            ignore=ignore_files,
            dirs_exist_ok=True
        )

        if override_config["archive_type"] != "noarchive":
            shutil.make_archive(str(dest_folder), override_config["archive_type"], dest_folder)
            shutil.rmtree(dest_folder, onerror=remove_readonly)

    # create backup of file
    else:
        suffix = ""
        for c in override_config["src"][::-1]:
            if c == ".":
                break
            suffix += c
        dest_folder = f"{override_config["dst"]}/{name_format_datetime}_{file_name}.{suffix[::-1]}"
        shutil.copy(override_config["src"], dest_folder)

    return str(dest_folder)


@check_kwargs(DEFAULT_CONFIG)
def clean_up(config_file: Optional[str | Path] = None, **overrides) -> dict:
    """ Clean up backup folder

        :param config_file:
        :return: dict of: folder content, isbackup, removed files

        if you have never used run_backup before, default is ISO format
        if you want to just copy your project without using archive, use 'None' \
        default is current path
        """
    # check_kwargs(overrides)

    override_config = set_correct_config(DEFAULT_CONFIG, overrides, config_file)
    content = os.listdir(override_config["dst"])

    # Length of format string
    date_len = len(datetime.now().strftime(override_config["name_format"]))

    isbackup = []
    for file in content:
        try:
            datetime.strptime(file[:date_len], override_config["name_format"])
            isbackup.append(file)
        except ValueError:
            continue

    # Create date data structure dict {date: suffix}
    date_content: list[BackupInstance] = []
    for file in isbackup:
        date_content.append(BackupInstance(file, date_len, override_config["name_format"]))

    # Split by just by date (not by time)
    groups = defaultdict(list[BackupInstance])
    for backup in date_content:
        groups[backup.date_type.date()].append(backup)

    # no_duplicity = [max(v, key=lambda f) for v in groups.values()] # Select the newest \
    # date of each day
    no_duplicity = []
    for backups in groups.values():
        no_duplicity.append(maximum(backups))

    final = sorted(no_duplicity, key=lambda b: b.date_type)[-int(override_config["backups_amount"]):]  # take only given \
    # amount
    to_remove = [t for t in date_content if t not in final]

    # Delete backups
    for item in to_remove:
        path = Path(override_config["dst"]) / Path(item.file)
        if item.suffix:
            os.remove(path)
        else:
            shutil.rmtree(path, onerror=remove_readonly)

    return {
        "content": content,
        "isbackup": isbackup,
        "removed": [f.file for f in to_remove]
    }