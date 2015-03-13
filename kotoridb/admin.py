from django.contrib import admin
from kotoridb.models import Anime, OnAirInfo, Studio, Staff, CharacterVoice, Person, Character
import autocomplete_light

class AnimeOnAirInline(admin.TabularInline):
    model=OnAirInfo
    extra=0

class AnimeStaffInline(admin.TabularInline):
    form = autocomplete_light.modelform_factory(Staff)
    model=Staff
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
    inlines = [AnimeOnAirInline, AnimeStaffInline]
    search_fields = ['^title', '^translations', 'studio__name']

class StudioAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'translations',
    )

class StaffAdmin(admin.ModelAdmin):
    form = autocomplete_light.modelform_factory(Staff)

class PersonAdmin(admin.ModelAdmin):
    form = autocomplete_light.modelform_factory(Person)

# Register your models here.
admin.site.register(Anime, AnimeAdmin)
admin.site.register(Studio, StudioAdmin)
admin.site.register(Staff, StaffAdmin)
admin.site.register(Person, PersonAdmin)
