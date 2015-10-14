# coding=utf-8
from __future__ import print_function, unicode_literals, absolute_import

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

class Command(BaseCommand):
    args = ''
    help = 'import anime list'

    from optparse import make_option
    option_list = BaseCommand.option_list + (
        make_option('-l', '--anime-list', dest='anime_list', help='anime list file', metavar='ANIME_LIST'),
    )

    def handle(self, *args, **options):
        if not options['anime_list']:
            raise CommandError('anime list file must be specified')
        import os.path
        if not (os.path.exists(options['anime_list']) and os.path.isfile(options['anime list'])):
            raise CommandError('anime list %s is not an legal file.' % (options['anime_list'],))

        import codecs
        with open(options['anime_list'], 'rb') as rawf:
            raw = rawf.read(4)
            if raw.startswith(codecs.BOM_UTF8):
                encoding = 'utf-8-sig'
            else:
                encoding = 'utf-8'


        with open(options['anime_list'], 'r', encoding=encoding) as f:
            transaction.set_autocommit(False)
            try:
                self.cvimport(f.readlines())
                transaction.commit()
            except Exception as e:
                fail_print(str(e))
                transaction.rollback()
