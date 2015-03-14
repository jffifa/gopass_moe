# -*- coding: utf-8 -*-
from django.db import models
from kotoridb import utils

# Create your models here.

class Studio(models.Model):
    class Meta:
        verbose_name = '制作公司'
        verbose_name_plural = '制作公司'

    def __str__(self):
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

    def __str__(self):
        return self.name

    name = models.CharField(max_length=128, db_index=True, verbose_name='名字')
    alias = models.CharField(max_length=128, db_index=True, blank=True, default='', verbose_name='译名')
    image = models.ImageField(upload_to='images/person', max_length=256, blank=True, verbose_name='肖像')

class Anime(models.Model):
    class Meta:
        verbose_name = '动画'
        verbose_name_plural = '动画'

    def __str__(self):
        if self.alias:
            return '%s(%s)' % (self.title, self.alias)
        else:
            return self.title


    title = models.CharField(max_length=128, default='title', db_index=True, verbose_name='标题')
    alias = models.CharField(max_length=128, blank=True, default='', db_index=True, verbose_name='译名')
    homepage = models.URLField(max_length=256, blank=True, default='', verbose_name='主页')
    on_air_weeks = models.IntegerField(default=1024, verbose_name='播出时长(周)')
    episodes = models.IntegerField(default=13, verbose_name='话数')
    image = models.ImageField(upload_to='images/anime/cover', max_length=256, blank=True, verbose_name='封面')
    studios = models.ManyToManyField(Studio, blank=True, verbose_name='制作公司')
    comment = models.TextField(blank=True, default='', verbose_name='备注')

    staffs = models.ManyToManyField(Person, through='Staff', through_fields=('anime', 'person'), related_name='anime_staffs')
    cvs = models.ManyToManyField(Person, through='AnimeCharacter', through_fields=('anime', 'cv'), related_name='anime_cvs')

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

    type = models.IntegerField(choices=_TYPE_CHOICES, default=_TYPE_EXTRA, verbose_name='放送类型')
    tv = models.CharField(max_length=128, blank=True, default='', verbose_name='电视台')
    time = models.DateTimeField(blank=True, null=True, default=None, verbose_name='放送时间')
    link = models.URLField(max_length=256, blank=True, default='', verbose_name='放送链接')
    anime = models.ForeignKey(Anime)

    def save(self, *args, **kwargs):
        if not self.tv and self.link:
            self.tv = utils.guess_tv_name(self.link)
        super(OnAirInfo, self).save(*args, **kwargs)

class Character(models.Model):
    class Meta:
        abstract = True

    name = models.CharField(max_length=128, db_index=True, verbose_name='角色名字')
    alias = models.CharField(max_length=128, db_index=True, blank=True, default='', verbose_name='译名')

class AnimeCharacter(Character):
    class Meta:
        verbose_name = '动画角色'
        verbose_name_plural = '动画角色'

    def __str__(self):
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

    title = models.IntegerField(db_index=True, choices=_TITLES, verbose_name='职位')
    person = models.ForeignKey(Person, verbose_name='人名')
    anime = models.ForeignKey(Anime, verbose_name='动画')

