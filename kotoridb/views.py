from django.http import HttpResponse
from django.shortcuts import render
from kotoridb.models import Anime
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

def on_air_time_show(t):
    TZ = pytz.timezone('Asia/Shanghai')
    t = t.astimezone(TZ)

    if int(t.strftime('%H')) <= 4:
        h = 24+int(t.strftime('%H'))
        tt = t - datetime.timedelta(days=1)
        return (int(tt.strftime('%w')), str(h)+tt.strftime(':%M, %a, %Y-%m-%d'))
    else:
        return (int(t.strftime('%w')), t.strftime('%H:%M, %a, %Y-%m-%d'))

def on_air(request):

    now = timezone.now()
    td_before = datetime.timedelta(weeks=4)
    animes = Anime.objects.filter(on_air_time__lte=now+td_before).order_by('on_air_time')
    on_air_animes = {w:[] for w in range(7)}
    for a in animes:
        end_time = a.on_air_time + datetime.timedelta(weeks=a.on_air_weeks)
        if end_time > now:
            w, a.on_air_time_show = on_air_time_show(a.on_air_time)
            a.dom_on_air_time_show = on_air_time_show(a.dom_on_air_time) if a.dom_on_air_time else None
            on_air_animes[w].append(a)

    context = nav_context()
    context['animes'] = on_air_animes
    context['time_now'] = now

    timezone.activate(pytz.timezone('Asia/Shanghai'))
    return render(request, 'kotoridb/on_air.html', context)
    #return HttpResponse(str(on_air_animes))

# Create your views here.
def index(request):
    context = nav_context()
    return render(request, 'kotoridb/index.html', context)
