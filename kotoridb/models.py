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
            return '%s(%s)' % (self.title, self.translations)
        else:
            return self.title

    name = models.CharField(max_length=128, default='studio', db_index=True)
    #translations = models.ManyToManyField(Translation, blank=True)
    translations = models.CharField(max_length=128, blank=True, default='', db_index=True)

class Anime(models.Model):

    def __str__(self):
        if self.translations:
            return '%s(%s)' % (self.title, self.translations)
        else:
            return self.title


    title = models.CharField(max_length=128, default='title', db_index=True)
    translations = models.CharField(max_length=128, blank=True, default='', db_index=True)
    #translations = models.ManyToManyField(Translation, blank=True)
    homepage = models.URLField(max_length=256, blank=True, default='')
    on_air_tv = models.CharField(max_length=128, default='')
    on_air_time = models.DateTimeField(blank=True, null=True, default=None)
    on_air_weeks = models.IntegerField(default=1024)
    on_air_link = models.URLField(max_length=256, blank=True, default='')
    dom_on_air_tv = models.CharField(max_length=128, blank=True, default='')
    dom_on_air_time = models.DateTimeField(blank=True, null=True, default=None)
    dom_on_air_link = models.URLField(max_length=256, blank=True, default='')
    episodes = models.IntegerField(default=13)
    #on_air = models.ForeignKey(OnAirInfo, blank=True, null=True, default=None, related_name='anime_set')
    #on_air_domestic = models.ForeignKey(OnAirInfo, blank=True, null=True, default=None, related_name='anime_domestic_set')
    #on_air_ext = models.ManyToManyField(OnAirInfo, blank=True, related_name='anime_ext_set')
    image = models.ImageField(upload_to='images/anime/cover', max_length=256, blank=True)
    studio = models.ForeignKey(Studio, blank=True, null=True, default=None)
    comment = models.TextField(blank=True, default='')

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

class Person(models.Model):
    def __str__(self):
        return self.name

    name = models.CharField(max_length=128, db_index=True)
    image = models.ImageField(upload_to='images/person', max_length=256, blank=True)

class Staff(models.Model):
    _TITLES = {
        (1,'原作','original'),
        (2,'监督','director'),
        (2,'系列构成','script plan'),
        (3,'脚本','script'),
        (4,'音乐','music'),
        (4,'音响监督','director of audiography'),
        (4,'摄影监督','director of photography'),
        (4,'演出','impresario'),
        (5,'总作画监督','chief animation director'),
        (5,'作画监督','animation director'),
        (5,'分镜','storyboard'),
        (5,'色彩设定','color design'),
        (5,'制作进行','production assistant'),
        (5,'美术监督','production designer'),
        (6,'人物设定','character design'),
    }

    def __str__(self):
        return self.title+':'+self.person.name

    title = models.
