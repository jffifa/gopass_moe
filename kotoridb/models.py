# -*- coding: utf-8 -*-
from django.db import models
from kotoridb import utils

# Create your models here.
"""
class Translation(models.Model):
    name = models.CharField(max_length=128, db_index=True)
"""

class Studio(models.Model):

    def __str__(self):
        if self.translations:
            return '%s(%s)' % (self.name, self.translations)
        else:
            return self.name

    name = models.CharField(max_length=128, default='studio', db_index=True)
    translations = models.CharField(max_length=128, blank=True, default='', db_index=True)
    alias = models.CharField(max_length=128, blank=True, default='', db_index=True)

class Anime(models.Model):

    def __str__(self):
        if self.translations:
            return '%s(%s)' % (self.title, self.translations)
        else:
            return self.title


    title = models.CharField(max_length=128, default='title', db_index=True, verbose_name='标题')
    translations = models.CharField(max_length=128, blank=True, default='', db_index=True, verbose_name='译名')
    alias = models.CharField(max_length=128, blank=True, default='', db_index=True)
    homepage = models.URLField(max_length=256, blank=True, default='', verbose_name='主页')
    on_air_tv = models.CharField(max_length=128, default='', verbose_name='最速放送')
    on_air_time = models.DateTimeField(blank=True, null=True, default=None, verbose_name='放送时间')
    on_air_weeks = models.IntegerField(default=1024, verbose_name='播出时长(周)')
    on_air_link = models.URLField(max_length=256, blank=True, default='', verbose_name='放送链接')
    dom_on_air_tv = models.CharField(max_length=128, blank=True, default='', verbose_name='国内放送')
    dom_on_air_time = models.DateTimeField(blank=True, null=True, default=None, verbose_name='国内放送时间')
    dom_on_air_link = models.URLField(max_length=256, blank=True, default='', verbose_name='国内放送链接')
    episodes = models.IntegerField(default=13, verbose_name='话数')
    #on_air = models.ForeignKey(OnAirInfo, blank=True, null=True, default=None, related_name='anime_set')
    #on_air_domestic = models.ForeignKey(OnAirInfo, blank=True, null=True, default=None, related_name='anime_domestic_set')
    #on_air_ext = models.ManyToManyField(OnAirInfo, blank=True, related_name='anime_ext_set')
    image = models.ImageField(upload_to='images/anime/cover', max_length=256, blank=True, verbose_name='封面')
    studio = models.ForeignKey(Studio, blank=True, null=True, default=None, verbose_name='制作公司') # TODO: manytomany
    comment = models.TextField(blank=True, default='', verbose_name='备注')

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

class Character(models.Model):

    def __str__(self):
        return '%s(%s)' % (self.name, self.anime)

    name = models.CharField(max_length=128, db_index=True)
    alias = models.CharField(max_length=128, db_index=True, blank=True, default='')
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
        #(1,'原作','original'),
        (2,'监督',),
        #(2,'监督','director'),
        (3,'系列构成',),
        #(3,'系列构成','script plan'),
        (4,'脚本',),
        #(4,'脚本','script'),
        (5,'音乐',),
        #(5,'音乐','music'),
        (6,'音响监督',),
        #(6,'音响监督','director of audiography'),
        (7,'摄影监督',),
        #(7,'摄影监督','director of photography'),
        (8,'演出',),
        #(8,'演出','impresario'),
        (9,'总作画监督',),
        #(9,'总作画监督','chief animation director'),
        (10,'作画监督',),
        #(10,'作画监督','animation director'),
        (11,'分镜',),
        #(11,'分镜','storyboard'),
        (12,'色彩设定',),
        #(12,'色彩设定','color design'),
        (13,'制作进行',),
        #(13,'制作进行','production assistant'),
        (14,'美术监督',),
        #(14,'美术监督','production designer'),
        (15,'人物设定',),
        #(15,'人物设定','character design'),
    )

    def __str__(self):
        return Staff._TITLES[self.title-1][1]+':'+self.person.name

    title = models.IntegerField(db_index=True, choices=_TITLES)
    person = models.ForeignKey(Person)
    #alias = models.CharField(max_length=128, blank=True)
    anime = models.ForeignKey(Anime)

class CharacterVoice(models.Model):
    def __str__(self):
        return '%s-%s(%s)' % (self.character.name, self.person.name, self.character.anime.title)

    character = models.ForeignKey(Character)
    person = models.ForeignKey(Person)

