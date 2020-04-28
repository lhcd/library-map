from datetime import datetime
from nypl_map.models import Library, Location, Hour, Alert

DAYS_MAP = {
    'sun.':0,
    'mon.':1,
    'tue.':2,
    'wed.':3,
    'thu.':4,
    'fri.':5,
    'sat.':6
}

def _time_string_to_timestamp(time: str):
    try:
        return datetime.strptime(time, '%H:%M')
    except (ValueError, TypeError):
        return None

def _date_time_string_to_datetime(date_time: str):
    try:
        return datetime.strptime(date_time, '%Y-%m-%dT%H:%M:%S%z')
    except (ValueError, TypeError) as e:
        return None

def api_geolocation_to_orm_location(geolocation: dict, library: Library) -> Location:
    if 'type' not in geolocation or geolocation.get('type') != 'Point':
        raise KeyError('Type is not point in {}'.format(geolocation))
    if 'coordinates' not in geolocation or len(geolocation['coordinates']) != 2:
        raise KeyError('Location coordinates are not a lat/long pair in {}'.format(geolocation))

    return Location(
        library=library,
        latitude=float(geolocation['coordinates'][0]),
        longitude=float(geolocation['coordinates'][1])
    )

def api_hours_to_orm_hours(interval: dict, library: Library) -> Hour:
    try:
        day = DAYS_MAP[interval['day'].lower()]
    except KeyError:
        raise KeyError('No matching day found in {}'.format(interval))

    return Hour(
        library=library,
        day=day,
        open_time=_time_string_to_timestamp(interval.get('open')),
        close_time=_time_string_to_timestamp(interval.get('close'))
    )

def api_alert_to_orm_alert(alert: dict, library: Library) -> Alert:
    link = alert.get('_links', {}).get('web', {}).get('href', '')
    period_dict = alert.get('applies', alert.get('display', {}))

    return Alert(
        library=library,
        message=alert.get('msg', ''),
        hyperlink=link,
        closure_reason=alert.get('closed_for', ''),
        is_closed=(True if 'closed_for' in alert else False),
        period_start=_date_time_string_to_datetime(period_dict.get('start')),
        period_end=_date_time_string_to_datetime(period_dict.get('end'))
    )

def api_library_to_orm_library(
    library: dict
) -> Library:
    if 'id' not in library:
        raise KeyError('Missing domain ID from library: {}'.format(library))

    library_object = Library.get_or_update_by_nypl_id(
        Library(
            nypl_id=library.get('id'),
            name=library.get('name', ''),
            about_text=library.get('about', ''),
            cross_street=library.get('cross_street', ''),
            street_address=library.get('street_address', '')
        )
    )

    # Wipe existing associated info
    library_object.hour_set.all().delete()
    library_object.alert_set.all().delete()
    library_object.location_set.all().delete()

    hours = Hour.objects.bulk_create([
        api_hours_to_orm_hours(hour, library_object)
        for hour in library.get('hours', {}).get('regular', {})
    ])
    alerts = Alert.objects.bulk_create([
        api_alert_to_orm_alert(alert, library_object)
        for alert in library.get('_embedded', {}).get('alerts', {})
    ])
    location = api_geolocation_to_orm_location(library.get('geolocation', {}), library_object).save()

    return library_object
