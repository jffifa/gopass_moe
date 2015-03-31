# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.db import transaction
from kotoridb.models import Anime, Person, AnimeCharacter
from .color_print import warn_print, info_print, fail_print
import re

class Command(BaseCommand):
    args = ''
    help = 'imports cv list.'

    from optparse import make_option
    option_list = BaseCommand.option_list + (
        make_option('-l', '--cv-list', dest='cv_list', help='cv list file', metavar='CV_LIST'),
    )

    def check_ascii(self, ch):
        return ord(ch)<128

    def deal_str(self, s):
        tr = '　 '
        s = s.strip(tr)
        # remove ()
        s = re.sub(r'([^()]+)\([^()]+\)', r'\1', s).strip(tr)
        s = re.sub(r'([^（）]+)（[^（）]+）', r'\1', s).strip(tr)
        # deal with space
        res = ''
        for i, c in enumerate(s):
            if c == ' ':
                if self.check_ascii(s[i-1]) or self.check_ascii(s[i+1]):
                    res += c
            else:
                res += c
        return res

    def cvimport(self, lines):
        anime = None
        chs = None
        for line in lines:
            line = line.strip()
            if not line:
                continue

            if line[0] == '*':
                anime_name = line[1:].strip()
                anime = None
                try:
                    anime = Anime.objects.get(title=anime_name)
                except ObjectDoesNotExist:
                    try:
                        anime = Anime.objects.get(alias=anime_name)
                    except ObjectDoesNotExist:
                        warn_print('anime [%s] not found. ignored.' % (anime_name,))
                        continue
                chs = anime.animecharacter_set.all()
                continue

            if not anime:
                continue

            character, cv = re.sub(r'( ){2,}', r'|', line, 1).split('|')
            character, cv = self.deal_str(character), self.deal_str(cv)
            #print(character, cv)

            if not character or not cv:
                continue

            try:
                p = Person.objects.get(name=cv)
            except MultipleObjectsReturned:
                warn_print('multiple person named [%s] exist, ignore for anime [%s]' % (cv,anime.title))
                continue
            except ObjectDoesNotExist:
                try:
                    p = Person.objects.get(alias=cv)
                except MultipleObjectsReturned:
                    warn_print('multiple person aliased [%s] exist, ignore for anime [%s]' % (cv,anime.title))
                    continue
                except ObjectDoesNotExist: # not exists, create one
                    p = Person(name=cv)
                    p.save()
                    info_print('create a new person named [%s]' % (cv,))

            try:
                ch = chs.get(name=character)
                ch.cv = p
                ch.save()
            except ObjectDoesNotExist:
                ch = AnimeCharacter(name=character, anime=anime, cv=p)
                ch.save()
                info_print('create a new character named [%s] for anime [%s]' % (cv,anime.title))

            info_print('import character [%s], whose CV is [%s], for anime [%s] succeeded' % (
                character, cv, anime.title))


    def handle(self, *args, **options):
        if not options['cv_list']:
            raise CommandError('cv list must be specified.')
        import os.path
        if not (os.path.exists(options['cv_list']) and os.path.isfile(options['cv_list'])):
            raise CommandError('cv list %s is not an legal file.' % (options['cv_list'],))

        import codecs
        with open(options['cv_list'], 'rb') as rawf:
            raw = rawf.read(4)
            if raw.startswith(codecs.BOM_UTF8):
                encoding = 'utf-8-sig'
            else:
                encoding = 'utf-8'


        with open(options['cv_list'], 'r', encoding=encoding) as f:
            transaction.set_autocommit(False)
            try:
                self.cvimport(f.readlines())
                transaction.commit()
            except Exception as e:
                fail_print(str(e))
                transaction.rollback()

