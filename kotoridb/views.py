from django.http import HttpResponse
from django.shortcuts import render
from kotoridb.models import Anime
import pytz
from django.utils import timezone
import datetime

def nav_context():
    now = timezone.now()
    now_year = int(now.strftime('%Y'))
    year_list = list(range(now_year-5,now_year))
    year_list.reverse()
    nav_context = {'nav_context':{
        'bangumi':{
            'finished_years':year_list,
        },
    }}
    return nav_context

def on_air_time_show(t):
    if int(t.strftime('%H')) <= 4:
        pass
    else:
        return t.strftime('%H:%M, %')

def on_air(request):
    now = timezone.now()
    td_before = datetime.timedelta(weeks=4)
    animes = Anime.objects.filter(on_air_time__lte=now+td_before).order_by('on_air_time')
    on_air_animes = {w:[] for w in range(7)}
    for a in animes:
        end_time = a.on_air_time + datetime.timedelta(weeks=a.on_air_weeks)
        if end_time > now:
            on_air_animes[int(a.on_air_time.strftime('%w'))].append(a)

    context = nav_context()
    context['animes'] = on_air_animes
    context['time_now'] = now
    return render(request, 'kotoridb/on_air.html', context)
    #return HttpResponse(str(on_air_animes))

# Create your views here.
def index(request):
    context = nav_context()
    return render(request, 'kotoridb/index.html', context)
