# coding=utf-8
from __future__ import print_function, absolute_import, unicode_literals

import requests
from pyquery import PyQuery as pq
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
import urllib


class Command(BaseCommand):
    scrape_url_prefix = 'http://cal.syoboi.jp/quarter'

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

        print(idx)

        if idx == -1:
            return []

        staff_q = anime_q('div.comment dl.staff > dd.staffkeywords')
        studio_str = pq(staff_q[idx]).text().strip()

        studio_names = studio_str.split('、')
        print(studio_names)
        return [{
            'studio_name': s,
        } for s in studio_names]

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

