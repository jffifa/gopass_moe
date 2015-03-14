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

def on_air_time_show(t):
    TZ = pytz.timezone('Asia/Shanghai')
    t = t.astimezone(TZ)

    if int(t.strftime('%H')) <= 4:
        h = 24+int(t.strftime('%H'))
        tt = t - datetime.timedelta(days=1)
        return (int(tt.strftime('%w')), str(h)+tt.strftime(':%M, %a'), tt.strftime('%Y-%m-%d'))
    else:
        return (int(t.strftime('%w')), t.strftime('%H:%M, %a'), t.strftime('%Y-%m-%d'))

def on_air(request):

    now = timezone.now()
    td_before = datetime.timedelta(weeks=4)
    on_airs = OnAir.objects.filter(time__lte=now+td_before).select_related('anime').order_by('time')
    animes = {}
    for oa in on_airs:
        if oa.type==OnAir._TYPE_FIRSTHAND and \
            oa.time and \
            oa.time+datetime.timedelta(weeks=oa.anime.on_air_weeks)>now:
            animes[oa.anime.id] = oa.anime
            animes[oa.anime.id].on_air = oa
        elif oa.type == OnAir._TYPE_DOM and oa.anime.id in animes:
            animes[oa.anime.id].dom_on_air = oa

    on_air_animes = {w:[] for w in range(7)}
    for i, a in animes.items():
        w, a.on_air_time_show, a.on_air_date_show = on_air_time_show(a.on_air.time)
        a.dom_on_air_time_show = on_air_time_show(a.dom_on_air.time)[1] if hasattr(a,'dom_on_air_time') else None
        a.studio = ', '.join([str(s) for s in a.studios.all()])
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
