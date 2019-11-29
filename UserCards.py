from constants import userCardsFileName, FileExistanceError
import os
import shelve
from datetime import datetime


class UserCards:
    def __init__(self, master, filename=userCardsFileName):
        self.app = master
        self.arr = []
        self.dbFileName = filename
        self.size = 0

        self.arrFilter = []
        self.arrFilterSize = 0

    def add(self, card):
        self.arr.append(card)
        self.size += 1

    def get(self, item):
        return self.arrFilter[item]

    def __getitem__(self, item):
        return self.arr[item]

    def __len__(self):
        return len(self.arr)

    def file_exists(self):
        return os.path.exists(self.dbFileName + '.dat')

    def save_to_file(self, rewrite_file=False, rewrite_records=False, inc_progress_func=None):
        # if not rewrite_file and self.file_exists():
        #    raise FileExistanceError('File exists')

        cnt = 0
        if not rewrite_file and self.file_exists(): # adding records
            open_flag = 'c'
        else:
            open_flag = 'n'

        with shelve.open(self.dbFileName, open_flag) as dbase:
            for record in self.arr:
                if not rewrite_records and record.uid in dbase.keys():
                    continue
                dbase[record.uid] = record
                cnt += 1
                if inc_progress_func:
                    inc_progress_func()
        self.app.statusVar.set('%d cards saved' % cnt)
        return cnt

    def load_from_file(self, init_progress_func=None, inc_progress_func=None, size_var=None):
        if not self.file_exists():
            raise FileExistanceError('File not exists')

        with shelve.open(self.dbFileName, 'r') as dbase:
            if init_progress_func:
                init_progress_func(len(dbase.keys()) - 1)
            self.arr.clear()

            cnt = 0
            for key, value in dbase.items():
                self.arr.append(value)
                if inc_progress_func:
                    inc_progress_func()
                cnt += 1
        self.size = cnt
        if size_var:
            size_var.set(cnt)
        self.app.statusVar.set('Loaded %d cards' % cnt)
        return cnt

    def filter(self, age_min, age_max, hd_type, bio_physical_min, bio_intellectual_min, bio_emotional_min,
               min_last_login_date):
        self.arrFilter.clear()
        self.arrFilterSize = 0
        self.app.statusPanel.init_progress_bar(max_value=self.app.userCards.size)

        for card in self.arr:
            fl = True
            if not (age_min <= card.age <= age_max): fl = False
            if not (hd_type == 'все' or card.hd_type == hd_type): fl = False
            if not (card.bio_physical >= bio_physical_min): fl = False
            if not (card.bio_intellectual >= bio_intellectual_min): fl = False
            if not (card.bio_emotional >= bio_emotional_min): fl = False
            min_last_login_datetime = datetime(min_last_login_date.year,
                                               min_last_login_date.month,
                                               min_last_login_date.day)
            if not (card.lastLogin >= min_last_login_datetime): fl = False

            if fl:
                self.arrFilter.append(card)
                self.arrFilterSize += 1

            self.app.statusPanel.inc_progress()
        self.app.statusVar.set('%d cards selected' % self.arrFilterSize)

    def clear_all(self):
        self.arr.clear()
        self.size = 0
        self.arrFilter.clear()
        self.arrFilterSize = 0

class UserCard:
    def __init__(self):
        self.uid = None
        self.premium = None
        self.link = None
        self.compatibilityLink = None
        self.imgLink = None
        self.imgData = None
        self.thumbnailLink = None
        self.thumbnailData = None
        self.gender = None
        self.firstName = None
        self.secondName = None
        self.age = None
        self.city = None
        self.zodiac = None
        self.lastLogin = None
        self.parseDate = None

        self.hd_type = None
        self.profile = None
        self.cross = None
        self.authority = None
        self.definition = None

        self.relationshipTypeText = None
        self.relationshipType = None
        self.bio_physical = None
        self.bio_intellectual = None
        self.bio_emotional = None

    def init_main(self, uid, premium, link, compatibility_link, img_link, img_data,
                  thumbnail_link, thumbnail_data,
                  first_name, second_name, age, city, zodiac, last_login, parse_date,
                  hd_type, profile, cross, authority, definition):
        self.uid = uid
        self.premium = premium
        self.link = link
        self.compatibilityLink = compatibility_link
        self.imgLink = img_link
        self.imgData = img_data
        self.thumbnailLink = thumbnail_link
        self.thumbnailData = thumbnail_data
        self.gender = None
        self.firstName = first_name
        self.secondName = second_name
        self.age = age
        self.city = city
        self.zodiac = zodiac
        self.lastLogin = last_login
        self.parseDate = parse_date
        self.hd_type = hd_type
        self.profile = profile
        self.cross = cross
        self.authority = authority
        self.definition = definition


    def init_compatibility(self, relationship_type_text, relationship_type,
                           bio_physical, bio_intellectual, bio_emotional):
        self.relationshipTypeText = relationship_type_text
        self.relationshipType = relationship_type
        self.bio_physical = bio_physical
        self.bio_intellectual = bio_intellectual
        self.bio_emotional = bio_emotional

    def test_print(self):
        print('uid = %s' % self.uid)
        print('premium = ', self.premium)
        print('link = ', self.link)
        print('img link = ', self.imgLink)
        print('name = ', self.firstName, self.secondName)
        print('age = ', self.age)
        print('city = ', self.city)
        print('zodiac = ', self.zodiac)
        print('last login = ', self.lastLogin)
        print('hd type = ', self.hd_type)
        print('profile = ', self.profile)
        print('cross = ', self.cross)
        print('authority = ', self.authority)
        print('definition = ', self.definition)
        print('relat title = ', self.relationshipTypeText)
        print('relat num = ', self.relationshipType)
        print('bio: phys = %d, intel = %d, emo = %d' % (self.bio_physical, self.bio_intellectual, self.bio_emotional))
