import os
import stat
import configparser
from pathlib import Path

from backuptool.backup import BackupInstance


default_config = {
    "src": Path.cwd(),
    "dst": Path.cwd(),
    "ignore": [],
    "name_format": "%Y%m%d_%H%M%S",
    "archive_type": "zip",
    "keep_name": False,
    "backups_amount": 0
}

def remove_readonly(func, path, _):
    """ Callback for shutil.rmtree. If exception PermissionError raise,
        will remove read-only flag and try to call the func again
        """
    os.chmod(path, stat.S_IWRITE)
    func(path)


def maximum(instances: list[BackupInstance]) -> BackupInstance:
    """ Find the newest date of the day (based on time)
        :param instances: list of days
        :return: newest date
        """
    max_value = instances[0]
    for inst in instances:
        if inst.date_type > max_value.date_type:
            max_value = inst
    return max_value


class AutoCastConfigParser(configparser.ConfigParser):

    def get_auto_cast(self, section, option):
        """Try to convert string to int, bool or keep it as str
            - override .get
            :param section: name of the section
            :param option: name of the option
            :return Union[int, bool, str]: best-match"""
        try:
            value = super().get(section, option)
        except:
            return None

        if value in ["True", "False"]:
            return True if value == "True" else False
        elif value.isdigit():
            return int(value)
        elif ", " in value:
            return value.split(", ")
        else:
            return value

    def convert(self):
        """ Convert config to dictionary
            :return: Config in dictionary
            """
        config = {}
        for section in self.sections():
            for k, v in self[section].items():
                config[k] = v
        return config

f_config = AutoCastConfigParser(interpolation=None)
f_config.read("c:/local/work/python/backuptool/help/config.ini", "utf-8") # TODO: FILE


def set_correct_config(old_config: dict, new_config: dict, config_file) -> dict:
    """ Choose right configuration option,

        Options to choose right configuration: from file, default or from args
        :param old_config: dictionary to overwrite
        :param new_config: dictionary with current changes
        :param config_file: Absolut path of config file location
        :return: right configuration option
        """
    pre_config = dict(old_config)
    if config_file:
        pre_config = _override_dict(pre_config, f_config.convert())

    print(pre_config)
    overrides = _override_dict(pre_config, new_config)
    print(overrides)

    return overrides


def _override_dict(old_dict: dict, new_dict: dict) -> dict:
    """ Overwrite dictionary with another one
        :param old_dict: dictionary to overwrite
        :param new_dict: dictionary with current changes
        :return: overwritten dict
        """
    overrides = {}
    skip = set(old_dict.keys()) ^ set(new_dict.keys())

    for k,v in old_dict.items():
        if k in skip:
            overrides[k] = v
        else:
            overrides[k] = new_dict[k]

    return overrides


def check_kwargs(kwargs):
    """ Check kwargs if it matches with default keys
        :param kwargs: variable to check
        """
    allowed_params = set()
    for k in default_config.keys():
        allowed_params.add(k)

    if unknown_params := set(kwargs.keys()) - allowed_params:
        raise ValueError(f"Unknown params: {unknown_params}. Allowed: {allowed_params}")