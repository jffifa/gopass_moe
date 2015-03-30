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
                oad = a.onair_set.get(type=OnAir._TYPE_DOM)
                a.dom_on_air = oad
            except:
                pass
            animes.append(oa.anime)

    for a in animes:
        a.studio = ', '.join([s.name for s in a.studios.all()])
        a.staff_list = [{
            'title':s.getTitle(s.title),
            'staff':s.person.name
            } for s in a.staff_set.select_related('person').all()]
        a.cv_list = [{
            'character':c.name,
            'cv':c.cv.name
            } for c in a.animecharacter_set.select_related('cv').all()]

    context = nav_context()
    context['animes'] = animes
    context['time_now'] = now

    timezone.activate(pytz.timezone('UTC'))
    return render(request, 'kotoridb/on_air.html', context)
    #return HttpResponse(str(on_air_animes))

# Create your views here.
def index(request):
    context = nav_context()
    return render(request, 'kotoridb/index.html', context)
