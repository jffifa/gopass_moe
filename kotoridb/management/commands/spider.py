# coding=utf-8
from __future__ import print_function, absolute_import, unicode_literals

import requests
from pyquery import PyQuery as pq
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from kotoridb.models import Staff
import urllib
import pytz


class Command(BaseCommand):
    scrape_url_prefix = 'http://cal.syoboi.jp/quarter'
    place_trans = Staff.get_place_trans()
    tz = pytz.timezone('Asia/Tokyo')

    @classmethod
    def gen_scrape_url_suffix(cls, time):
        year, month = time.split('.')

        year = int(year)
        assert year>=2010, year<=2038
        month = int(month)
        q_dict = {1:'1',4:'2',7:'3',10:'4'}
        assert month in q_dict

        return 'q'.join((str(year), q_dict[month]))

    def add_arguments(self, parser):
        parser.add_argument('-t', '--time', dest='time')

    @classmethod
    def get_anime_title(cls, anime_q):
        title = anime_q('table > tr > td > a.title').text().strip()
        return title

    @classmethod
    def guess_anime_title_cn(cls, title):
        def gen_scrape_url(title):
            return 'http://bangumi.tv/subject_search/%s' % (urllib.quote_plus(title.encode('utf-8')))

        resp = requests.get(gen_scrape_url(title), params={'cat':'2'})
        # force resp use encoding utf-8
        resp.encoding = 'utf-8'
        if resp.status_code != 200:
            return None

        bgm_raw = resp.text
        bgm = pq(bgm_raw)
        title_cn = bgm('ul#browserItemList > li h3 span.subject_type_2').eq(0).parent().children('a.l').text().strip()
        if title_cn:
            return title_cn
        else:
            return None

    @classmethod
    def get_homepage(cls, anime_q):
        link = anime_q('div.comment div.links > ul > li > a').eq(0).attr['href']
        if link:
            return link
        else:
            return None

    @classmethod
    def get_studio_list(cls, anime_q):
        staff_q = anime_q('div.comment dl.staff > dt')
        idx = -1
        for idx, staff_title in enumerate(staff_q):
            if pq(staff_title).text() == 'アニメーション制作':
                break

        if idx == -1:
            return []

        staff_q = anime_q('div.comment dl.staff > dd.staffkeywords')
        studio_str = pq(staff_q[idx]).text().strip()

        studio_names = studio_str.split('、')
        return [{
            'studio_name': s,
        } for s in studio_names]

    @classmethod
    def get_cv_list(cls, anime_q):
        res = []
        cast_char_q = anime_q('div.comment dl.cast > dt')
        cast_q = anime_q('div.comment dl.cast > dd.staffkeywords')

        for char, cast in [(pq(x), pq(y)) for (x, y) in zip(cast_char_q, cast_q)]:
            char_name = char.text().strip()
            cast_name = cast.text().strip()
            res.append({'char_name':char_name,'cv_name':cast_name})

        return res

    @classmethod
    def get_staff_list(cls, anime_q):
        res = []
        staff_title_q = anime_q('div.comment dl.staff > dt')
        staff_q = anime_q('div.comment dl.staff > dd.staffkeywords')

        for staff_title, staff in [(pq(x), pq(y)) for (x, y) in zip (staff_title_q, staff_q)]:
            staff_title_name = staff_title.text().strip()
            staff_name = staff.text().strip()
            if staff_title_name == 'アニメーション制作':
                continue

            # split staff_title:
            title_list = [x.strip() for x in staff_title_name.split('・')]
            # split staff name
            name_list = [x.strip() for x in staff_name.split('、')]

            for title in title_list:
                if title not in cls.place_trans:
                    continue
                for name in name_list:
                    res.append({'staff_title':cls.place_trans(title), 'staff_name':name})

        return res

    @classmethod
    def get_on_air_list(cls, anime_q):


    def handle(self, *args, **options):
        scrape_url = '/'.join((
            self.scrape_url_prefix,
            self.gen_scrape_url_suffix(options['time'])))
        resp = requests.get(scrape_url)

        if resp.status_code != 200:
            raise CommandError('Scrape URL "%s" is unavailable.' % (scrape_url,))

        html_raw = resp.text
        html = pq(html_raw)
        anime_list_q = html('ul.titlesDetail > li')

        anime_list = [
        ]

        for anime_e in anime_list_q:
            anime = {
                'title':None,
                'title_cn':None,
                'homepage':None,
                'staff_list':[],
                'cv_list':[],
                'on_air_list':[],
                'studio_list':[],
            }
            anime_q = pq(anime_e)

            anime['title'] = self.get_anime_title(anime_q)
            anime['title_cn'] = self.guess_anime_title_cn(anime['title'])
            anime['homepage'] = self.get_homepage(anime_q)
            anime['studio_list'] = self.get_studio_list(anime_q)
            anime['cv_list'] = self.get_cv_list(anime_q)
            anime['staff_list'] = self.get_staff_list(anime_q)
            anime_list.append(anime)

