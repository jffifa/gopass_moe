from django.contrib import admin
from kotoridb.models import Anime, OnAirInfo, Studio
import autocomplete_light

class AnimeOnAirInline(admin.TabularInline):
    model=OnAirInfo
    extra=0

class AnimeAdmin(admin.ModelAdmin):
    form = autocomplete_light.modelform_factory(Anime)

    list_display = (
        'title',
        'translations',
        'studio',
        'on_air_tv',
        'on_air_time',
        'on_air_weeks',
        'dom_on_air_tv',
        'dom_on_air_time',
        'dom_on_air_link',
    )
    inlines = [AnimeOnAirInline]
    search_fields = ['^title', '^translations', 'studio__name']

class StudioAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'translations',
    )

# Register your models here.
admin.site.register(Anime, AnimeAdmin)
admin.site.register(Studio, StudioAdmin)
