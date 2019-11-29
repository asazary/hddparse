import os
import constants
import shelve


class SimpleUserCards:
    def __init__(self, filename=constants.simpleCardsFileName):
        self.arr = []
        self.filename = filename

    def add(self, user_card):
        self.arr.append(user_card)

    def __getitem__(self, item):
        return self.arr[item]

    def __len__(self):
        return len(self.arr)

    def size(self):
        return len(self.arr)

    def file_exists(self):
        return os.path.exists(self.filename + '.dat')

    def save_to_file(self, rewrite_file=False, rewrite_records=False, inc_progress_func=None):
        if not rewrite_file and self.file_exists():
            raise constants.FileExistanceError('File exists')

        cnt = 0
        with shelve.open(self.filename, 'n') as dbase:
            for record in self.arr:
                if not rewrite_records and record.uid in dbase.keys():
                    continue
                dbase[record.uid] = record
                cnt += 1
                if inc_progress_func:
                    inc_progress_func()
        return cnt

    def load_from_file(self, init_progress_func=None, inc_progress_func=None):
        if not self.file_exists():
            raise constants.FileExistanceError('File not exists')

        with shelve.open(self.filename, 'r') as dbase:
            if init_progress_func:
                init_progress_func(len(dbase.keys()) - 1)
            self.arr.clear()

            cnt = 0
            for key, value in dbase.items():
                self.arr.append(value)
                if inc_progress_func:
                    inc_progress_func()
                cnt += 1
        return cnt


class UserCardSimple:
    def __init__(self, uid=None, link=None, imgLink=None, imgData=None, name=None, age=None, type=None):
        self.uid = uid
        self.link = link
        self.imgLink = imgLink
        self.imgData = imgData
        self.name = name
        self.age = age
        self.type = type
