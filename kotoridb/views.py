from django.http import HttpResponse
from django.shortcuts import render
from kotoridb.models import Anime, OnAir
import pytz
from django.utils import timezone
import datetime

def nav_context():
    now = timezone.now()
    now_year = int(now.strftime('%Y'))
    year_list = list(range(now_year-4,now_year+1))
    year_list.reverse()
    nav_context = {'nav_context':{
        'bangumi':{
            'finished_years':year_list,
        },
    }}
    return nav_context

def on_air(request):

    now = timezone.now()
    td_before = datetime.timedelta(weeks=4)
    on_airs = OnAir.objects.filter(time__lte=now+td_before, type=OnAir._TYPE_FIRSTHAND).select_related('anime').order_by('time')
    animes = []
    for oa in on_airs:
        if oa.time and oa.time+datetime.timedelta(weeks=oa.anime.on_air_weeks)>now:
            a = oa.anime
            a.on_air = oa
            try:
                a.dom_on_air = a.onair_set.get(type=OnAir._TYPE_DOM)
            except:
                pass
            a.extra_on_air = a.onair_set.filter(type=OnAir._TYPE_EXTRA)
            animes.append(oa.anime)

    for a in animes:
        a.studio = ', '.join([str(s) for s in a.studios.all()])
        a.staff_list = [{
            'place':s.place,
            'staff':s.person.name
            } for s in a.staff_set.select_related('person').all()]
        # ATTENTION: need to be in order
        a.staff_dict = {}
        for s in a.staff_list:
            if s['place'] in a.staff_dict:
                a.staff_dict[s['place']][1].append(s['staff'])
            else:
                a.staff_dict[s['place']] = (len(a.staff_dict), [s['staff']])
        a.staff_dict = sorted(a.staff_dict.items(), key=lambda x: x[1][0])
        a.staff_dict = [(k, v[1]) for k, v in a.staff_dict]
        import json
        a.staff_dict = json.dumps(a.staff_dict)

        a.cv_list = [{
            'character':c.name,
            'cv':c.cv.name
            } for c in a.animecharacter_set.select_related('cv').all()]

    context = nav_context()
    context['animes'] = animes
    context['time_now'] = now

    #timezone.activate(pytz.timezone('UTC'))
    return render(request, 'kotoridb/on_air.html', context)
    #return HttpResponse(str(on_air_animes))

# Create your views here.
def index(request):
    context = nav_context()
    return render(request, 'kotoridb/index.html', context)
