# coding=utf-8
from __future__ import print_function, unicode_literals, absolute_import

import re
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from .color_print import fail_print, warn_print, info_print
from kotoridb.models import Anime, Studio, OnAir
from django.db.models import Q
from datetime import datetime, timedelta
from pytz import timezone

class Command(BaseCommand):
    args = ''
    help = 'import anime list'

    from optparse import make_option
    option_list = BaseCommand.option_list + (
        make_option('-l', '--anime-list', dest='anime_list', help='anime list file', metavar='ANIME_LIST'),
    )

    def parse_line(self, anime, line):
        keys = {
            '原名':'title',
            '官网':'homepage',
            '译名':'alias',
            '公司':'studio',
            '电视台':'tv',
            '首播日期':'date',
            '首播时间':'time',
        }
        for k in keys.keys():
            match = re.match(k+r'\s+(.+)$', line)
            if match:
                value = match.group(1)
                anime[keys[k]] = value

    def save_anime(self, anime):
        assert('title' in anime)
        if Anime.objects.filter(title=anime['title']).exists():
            warn_print('anime[%s] already exists' % (anime['title'],))
            return

        a = Anime()
        a.title = anime['title']

        if 'homepage' in anime:
            a.homepage = anime['homepage']
        if 'alias' in anime:
            a.alias = anime['alias']

        a.save()
        info_print('anime[%s] is created' % (anime['title'],))

        if 'studio' in anime:
            try:
                studio = Studio.objects.get(Q(name=anime['studio'])|Q(alias=anime['studio']))
            except Studio.DoesNotExist:
                studio = Studio.objects.create(name=anime['studio'])
                info_print('studio[%s] is created' % (anime['studio'],))
            a.studios.add(studio)

        if 'tv' in anime:
            oa = OnAir()
            oa.anime = a
            oa.tv = anime['tv']
            if 'date' in anime:
                if 'time' not in anime:
                    anime['time'] = '00:00'
                anime['date'] = '2015/'+anime['date']
                hour, minute = map(int, anime['time'].split(':'))
                day_delta = 0
                if hour >= 24:
                    hour -= 24
                    day_delta = 1
                    anime['time'] = '%02d:%02d' % (hour, minute)
                dt = datetime.strptime(anime['date']+' '+anime['time'], '%Y/%m/%d %H:%M')+timedelta(days=day_delta)
                oa.time = timezone('Asia/Tokyo').localize(dt)
            oa.save()

    def import_one(self, offset, lines):
        anime = {}
        while offset < len(lines):
            line = lines[offset].strip()
            if not line:
                self.save_anime(anime)
                return offset+1

            self.parse_line(anime, line)
            offset += 1

    def anime_import(self, lines):
        offset = 0
        while offset < len(lines):
            line = lines[offset].strip()
            if not line:
                offset += 1
                continue

            offset = self.import_one(offset, lines)

    def handle(self, *args, **options):
        if not options['anime_list']:
            raise CommandError('anime list file must be specified')
        import os.path
        if not (os.path.exists(options['anime_list']) and os.path.isfile(options['anime_list'])):
            raise CommandError('anime list %s is not an legal file.' % (options['anime_list'],))

        import codecs
        with open(options['anime_list'], 'rb') as rawf:
            raw = rawf.read(4)
            if raw.startswith(codecs.BOM_UTF8):
                encoding = 'utf-8-sig'
            else:
                encoding = 'utf-8'


        with open(options['anime_list'], 'r') as f:
            transaction.set_autocommit(False)
            try:
                s = f.read()
                u = s.decode(encoding)
                l = u.splitlines()
                self.anime_import(l)
                transaction.commit()
            except Exception as e:
                fail_print(str(e))
                transaction.rollback()
