# -*- coding: utf-8 -*-
from django.db import models
from kotoridb import utils

# Create your models here.
"""
class Translation(models.Model):
    name = models.CharField(max_length=128, db_index=True)
"""

class Studio(models.Model):
    class Meta:
        verbose_name = '制作公司'

    def __str__(self):
        if self.alias:
            return '%s(%s)' % (self.name, self.alias)
        else:
            return self.name

    name = models.CharField(max_length=128, default='studio', db_index=True)
    alias = models.CharField(max_length=128, blank=True, default='', db_index=True, verbose_name='译名')

class Anime(models.Model):
    class Meta:
        verbose_name = '动画'

    def __str__(self):
        if self.alias:
            return '%s(%s)' % (self.title, self.alias)
        else:
            return self.title


    title = models.CharField(max_length=128, default='title', db_index=True, verbose_name='标题')
    alias = models.CharField(max_length=128, blank=True, default='', db_index=True, verbose_name='译名')
    homepage = models.URLField(max_length=256, blank=True, default='', verbose_name='主页')
    on_air_tv = models.CharField(max_length=128, default='', verbose_name='最速放送')
    on_air_time = models.DateTimeField(blank=True, null=True, default=None, verbose_name='放送时间')
    on_air_weeks = models.IntegerField(default=1024, verbose_name='播出时长(周)')
    on_air_link = models.URLField(max_length=256, blank=True, default='', verbose_name='放送链接')
    dom_on_air_tv = models.CharField(max_length=128, blank=True, default='', verbose_name='国内放送')
    dom_on_air_time = models.DateTimeField(blank=True, null=True, default=None, verbose_name='国内放送时间')
    dom_on_air_link = models.URLField(max_length=256, blank=True, default='', verbose_name='国内放送链接')
    episodes = models.IntegerField(default=13, verbose_name='话数')
    image = models.ImageField(upload_to='images/anime/cover', max_length=256, blank=True, verbose_name='封面')
    studio = models.ForeignKey(Studio, blank=True, null=True, default=None, verbose_name='制作公司') # TODO: manytomany
    studios = models.ManyToManyField(Studio, blank=True, verbose_name='制作公司')
    comment = models.TextField(blank=True, default='', verbose_name='备注')

    staffs = models.ManyToManyField(Person, through='Staff', through_fields=('anime', 'person'))
    cvs = models.ManyToManyField(Person, through='AnimeCharacter', through_fields=('anime', 'cv'))

    def save(self, *args, **kwargs):
        if not self.dom_on_air_tv and self.dom_on_air_link:
            self.dom_on_air_tv = utils.guess_tv_name(self.dom_on_air_link)
        super(Anime, self).save(*args, **kwargs)

class OnAirInfo(models.Model):

    def __str__(self):
        return self.tv_station+'/'+str(self.time)

    tv_station = models.CharField(max_length=128, blank=True, default='')
    time = models.DateTimeField(blank=True, null=True, default=None)
    link = models.URLField(max_length=256, blank=True, default='')
    anime = models.ForeignKey(Anime)

    def save(self, *args, **kwargs):
        if not self.tv_station and self.link:
            self.tv_station = utils.guess_tv_name(self.link)
        super(OnAirInfo, self).save(*args, **kwargs)

class OnAir(models.Model):
    class Meta:
        verbose_name = '放送信息'

    def __str__(self):
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

    type = models.IntegerField(choices=_TYPE_CHOICES, default=_TYPE_EXTRA)
    tv = models.CharField(max_length=128, blank=True, default='')
    time = models.DateTimeField(blank=True, null=True, default=None)
    link = models.URLField(max_length=256, blank=True, default='')
    anime = models.ForeignKey(Anime)

class Character(models.Model):
    class Meta:
        abstract = True

    name = models.CharField(max_length=128, db_index=True)
    alias = models.CharField(max_length=128, db_index=True, blank=True, default='')

class AnimeCharacter(Character):
    class Meta:
        verbose_name = '动画角色'

    def __str__(self):
        if self.cv:
            return '%s-%s(%s)' % (self.name, self.cv.name, self.anime.title)
        else:
            return '%s(%s)' % (self.name, self.anime.title)

    cv = models.ForeignKey(Person, blank=True, null=True, default=None)
    anime = models.ForeignKey(Anime)

class Person(models.Model):
    def __str__(self):
        return self.name

    name = models.CharField(max_length=128, db_index=True)
    alias = models.CharField(max_length=128, db_index=True, blank=True, default='')
    image = models.ImageField(upload_to='images/person', max_length=256, blank=True)

class Staff(models.Model):
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

    def __str__(self):
        return Staff._TITLES[self.title-1][1]+':'+self.person.name

    title = models.IntegerField(db_index=True, choices=_TITLES)
    person = models.ForeignKey(Person)
    #alias = models.CharField(max_length=128, blank=True)
    anime = models.ForeignKey(Anime)

