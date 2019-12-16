import threading
from queue import Queue
from UserCards import *
import constants
import requests
import time
from math import floor
import pyquery
import re
from constants import DEBUG_MODE


class NetTools:
    def __init__(self, app=None, email=constants.email, password=constants.password):
        self.app = app
        self.session = requests.Session()
        self.stop_flag = False
        self.stop_flag_lock = threading.Lock()

        self.users_links_queue = None
        self._users_links_threads_number = 5
        self._cards_left = 0
        self._cards_left_lock = threading.Lock()
        self._error_log_file_lock = threading.Lock()

        self.status_lock = threading.Lock()

        self.parse_pages_thread = None
        self.parse_profiles_threads = []

        self.user_gender = None

    def login_func(self, email=constants.email, password=constants.password):
        if email == '':
            email = constants.email
        if password == '':
            password = constants.password

        r = self.session.get(constants.loginPage)
        a = r.content.find(b'requestSimpleSign')
        sign = r.content[a + len(b'window.requestSimpleSign = '):r.content.find(b';', a) - 1]

        data = {"action": "processXdget",
                "xdgetId": "99945",
                "params[action]": "login",
                "params[url]": constants.loginPage,
                "params[email]": email,
                "params[password]": password,
                "params[null]": "",
                "params[object_type]": "cms_page",
                "params[object_id]": "-1",
                "requestTime": str(floor(time.time())),
                "requestSimpleSign": sign.decode('utf-8')
                }
        r = self.session.post(constants.loginPage, data=data)
        status = 'user_id' in r.json()
        if status:
            return status, r.json()['redirectUrl']
        else:
            return status, r.json()['errorMessage']

    def start_full_net_search(self, params, threads_number=5):
        if DEBUG_MODE:
            print("TEST: start net search")
        search_link = constants.searchPage + constants.search_page_params
        search_link = search_link.format(**params)
        html = self.session.get(search_link).content.decode('utf-8')
        dom = pyquery.PyQuery(html)
        cnt_str = dom('div.params-search > button.btn-primary').next('span').text().strip()

        self.number_of_records = int(cnt_str.split()[0])
        progress_max_val = self.number_of_records - 1 if self.number_of_records > 0 else 0
        self._cards_left = self.number_of_records

        if params["gender"] in ("male", "female"):
            self.user_gender = params["gender"]
        else:
            self.user_gender = None

        if DEBUG_MODE:
            print("TEST: max progress: %s" % cnt_str)

        if self.app.statusPanel is not None:
            self.app.statusPanel.set_status(cnt_str)
            self.app.statusPanel.init_progress_bar(progress_max_val)
            self.app.statusPanel.enable_stop_button()

        self.stop_flag = False
        self.users_links_queue = Queue()

        self.app.statusPanel.timeCounter.start(max_progress_val=progress_max_val,
                                               progress_var=self.app.statusPanel.progressVar,
                                               stop_status_func=self.app.statusPanel.get_stop_status)

        self.parse_pages_thread = threading.Thread(target=lambda: self.parse_pages_thread_func(dom))
        self.parse_pages_thread.start()

        self.parse_profiles_threads.clear()
        for i in range(threads_number):
            thread = threading.Thread(target=lambda: self.user_profile_parser(i))
            self.parse_profiles_threads.append(thread)
            thread.start()

        while not self.app.statusPanel.get_stop_status() and self._cards_left > 0:
            time.sleep(0.5)

        self.app.statusPanel.timeCounter.stop()
        self.app.statusPanel.set_status('%d cards parsed' % self.app.userCards.size)
        self.app.statusPanel.disable_stop_button()

    def parse_users_list(self, dom):
        for user in dom('div.hd-search-card-list > a.hd-user-card').items():
            href = user.attr('href')
            uid = href[href.rfind('=') + 1:]
            link = constants.siteBase + href
            user_info = user.children('div.hd-user-card-info').text().strip()
            user_info = [x.strip() for x in re.split("\n|,", user_info)]
            age = int(user_info[-2].split()[0])

            self.users_links_queue.put((link, uid, age))

            if self.app.statusPanel.get_stop_status():
                break

        next_but = dom('div.modal-block-content > div.hd-info > ul.pagination > li.next')
        if next_but.has_class('disabled') or len(next_but) == 0:
            next_link = None
        else:
            next_link = constants.siteBase + next_but.children('a').attr('href')

        return next_link

    def parse_pages_thread_func(self, init_dom):
        next_link = "..."
        dom = init_dom
        r = re.compile(r'page=(\d*)\&')
        while not self.stop_flag and next_link is not None:
            next_link = self.parse_users_list(dom)
            if next_link is None:
                break
            html = self.session.get(next_link).content.decode('utf-8')
            dom = pyquery.PyQuery(html)

            if DEBUG_MODE:
                print("TEST: got page %s" % r.findall(html)[0])

        if DEBUG_MODE:
            print("TEST: page parser thread stopped")

    def parse_user_profile(self, link, p_age=None):
        uid = link[link.rfind('=') + 1:]

        html = self.session.get(link).content.decode('utf-8')
        dom = pyquery.PyQuery(html)

        dom_info = dom('div.hd-info.hd-user-profile')
        img_link = dom_info.find('div.user-profile-image > a').attr('href')
        # img_data = requests.get(img_link).content
        img_data = None
        thumbnail_link = 'https:' + dom_info.find('img.user-profile-image ').attr('src')
        thumbnail_data = requests.get(thumbnail_link).content

        compatibility_link = constants.siteBase + dom_info.find('div > ul.hd-menu-tab li:eq(2) > a').attr('href')
        name = dom_info.find('div > h1.f-header').text().strip()

        short_list_info_cnt = dom_info.find('div > div.hd-short-info-list > span').size()

        premium_elem = None
        city_elem = None
        age_elem = None
        zodiac_elem = None
        last_login_elem = None

        if short_list_info_cnt == 5:
            premium_elem = dom_info.find('div > div.hd-short-info-list > span:eq(0)')
            city_elem = dom_info.find('div > div.hd-short-info-list > span:eq(1)')
            age_elem = dom_info.find('div > div.hd-short-info-list > span:eq(2)')
            zodiac_elem = dom_info.find('div > div.hd-short-info-list > span:eq(3)')
            last_login_elem = dom_info.find('div > div.hd-short-info-list > span:eq(4)')

        elif short_list_info_cnt == 4:
            premium_elem = None
            city_elem = dom_info.find('div > div.hd-short-info-list > span:eq(0)')
            age_elem = dom_info.find('div > div.hd-short-info-list > span:eq(1)')
            zodiac_elem = dom_info.find('div > div.hd-short-info-list > span:eq(2)')
            last_login_elem = dom_info.find('div > div.hd-short-info-list > span:eq(3)')

        elif short_list_info_cnt == 3:
            premium_elem = dom_info.find('div > div.hd-short-info-list > span:eq(0)')
            city_elem = dom_info.find('div > div.hd-short-info-list > span:eq(1)')
            age_elem = None
            zodiac_elem = None
            last_login_elem = dom_info.find('div > div.hd-short-info-list > span:eq(2)')

        elif short_list_info_cnt == 2:
            premium_elem = None
            city_elem = dom_info.find('div > div.hd-short-info-list > span:eq(0)')
            age_elem = None
            zodiac_elem = None
            last_login_elem = dom_info.find('div > div.hd-short-info-list > span:eq(1)')

        age = p_age
        if premium_elem is not None:
            premium = True
        else:
            premium = False
        if city_elem is not None:
            city = city_elem.text().strip().rstrip('.')
        else:
            city = None
        if age_elem is not None:
            pass
        if zodiac_elem is not None:
            zodiac = zodiac_elem.text().strip()
        else:
            zodiac = None
        if last_login_elem is not None:
            if last_login_elem.text() == 'сейчас на сайте':
                last_login = datetime.now()
            else:
                last_login_lst = last_login_elem.text().strip().split()
                # print(last_login_lst)
                last_login_str = '%s.%s.%s %s' % (last_login_lst[1].ljust(2, '0'),
                                                  constants.monthsDict[last_login_lst[2]],
                                                  datetime.now().strftime('%Y'),
                                                  last_login_lst[3].ljust(5, '0'))
                last_login = datetime.strptime(last_login_str, '%d.%m.%Y %H:%M')

            if last_login > datetime.now():
                last_login = last_login.replace(year=int(last_login.strftime('%Y')) - 1)
        else:
            last_login = None

        parse_date = datetime.now()
        # --------

        hd_type = dom_info.find('div > div.hd-tags-list > div.main-tags > a:eq(0)').text()
        profile = dom_info.find('div > div.hd-tags-list > div.main-tags > a:eq(1)').text()
        cross = dom_info.find('div > div.hd-tags-list > div.main-tags > a:eq(2)').text()

        authority = dom_info.find('div > div.hd-tags-list div:eq(1) > a:eq(0)').text()
        definition = dom_info.find('div > div.hd-tags-list div:eq(1) > a:eq(1)').text()

        user_card = UserCard()
        user_card.init_main(uid=uid, premium=premium, link=link, compatibility_link=compatibility_link,
                            img_link=img_link, img_data=img_data,
                            thumbnail_link=thumbnail_link, thumbnail_data=thumbnail_data,
                            first_name=name.split()[0],
                            second_name=(name.split()[-1] if len(name.split()) > 1 else None),
                            age=age, city=city, zodiac=zodiac, last_login=last_login, parse_date=parse_date,
                            hd_type=hd_type, profile=profile, cross=cross, authority=authority, definition=definition,
                            gender=self.user_gender)

        html = self.session.get(compatibility_link).content.decode('utf-8')
        dom = pyquery.PyQuery(html)

        compatibility_title = dom('div.hd-info > div.hd-composite-title.hd-composite-title-desktop').clone() \
            .children().remove().end().text().strip()
        compatibility_number = dom('div.hd-info > div.hd-composite-title.hd-composite-title-desktop > div') \
            .text().strip()

        dom_bio = dom('div.hd-info.row > div > div.row')
        # print(dom_bio.find('div > div.hd-bar-physical > div.bar-title').text())
        comp_bio_physical = dom_bio.find('div > div.hd-bar-physical > div.bar-title').text() \
            .split()[1].strip().rstrip('%')
        comp_bio_physical = int(comp_bio_physical)
        comp_bio_intellectual = dom_bio.find('div > div.hd-bar-intellect > div.bar-title').text() \
            .split()[1].strip().rstrip('%')
        comp_bio_intellectual = int(comp_bio_intellectual)
        comp_bio_emotional = dom_bio.find('div > div.hd-bar-emotion > div.bar-title').text() \
            .split()[1].strip().rstrip('%')
        comp_bio_emotional = int(comp_bio_emotional)

        user_card.init_compatibility(relationship_type_text=compatibility_title,
                                     relationship_type=compatibility_number,
                                     bio_physical=comp_bio_physical, bio_intellectual=comp_bio_intellectual,
                                     bio_emotional=comp_bio_emotional)
        return user_card

    def user_profile_parser(self, num=0):
        while not self.app.statusPanel.get_stop_status() and self._cards_left > 0:
            if self.users_links_queue.empty():
                continue

            (link, uid, age) = self.users_links_queue.get()
            if DEBUG_MODE:
                print("TEST: thread %d: got %s" % (num, uid))
            try:
                user_card = self.parse_user_profile(link, p_age=age)
                self.app.userCards.add(user_card)
            except Exception as e:
                with open(constants.error_log_filename, 'w') as error_log_file:
                    error_log_file.write(uid + '\n')
                    error_log_file.write(str(e) + '\n')

            with self._cards_left_lock:
                self._cards_left -= 1
                cleft = self._cards_left
            with self.status_lock:
                self.app.statusPanel.inc_progress()
                self.app.statusPanel.set_status('%d of %d' % (self.number_of_records - cleft, self.number_of_records))

        if DEBUG_MODE:
            print("TEST: thread %d stopped" % num)