from datetime import datetime

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