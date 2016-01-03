# coding=utf-8
from __future__ import print_function, absolute_import, unicode_literals

import requests
from pyquery import PyQuery as pq
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction


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
        parser.add_argument('-t', '--time', nargs=1)

    def handle(self, *args, **options):
        scrape_url = '/'.join((
            self.scrape_url_prefix,
            self.gen_scrape_url_suffix(options['time'])))
        resp = requests.get(scrape_url)

        if resp.status_code != 200:
            raise CommandError('Scrape URL "%s" is unavailable.' % (scrape_url,))

        html_raw = resp.text
        ctx = pq(html_raw)
        anime_list_q = ctx('ul.titlesDetail > li')

        anime_list = [
        ]

        for anime_e in anime_list_q:
            anime = {
                'title':None,
                'homepage':None,
                'staff_list':[],
                'cv_list':[],
                'on_air_list':[],
            }
            anime_q = pq(anime_e)
