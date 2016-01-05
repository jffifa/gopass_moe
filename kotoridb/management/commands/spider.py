# coding=utf-8
from __future__ import print_function, absolute_import, unicode_literals

import requests
from pyquery import PyQuery as pq
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from kotoridb.models import *
from django.db.models import Q
import urllib
import pytz
import re
from datetime import datetime, date, timedelta
from .cvimport import warn_print, info_print, fail_print


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
    def studio_import(cls, anime, studio_list):
        for s in studio_list:
            try:
                studio = Studio.objects.get(Q(name=s['studio_name'])|Q(alias=s['studio_name']))
            except Studio.DoesNotExist:
                studio = Studio.objects.create(name=anime['studio_name'])
                info_print('studio[%s] is created' % (s['studio_name'],))
            anime.studios.add(studio)

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
    def cv_import(cls, anime, cv_list):
        chs = anime.animecharacter_set.all()
        for cv in cv_list:
            try:
                p = Person.objects.get(name=cv['cv_name'])
            except Person.MultipleObjectsReturned:
                warn_print('multiple person named [%s] exist, ignore for anime [%s]' % (cv['cv_name'],anime.title))
                continue
            except Person.DoesNotExist:
                try:
                    p = Person.objects.get(alias=cv['cv_name'])
                except Person.MultipleObjectsReturned:
                    warn_print('multiple person aliased [%s] exist, ignore for anime [%s]' % (cv['cv_name'],anime.title))
                    continue
                except Person.DoesNotExist: # not exists, create one
                    p = Person(name=cv['cv_name'])
                    p.save()
                    info_print('create a new person named [%s]' % (cv['cv_name'],))

            try:
                ch = chs.get(name=cv['char_name'])
                ch.cv = p
                ch.save()
            except AnimeCharacter.DoesNotExist:
                ch = AnimeCharacter(name=cv['char_name'], anime=anime, cv=p)
                ch.save()
                info_print('create a new character named [%s] for anime [%s]' % (cv['char_name'],anime.title))

            info_print('import character [%s], whose CV is [%s], for anime [%s] succeeded' % (
                cv['char_name'], cv['cv_name'], anime.title))

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
                    res.append({'staff_title':cls.place_trans[title], 'staff_name':name})

        return res

    @classmethod
    def staff_import(cls, anime, staff_list):
        staffs = anime.staffs
        for staff in staff_list:
            try:
                p = Person.objects.get(name=staff['staff_name'])
            except Person.MultipleObjectsReturned:
                warn_print('multiple person named [%s] exist, ignore for anime [%s] with place [%s]' % (
                    staff['staff_name'], anime.title, staff['staff_title']))
                continue
            except Person.DoesNotExist:
                try:
                    p = Person.objects.get(alias=staff['staff_name'])
                except Person.MultipleObjectsReturned:
                    warn_print('multiple person aliased [%s] exist, ignore for anime [%s] with place[%s]' % (
                        staff['staff_name'], anime.title, staff['staff_title']))
                    continue
                except Person.DoesNotExist: # not exists, create one
                    p = Person(name=staff['staff_name'])
                    p.save()
                    info_print('create a new person named [%s]' % (staff['staff_name'],))

            try:
                s = staffs.get(place=staff['staff_title'], person=p)
            except Staff.ObjectDoesNotExist:
                s = Staff(place=staff['staff_title'], anime=anime, person=p)
                s.save()
                info_print('create a new staff with place [%s] and name [%s] for anime [%s]' %
                           (staff['staff_title'], staff['staff_name'], anime.title))

            info_print('import staff [%s-%s], for anime [%s] succeeded' % (
                    staff['staff_title'], staff['staff_name'], anime.title))

    @classmethod
    def parse_datetime(cls, datetime_str):
        m = re.match(r'(20[0-9][0-9]-[0-1][0-9]-[0-3][0-9])\s+\(.\)\s+([0-9:]+)', datetime_str)
        try:
            date_str = m.group(1)
            time_str = m.group(2)
        except Exception as e:
            print(datetime_str)
            raise e
        y, m, d = map(int, date_str.split('-'))
        hour, min = map(int, time_str.split(':'))

        h24 = 0
        if hour>=24:
            hour -= 24
            h24 = 1
        dt = datetime(y, m, d, hour, min, tzinfo=cls.tz)
        dt += timedelta(days=h24)
        return dt

    @classmethod
    def get_on_air_list(cls, anime_q):
        res = []

        on_air_list_q = anime_q('div.comment div.progs ul > li ')
        first_type = OnAir._TYPE_FIRSTHAND
        for on_air_obj in on_air_list_q:
            on_air_q = pq(on_air_obj)
            datetime = on_air_q('span.StTime').text()
            datetime = cls.parse_datetime(datetime)
            tv = on_air_q('span.ChName').text()
            if tv == 'ニコニコチャンネル':
                tv = 'niconico'
            elif tv == 'ディズニー・チャンネル':
                tv = 'disney channel'
            oa = {
                'type':first_type,
                'tv':tv,
                'time':datetime,
            }
            res.append(oa)
            first_type = OnAir._TYPE_EXTRA

        return res

    @classmethod
    def on_air_import(self, anime, on_air_list):
        for on_air in on_air_list:
            oa = OnAir(anime=anime, tv=on_air['tv'], type=on_air['type'], time=on_air['time'])
            oa.save()

    def anime_import(self, anime_list):
        with transaction.atomic():
            for anime_dict in anime_list:
                # find anime or create first
                try:
                    anime = Anime.objects.get(title=anime_dict['title'])
                except Anime.DoesNotExist:
                    anime = None
                    if anime_dict['title_cn']:
                        try:
                            anime = Anime.objects.get(alias=anime_dict['title_cn'])
                        except Anime.DoesNotExist:
                            anime = None
                    if anime is None:
                        anime = Anime()

                anime.title = anime_dict['title']
                if anime_dict['title_cn']:
                    anime.alias = anime_dict['title_cn']
                if anime_dict['homepage']:
                    anime.homepage = anime_dict['homepage']
                anime.save()

                if anime_dict['studio_list']:
                    self.studio_import(anime, anime_dict['studio_list'])

                if anime_dict['cv_list']:
                    self.cv_import(anime, anime_dict['cv_list'])

                if anime_dict['staff_list']:
                    self.staff_import(anime, anime_dict['staff_list'])

                if anime_dict['on_air_list']:
                    self.on_air_import(anime, anime_dict['on_air_list'])

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
            anime['on_air_list'] = self.get_on_air_list(anime_q)
            #print(anime)
            anime_list.append(anime)

        self.anime_import(anime_list)


