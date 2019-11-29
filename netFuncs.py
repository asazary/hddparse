import requests
from math import floor
import time
import pyquery
from SimpleCards import *
import constants as consts
from datetime import datetime
from UserCards import *


class NetTools:
    def __init__(self, app=None, email=consts.email, password=consts.password):
        self.ses = requests.Session()
        self.email = email
        self.password = password
        self.app = app

    def login_func(self, email=consts.email, password=consts.password):
        r = self.ses.get(consts.loginPage)
        a = r.content.find(b'requestSimpleSign')
        sign = r.content[a + len(b'window.requestSimpleSign = '):r.content.find(b';', a) - 1]

        data = {"action": "processXdget",
                "xdgetId": "99945",
                "params[action]": "login",
                "params[url]": consts.loginPage,
                "params[email]": email,
                "params[password]": password,
                "params[null]": "",
                "params[object_type]": "cms_page",
                "params[object_id]": "-1",
                "requestTime": str(floor(time.time())),
                "requestSimpleSign": sign.decode('utf-8')
                }
        r = self.ses.post(consts.loginPage, data=data)
        status = 'user_id' in r.json()
        if status:
            return (status, r.json()['redirectUrl'])
        else:
            return (status, r.json()['errorMessage'])

    def get_my_profile_page(self):
        r = self.ses.get(consts.myProfilePage)
        print(r.content)
        # return r.content

    def start_search(self, params):
        search_link = consts.searchPage + \
                      '?hd_type=params&d[age_from]={ageFrom}&d[age_to]={ageTo}&d[gender]={gender}&d[city]={city}'
        search_link = search_link.format(**params)

        html = self.ses.get(search_link).content.decode('utf-8')
        dom = pyquery.PyQuery(html)
        cnt_str = dom('div.params-search > button.btn-primary').next('span').text().strip()
        self.app.statusVar.set(cnt_str)
        progress_max_val = int(cnt_str.split()[0])-1 if int(cnt_str.split()[0]) > 0 else 0
        self.app.statusPanel.init_progress_bar(progress_max_val)
        self.app.statusPanel.enable_stop_button()

        stop_flag = False

        while True:
            for user in dom('div.hd-search-card-list > a.hd-user-card').items():
                if self.app.statusPanel.stopFlagVar.get():
                    stop_flag = True
                    break

                href = user.attr('href')
                uid = href[href.rfind('=') + 1:]
                link = consts.siteBase + href
                img_link = 'https:' + user('img.user-profile-image').attr('src')
                img_data = requests.get(img_link).content
                userinfo = user.children('div.hd-user-card-info').text().strip()
                userinfo = [x.strip() for x in userinfo.replace(',', '\n').split('\n')]
                name = userinfo[0]
                age = int(userinfo[1].split()[0])
                type = consts.typesDict[userinfo[2]]

                user_card = UserCardSimple(uid=uid, link=link, imgLink=img_link, imgData=img_data, name=name,
                                           age=age, type=type)

                self.app.simpleCards.add(user_card)
                self.app.statusPanel.inc_progress()

            if stop_flag:
                break

            next_but = dom('div.modal-block-content > div.hd-info > ul.pagination > li.next')
            # print('next = ', next_but)
            if next_but.has_class('disabled') or len(next_but) == 0:
                break
            else:
                # print(next_but.children('a').attr('href'))
                search_link = consts.siteBase + next_but.children('a').attr('href')
                html = self.ses.get(search_link).content.decode('utf-8')
                dom = pyquery.PyQuery(html)

    def start_full_net_search(self, params):
        search_link = consts.searchPage + \
                      '?hd_type=params&d[age_from]={ageFrom}&d[age_to]={ageTo}&d[gender]={gender}&d[city]={city}'
        search_link = search_link.format(**params)
        html = self.ses.get(search_link).content.decode('utf-8')
        dom = pyquery.PyQuery(html)
        cnt_str = dom('div.params-search > button.btn-primary').next('span').text().strip()
        self.app.statusVar.set(cnt_str)
        number_of_records = int(cnt_str.split()[0])
        progress_max_val = int(cnt_str.split()[0]) - 1 if int(cnt_str.split()[0]) > 0 else 0
        self.app.statusPanel.init_progress_bar(progress_max_val)
        self.app.statusPanel.enable_stop_button()

        stop_flag = False
        current_rec_num = 1

        error_log_file = open(consts.error_log_filename, 'w')

        self.app.statusPanel.timeCounter.start(max_progress_val=progress_max_val,
                                               progress_var=self.app.progressVar)

        while True:
            for user in dom('div.hd-search-card-list > a.hd-user-card').items():
                if self.app.statusPanel.stopFlagVar.get():
                    stop_flag = True
                    break

                href = user.attr('href')
                uid = href[href.rfind('=') + 1:]
                link = consts.siteBase + href
                userinfo = user.children('div.hd-user-card-info').text().strip()
                userinfo = [x.strip() for x in userinfo.replace(',', '\n').split('\n')]
                age = int(userinfo[1].split()[0])

                try:
                    user_card = self.parse_user_profile(link, p_age=age)
                    self.app.userCards.add(user_card)
                except Exception as e:
                    error_log_file.write(uid + '\n')
                    error_log_file.write(str(e) + '\n')

                self.app.statusPanel.inc_progress()
                self.app.statusVar.set('%d of %d' % (current_rec_num, number_of_records))
                current_rec_num += 1

            if stop_flag:
                break

            next_but = dom('div.modal-block-content > div.hd-info > ul.pagination > li.next')
            if next_but.has_class('disabled') or len(next_but) == 0:
                break
            else:
                search_link = consts.siteBase + next_but.children('a').attr('href')
                html = self.ses.get(search_link).content.decode('utf-8')
                dom = pyquery.PyQuery(html)

        self.app.statusPanel.timeCounter.stop()
        self.app.statusVar.set('%d cards parsed' % self.app.userCards.size)
        error_log_file.close()
        self.app.statusPanel.disable_stop_button()

    def parse_user_profile(self, link, p_age=None):
        uid = link[link.rfind('=') + 1:]

        html = self.ses.get(link).content.decode('utf-8')
        dom = pyquery.PyQuery(html)

        dom_info = dom('div.hd-info.hd-user-profile')
        img_link = dom_info.find('div.user-profile-image > a').attr('href')
        # img_data = requests.get(img_link).content
        img_data = None
        thumbnail_link = 'https:' + dom_info.find('img.user-profile-image ').attr('src')
        thumbnail_data = requests.get(thumbnail_link).content

        compatibility_link = consts.siteBase + dom_info.find('div > ul.hd-menu-tab li:eq(2) > a').attr('href')
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
                                                  consts.monthsDict[last_login_lst[2]],
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
                            second_name=(name.split()[1] if len(name.split())>1 else None),
                            age=age, city=city, zodiac=zodiac, last_login=last_login, parse_date=parse_date,
                            hd_type=hd_type, profile=profile, cross=cross, authority=authority, definition=definition)

        html = self.ses.get(compatibility_link).content.decode('utf-8')
        dom = pyquery.PyQuery(html)

        compatibility_title = dom('div.hd-info > div.hd-composite-title.hd-composite-title-desktop').clone()\
            .children().remove().end().text().strip()
        compatibility_number = dom('div.hd-info > div.hd-composite-title.hd-composite-title-desktop > div')\
            .text().strip()

        dom_bio = dom('div.hd-info.row > div > div.row')
        # print(dom_bio.find('div > div.hd-bar-physical > div.bar-title').text())
        comp_bio_physical = dom_bio.find('div > div.hd-bar-physical > div.bar-title').text()\
            .split()[1].strip().rstrip('%')
        comp_bio_physical = int(comp_bio_physical)
        comp_bio_intellectual = dom_bio.find('div > div.hd-bar-intellect > div.bar-title').text()\
            .split()[1].strip().rstrip('%')
        comp_bio_intellectual = int(comp_bio_intellectual)
        comp_bio_emotional = dom_bio.find('div > div.hd-bar-emotion > div.bar-title').text()\
            .split()[1].strip().rstrip('%')
        comp_bio_emotional = int(comp_bio_emotional)

        user_card.init_compatibility(relationship_type_text=compatibility_title,
                                     relationship_type=compatibility_number,
                                     bio_physical=comp_bio_physical, bio_intellectual=comp_bio_intellectual,
                                     bio_emotional=comp_bio_emotional)

        return user_card

    def test_search(self):
        testuser = UserCardSimple()
        testlink = 'https://hd.dating/lsp/hd-search?type=params&d[age_from]=0&d[age_to]=30&d[gender]=female&d[city]=Санкт-Петербург&page=1'
        html = self.ses.get(testlink).content.decode('utf-8')

        dom = pyquery.PyQuery(html)
        cntstr = dom('div.params-search > button.btn-primary').next('span').text().strip()
        print(cntstr)
        user = dom('a.hd-user-card').eq(0)
        userlink = consts.siteBase + user.attr('href')
        print(userlink)
        userimglink = 'https:' + user('img.user-profile-image').attr('src')
        print(userimglink)
        # user1 = dim('div.hd-user-card-info').eq(0).text()
        img_data = requests.get(userimglink).content
        userinfo = user.children('div.hd-user-card-info').text().strip()
        userinfolist = [x.strip() for x in userinfo.replace(',', '\n').split('\n')]
        print(userinfolist)
