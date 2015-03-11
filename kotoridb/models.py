from django.db import models

# Create your models here.
"""
class Translation(models.Model):
    name = models.CharField(max_length=128, db_index=True)
"""

class Studio(models.Model):

    def __str__(self):
        return self.name

    name = models.CharField(max_length=128, default='studio', db_index=True)
    #translations = models.ManyToManyField(Translation, blank=True)
    translations = models.CharField(max_length=128, blank=True, default='', db_index=True)

class Anime(models.Model):

    def __str__(self):
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

class OnAirInfo(models.Model):

    def __str__(self):
        return self.tv_station+'|'+str(self.time)

    tv_station = models.CharField(max_length=128, default='tv_station')
    time = models.DateTimeField(blank=True, null=True, default=None)
    link = models.URLField(max_length=256, blank=True, default='')
    anime = models.ForeignKey(Anime)

