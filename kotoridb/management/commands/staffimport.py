# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.db import transaction
from kotoridb.models import Anime, Person, Staff
from .color_print import warn_print, info_print, fail_print
from .utils import deal_str, split_str
import re

class Command(BaseCommand):
    args = ''
    help = 'imports staff list.'

    from optparse import make_option
    option_list = BaseCommand.option_list + (
        make_option('-l', '--staff-list', dest='staff_list', help='staff list file', metavar='STAFF_LIST'),
    )

    PLACE_TRANS = {
        '原作':['原作','著者'],
        '漫画':'漫画',
        '原作插画':'原作イラスト',
        '原案':'原案',
        'Guest Character Design':'ゲストキャラクターデザイン',
        'Design Works':'デザインワークス',
        '系列构成':'シリーズ構成',
        '系列演出':'シリーズ演出',
        '翻译':'翻訳',
        'Series Director':'シリーズディレクター',
        '总监督':'総監督',
        '监督':'監督',
        '总作画监督':'総作画監督',
        '人物总作监':'キャラクター総作画監督',
        '怪物总作监':'クリーチャー総作画監督',
        '作画监督':'作画監督',
        '效果作画监督':'エフェクト作画監督',
        'Visual Effect':'ビジュアルエフェクト',
        '动作作画监督':'アクション作画監督',
        'Animation Director':'アニメーションディレクター',
        '监修':'スーパーバイザー',
        '脚本':'脚本',
        '主要人物设计':'チーフキャラクターデザイン',
        '人物设计':[
            'キャラクターデザイン',
            'キャラデザイン',
            'キャラクターデザイナー',
            'メインキャラクターデザイン'],
        '人物原案':[
            'キャラクターデザイン原案',
            'キャラクター原案',
            'キャラ原案'],
        '机械设计':[
            'メカニックデザイン',
            'メカデザイン',
            'メカニカルデザイン'],
        '怪物设定':[
            'クリーチャー設定',
            'クリーチャーデザイン',],
        '概念设定':[
            'コンセプト',
            'コンセプトデザイン'],
        '色彩设计':'色彩設計',
        '平面设计':'グラフィックデザイナー',
        '美术':'美術',
        '美术设定':'美術設定',
        '美术监督':'美術監督',
        '美术指导':'プロダクションデザイナー',
        '摄影监督':'撮影監督',
        '动作监督':'アクション監督',
        '动作监修':'アクション監修',
        '编集':'編集',
        '音响监督':'音響監督',
        '音响制作':[
                '音響製作',
                '音響制作',],
        '音响效果':'音響効果',
        '音乐':'音楽',
        '音乐制作':[
                '音楽プロデュース',
                '音楽制作'],
        '主要脚本':'メインライター',
        'CG导演':'CGディレクター',
        'CG监修':'CGスーパーバイザー',
        '背景':'背景',
        '背景设计':'背景デザイン',
        '背景监督':'背景監督',
        '标志设计':'ロゴデザイン',
        '制作':'プロデュース',
        '剪辑':'映像編集',
        '次要人物设计':'サブキャラクター',
        '道具设计':'プロップデザイン',
        '主要原画':[
                'メインアニメーター',
                'チーフアニメーター',
                'キーアニメーター',],
        '3D监督':'3D監督',
        '2D Works':'2Dワークス',
        'Modeling Director':'モデリングディレクター',
        '演出':'演出',
        '宠物设计':'ペットデザイン',
        '图形用户界面设计':'モニターデザイン',
        'Image Board':'イメージボード',
        'Concept Artist':'コンセプトアーティスト',
        'Lingerie Design':'ランジェリーデザイン',
    }

        

    def staffimport(self, lines):
        # get reverse dict for PLACE_TRANS
        self.PLACE_TRANS_REV = {}
        for trans, org in self.PLACE_TRANS.items():
            if type(org) is list:
                for o in org:
                    self.PLACE_TRANS_REV[o] = trans
            else:
                self.PLACE_TRANS_REV[org] = trans

        anime = None
        staffs = None
        for line in lines:
            line = line.strip()
            if not line:
                continue

            # anime name
            if line[0] == '*':
                anime_name = line[1:].strip()
                anime = None
                try:
                    anime = Anime.objects.get(title=anime_name)
                except ObjectDoesNotExist:
                    try:
                        anime = Anime.objects.get(alias=anime_name)
                    except ObjectDoesNotExist:
                        warn_print('anime [%s] not found, ignored' % (anime_name,))
                        continue
                staffs = anime.staff_set.all()
                continue

            if not anime:
                continue

            # split keys and values
            try:
                places, names = re.sub(r'( ){2,}', r'|', line, 1).split('|')
            except ValueError:
                warn_print('failed to unpack %s for anime %s, ignored' % (line, anime.title))
                continue

            # split keys by delimiter
            place_delimiter = '/／&＆・、'
            places = list(map(lambda x:deal_str(x,False), split_str(places, place_delimiter)))
            # split values by delimiter
            name_delimiter = '/／&＆、'
            names = list(map(deal_str, split_str(names, name_delimiter)))

            if not places or not names:
                continue

            for name in names:
                try:
                    p = Person.objects.get(name=name)
                except MultipleObjectsReturned:
                    warn_print('multiple person named [%s] exist, ignore for anime [%s] with place [%s]' % (name,anime.title,place))
                    continue
                except ObjectDoesNotExist:
                    try:
                        p = Person.objects.get(alias=name)
                    except MultipleObjectsReturned:
                        warn_print('multiple person aliased [%s] exist, ignore for anime [%s] with place [%s]' % (name,anime.title,place))
                        continue
                    except ObjectDoesNotExist: # not exists, create one
                        p = Person(name=name)
                        p.save()
                        info_print('create a new person named [%s]' % (name,))

                for place in places:
                    if place in self.PLACE_TRANS_REV:
                        place = self.PLACE_TRANS_REV[place]

                    try:
                        s = staffs.get(place=place, person=p)
                    except ObjectDoesNotExist:
                        s = Staff(place=place, anime=anime, person=p)
                        s.save()
                        info_print('create a new staff with place [%s] and name [%s] for anime [%s]' % (place,name,anime.title))

                    info_print('import staff [%s-%s], for anime [%s] succeeded' % (
                        place, name, anime.title))


    def handle(self, *args, **options):
        if not options['staff_list']:
            raise CommandError('staff list must be specified.')
        import os.path
        if not (os.path.exists(options['staff_list']) and os.path.isfile(options['staff_list'])):
            raise CommandError('staff list %s is not an legal file.' % (options['staff_list'],))

        import codecs
        with open(options['staff_list'], 'rb') as rawf:
            raw = rawf.read(4)
            if raw.startswith(codecs.BOM_UTF8):
                encoding = 'utf-8-sig'
            else:
                encoding = 'utf-8'


        with open(options['staff_list'], 'r', encoding=encoding) as f:
            transaction.set_autocommit(False)
            try:
                self.staffimport(f.readlines())
                transaction.commit()
            except Exception as e:
                fail_print(str(e))
                transaction.rollback()

