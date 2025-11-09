import os
import stat
import configparser

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
            :return: Config in dictionary"""
        config = {}
        for section in self.sections():
            for k, v in self[section].items():
                config[k] = v
        return config

f_config = AutoCastConfigParser(interpolation=None)
f_config.read("c:/local/work/python/backuptool/help/config.ini", "utf-8") # TODO: FILE