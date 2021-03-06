# coding=utf-8
from __future__ import unicode_literals, print_function, absolute_import

from django.contrib import admin
from kotoridb.models import Anime, Studio, Staff, Person, OnAir, AnimeCharacter
from autocomplete_light import shortcuts as autocomplete_light
from django.utils import timezone

class AnimeStaffInline(admin.StackedInline):
    form = autocomplete_light.modelform_factory(Staff, fields='__all__')
    model= Staff
    extra= 0

class AnimeCharacterInline(admin.StackedInline):
    form = autocomplete_light.modelform_factory(AnimeCharacter, fields='__all__')
    model = AnimeCharacter
    extra = 0

class OnAirInline(admin.StackedInline):
    form = autocomplete_light.modelform_factory(OnAir, fields='__all__')
    model = OnAir
    extra = 0

class AnimeAdmin(admin.ModelAdmin):
    form = autocomplete_light.modelform_factory(Anime, fields='__all__')

    list_display = (
        'title',
        'alias',
        'display_studios',
        'display_onair',
    )
    inlines = [OnAirInline, AnimeStaffInline, AnimeCharacterInline]
    search_fields = ['title', 'alias']

    def display_studios(self, obj):
        return ', '.join(map(lambda x:x.name, obj.studios.all()))
    display_studios.short_description = '制作公司'

    def display_onair(self, obj):
        try:
            oa = obj.onair_set.get(type=1)
            if oa.time:
                return oa.tv+' / '+oa.time.astimezone(timezone.get_current_timezone()).strftime('%H:%M:%S, %a, %Y-%m-%d')
            else:
                return oa.tv
        except:
            return ''
    display_onair.short_description = '最速放送'

class StudioAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'alias',
    )

class StaffAdmin(admin.ModelAdmin):
    form = autocomplete_light.modelform_factory(Staff, fields='__all__')

class PersonAdmin(admin.ModelAdmin):
    form = autocomplete_light.modelform_factory(Person, fields='__all__')

# Register your models here.
admin.site.register(Anime, AnimeAdmin)
admin.site.register(Studio, StudioAdmin)
admin.site.register(Staff, StaffAdmin)
admin.site.register(Person, PersonAdmin)
admin.site.register(OnAir)
