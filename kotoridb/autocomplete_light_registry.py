import autocomplete_light
from kotoridb.models import Studio, Person, Anime

autocomplete_light.register(Studio,
    search_fields=['^name', '^translations'],
    attrs={
        'data-autocomplete-minimum-characters':1,
    },
    widget_attrs={
        'data-widget-maximum-values':4,
    }
)

autocomplete_light.register(Person,
    search_fields=['^name', '^alias'],
    attrs={
        'data-autocomplete-minimum-characters':1,
    },
    widget_attrs={
        'data-widget-maximum-values':4,
    }
)

autocomplete_light.register(Anime,
    search_fields=['^title', '^translations'],
    attrs={
        'data-autocomplete-minimum-characters':1,
    },
    widget_attrs={
        'data-widget-maximum-values':4,
    }
)
