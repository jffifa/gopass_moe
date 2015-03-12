import autocomplete_light
from models import Person

autocomplete_light.register(Studio,
    search_fields=['^name', '^translations'],
    attrs={
        'data-autocomplete-minimum-characters':2,
    },
    widget_attrs={
        'data-widget-maximum-values':4,
    }
)
