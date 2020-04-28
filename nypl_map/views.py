from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, Http404
from django.db.models import Prefetch
from django.shortcuts import render

from datetime import datetime
import json

from .models import Library, Alert, Hour, Location

def index(request):
    return map(request)

def library(request, library_id):
    try:
        library = Library.objects.get(pk=library_id)
    except Library.DoesNotExist:
        raise Http404("Library does not exist")
    return HttpResponse(library)

def map(request):
    return render(request, 'index.html')

def nyc_geo_json(request):
    with open('/static/Borough Boundaries.geojson', 'r') as f:
        return JsonResponse(json.load(f))

# TODO: Move to mappers
def library_map_data(request):
    library_objects = Library.objects.all().prefetch_related(
        Prefetch('location_set', queryset=Location.objects.all()),
        Prefetch('hour_set', queryset=Hour.objects.filter(
            day=datetime.today().weekday()
        )),
        Prefetch('alert_set', queryset=Alert.objects.filter(
            period_start__lt=datetime.now(),
            period_end__gt=datetime.now()
        ))
    )
    libraries = {
        library.id: {
            'latitude': library.location_set.get().latitude,
            'longitude': library.location_set.get().longitude,

            'name': library.name,
            'about_text': library.about_text,
            'cross_street': library.cross_street,
            'street_address': library.street_address,

            'is_open': library.is_open(),
            'would_be_open': library.would_be_open(),

            'opening': (
                library.hour_set.all()[0].open_time.strftime('%H:%M')
                if (library.hour_set.all() and library.hour_set.all()[0].open_time is not None)
                else None
            ),
            'closing': (
                library.hour_set.all()[0].close_time.strftime('%H:%M')
                if (library.hour_set.all() and library.hour_set.all()[0].close_time is not None)
                else None
            ),

            'alerts': [
                {
                    'message': alert.message,
                    'closure_reason': alert.closure_reason,
                    'is_closed': alert.is_closed,
                    'period_start': alert.period_start.strftime('%y-%d-%m %H:%M'),
                    'period_end': alert.period_end.strftime('%y-%d-%m %H:%M'),
                    'link': alert.hyperlink
                }
                for alert in library.alert_set.all()
            ]

        }
        for library in library_objects
    }
    return JsonResponse(libraries)
