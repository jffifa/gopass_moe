# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

from django.db import models
from kotoridb import utils

# Create your models here.


class Studio(models.Model):
    class Meta:
        verbose_name = '制作公司'
        verbose_name_plural = '制作公司'

    def __unicode__(self):
        if self.alias:
            return '%s(%s)' % (self.name, self.alias)
        else:
            return self.name

    name = models.CharField(max_length=128, default='studio', db_index=True, verbose_name='名字')
    alias = models.CharField(max_length=128, blank=True, default='', db_index=True, verbose_name='译名')


class Person(models.Model):
    class Meta:
        verbose_name = '人物'
        verbose_name_plural = '人物'

    def __unicode__(self):
        return self.name

    name = models.CharField(max_length=128, db_index=True, verbose_name='名字')
    alias = models.CharField(max_length=128, db_index=True, blank=True, default='', verbose_name='译名')
    image = models.ImageField(upload_to='images/person', max_length=256, blank=True, verbose_name='肖像')


class Anime(models.Model):
    class Meta:
        verbose_name = '动画'
        verbose_name_plural = '动画'

    def __unicode__(self):
        if self.alias:
            return '%s(%s)' % (self.title, self.alias)
        else:
            return self.title

    title = models.CharField(max_length=128, default='title', db_index=True, verbose_name='标题')
    alias = models.CharField(max_length=128, blank=True, default='', db_index=True, verbose_name='译名')
    homepage = models.URLField(max_length=256, blank=True, default='', verbose_name='主页')
    on_air_weeks = models.IntegerField(default=1024, verbose_name='播出时长(周)')
    episodes = models.IntegerField(default=0, verbose_name='话数')
    image = models.ImageField(upload_to='images/anime/cover', max_length=256, blank=True, verbose_name='封面')
    studios = models.ManyToManyField(Studio, blank=True, verbose_name='制作公司')
    comment = models.TextField(blank=True, default='', verbose_name='备注')

    staffs = models.ManyToManyField(Person, through='Staff', through_fields=('anime', 'person'), related_name='anime_staffs')
    cvs = models.ManyToManyField(Person, through='AnimeCharacter', through_fields=('anime', 'cv'), related_name='anime_cvs')


class OnAir(models.Model):
    class Meta:
        verbose_name = '放送信息'
        verbose_name_plural = '放送信息'

    def __unicode__(self):
        if self.time:
            return self.tv+'/'+str(self.time)
        else:
            return self.tv

    _TYPE_FIRSTHAND = 1
    _TYPE_DOM = 2
    _TYPE_EXTRA = 3

    _TYPE_CHOICES = (
        (_TYPE_FIRSTHAND, '最速放送'),
        (_TYPE_DOM, '国内官方'),
        (_TYPE_EXTRA, '其他'),
    )

    type = models.IntegerField(choices=_TYPE_CHOICES, default=_TYPE_EXTRA, verbose_name='放送类型')
    tv = models.CharField(max_length=128, blank=True, default='', verbose_name='电视台')
    time = models.DateTimeField(blank=True, null=True, default=None, db_index=True, verbose_name='放送时间')
    link = models.URLField(max_length=256, blank=True, default='', verbose_name='放送链接')
    anime = models.ForeignKey(Anime)

    def save(self, *args, **kwargs):
        if not self.tv and self.link:
            self.tv = utils.guess_tv_name(self.link)
        super(OnAir, self).save(*args, **kwargs)


class Character(models.Model):
    class Meta:
        abstract = True

    name = models.CharField(max_length=128, db_index=True, verbose_name='角色名字')
    alias = models.CharField(max_length=128, db_index=True, blank=True, default='', verbose_name='译名')


class AnimeCharacter(Character):
    class Meta:
        verbose_name = '动画角色'
        verbose_name_plural = '动画角色'

    def __unicode__(self):
        if self.cv:
            return '%s-%s(%s)' % (self.name, self.cv.name, self.anime.title)
        else:
            return '%s(%s)' % (self.name, self.anime.title)

    cv = models.ForeignKey(Person, blank=True, null=True, default=None)
    anime = models.ForeignKey(Anime)


class Staff(models.Model):
    class Meta:
        verbose_name = '制作人员'
        verbose_name_plural = '制作人员'

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

    _TITLES = (
        (1,'原作',),
        (2,'监督',),
        (3,'系列构成',),
        (4,'脚本',),
        (5,'音乐',),
        (6,'音响监督',),
        (7,'摄影监督',),
        (8,'演出',),
        (9,'总作画监督',),
        (10,'作画监督',),
        (11,'分镜',),
        (12,'色彩设定',),
        (13,'制作进行',),
        (14,'美术监督',),
        (15,'人物设定',),
    )

    def __unicode__(self):
        return '%s:%s' % (self.place, self.person.name)

    place = models.CharField(max_length=32, db_index=True, default='', verbose_name='职位')
    person = models.ForeignKey(Person, verbose_name='人名')
    anime = models.ForeignKey(Anime, verbose_name='动画')

    @classmethod
    def get_place_trans(cls):
        # get reverse dict for PLACE_TRANS
        place_trans = {}
        for trans, org in cls.PLACE_TRANS.items():
            if type(org) is list:
                for o in org:
                    place_trans[o] = trans
            else:
                place_trans[org] = trans
        return place_trans
