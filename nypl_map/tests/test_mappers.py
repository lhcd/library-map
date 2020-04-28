from django.test import TestCase

from datetime import datetime, timezone, timedelta
import pytz

from nypl_map.tests.factories import LibraryFactory
from nypl_map.library_updater.mappers import (
    api_geolocation_to_orm_location,
    api_hours_to_orm_hours,
    api_alert_to_orm_alert,
    api_library_to_orm_library
)

class MapperTestCase(TestCase):
    def setUp(self):
        self.library = LibraryFactory()

    def test_api_geolocation_to_orm_location(self):
        # An unrecognized coordinate type raises an appropriate error
        with self.assertRaisesRegex(KeyError, 'Type is not point in .*'):
            api_geolocation_to_orm_location({}, self.library)

        # A missing or badly formed set of coordinates raises an appropriate error
        with self.assertRaisesRegex(KeyError, 'Location coordinates are not a lat/long pair in .*'):
            api_geolocation_to_orm_location({'type': 'Point'}, self.library)
        with self.assertRaisesRegex(KeyError, 'Location coordinates are not a lat/long pair in .*'):
            api_geolocation_to_orm_location({'type': 'Point', 'coordinates': []}, self.library)
        with self.assertRaisesRegex(ValueError, 'could not convert string to float: .*'):
            api_geolocation_to_orm_location({'type': 'Point', 'coordinates': ['a', 'b']}, self.library)

        # A valid geolocation gets mapped appropriately
        geolocation = {
            "type": "Point",
            "coordinates": [-73.9522, 40.7863]
        }
        actual = api_geolocation_to_orm_location(geolocation, self.library)
        self.assertEquals(actual.library, self.library)
        self.assertEquals(actual.latitude, -73.9522)
        self.assertEquals(actual.longitude, 40.7863)

    def test_api_hours_to_orm_hours(self):
        # An unreconized or missing day raises an appropriate error
        with self.assertRaisesRegex(KeyError, 'No matching day found in .*'):
            api_hours_to_orm_hours({'day': 'Zurday'}, self.library)
        with self.assertRaisesRegex(KeyError, 'No matching day found in .*'):
            api_hours_to_orm_hours({}, self.library)

        # A valid set of hours gets mapped appropriately
        closed_day = {
            "day": "Sun.",
            "open": None,
            "close": None
        }
        actual = api_hours_to_orm_hours(closed_day, self.library)
        self.assertEquals(actual.library, self.library)
        self.assertEquals(actual.day, 0)
        self.assertEquals(actual.open_time, None)
        self.assertEquals(actual.close_time, None)
        self.assertFalse(actual.open_today())

        open_day = {
            "day": "Mon.",
            "open": "10:00",
            "close": "19:00"
        }
        actual = api_hours_to_orm_hours(open_day, self.library)
        self.assertEquals(actual.library, self.library)
        self.assertEquals(actual.day, 1)
        self.assertEquals(actual.open_time, datetime(1900, 1, 1, 10))
        self.assertEquals(actual.close_time, datetime(1900, 1, 1, 19))
        self.assertTrue(actual.open_today())

    def test_api_alert_to_orm_alert(self):
        closure_alert = {
            "scope": "location",
            "_links": {
                "web": {
                    "href": "https://www.nypl.org/"
                }
            },
            "msg": "Closure reason",
            "display": {
                "start": "2019-01-14T00:00:00-05:00",
                "end": "2020-04-01T00:00:00-04:00"
            },
            "closed_for": "Closed for building improvements",
            "applies": {
                "start": "2019-02-16T00:00:00-05:00",
                "end": "2020-04-01T00:00:00-04:00"
            }
        }
        actual = api_alert_to_orm_alert(closure_alert, self.library)
        self.assertEquals(actual.library, self.library)
        self.assertEquals(actual.message, 'Closure reason')
        self.assertEquals(actual.closure_reason, 'Closed for building improvements')
        self.assertEquals(actual.is_closed, True)
        self.assertEquals(actual.period_start, datetime(2019, 2, 16, 0, 0, 0, 0, timezone(timedelta(hours=-5))))
        self.assertEquals(actual.period_end, datetime(2020, 4, 1, 0, 0, 0, 0, timezone(timedelta(hours=-4))))
        self.assertEquals(actual.hyperlink, 'https://www.nypl.org/')

        service_alert = {
            "msg": "The wheelchair lift is currently out of service.",
            "display": {
                "start": "2020-01-06T00:00:00-05:00",
                "end": "2020-03-01T00:00:00-05:00"
            }
        }
        actual = api_alert_to_orm_alert(service_alert, self.library)
        self.assertEquals(actual.library, self.library)
        self.assertEquals(actual.message, 'The wheelchair lift is currently out of service.')
        self.assertEquals(actual.is_closed, False)
        self.assertEquals(actual.period_start, datetime(2020, 1, 6, 0, 0, 0, 0, timezone(timedelta(hours=-5))))
        self.assertEquals(actual.period_end, datetime(2020, 3, 1, 0, 0, 0, 0, timezone(timedelta(hours=-5))))
        self.assertEquals(actual.hyperlink, '')

    def test_api_library_to_orm_library(self):
        # An error is thrown if no ID is present in the dict passed
        idless_library = {'name': 'unknown library'}
        with self.assertRaisesRegex(KeyError, 'Missing domain ID from library: .*'):
            api_library_to_orm_library(idless_library)

        # A valid library is mapped as expected
        library = {
            'id': 'ABC',
            'name': 'Greg Memorial Library',
            'about': 'RIP Greg',
            'cross_street': '42nd and 178th',
            'street_address': '27 West 42nd Street',
            '_embedded': {
                'alerts': [{
                    "id": "562404",
                    "closed_for": "fire alarm testing",
                    "applies": {
                        "start": "2020-02-04T10:00:00-05:00",
                        "end": "2020-02-04T13:00:00-05:00"
                    }
                }],
            },
            'geolocation': {
                    "type": "Point",
                    "coordinates": [
                        -73.9522,
                        40.7863
                    ]
                },
            'hours': {
                "regular": [
                    {
                        "day": "Sun.",
                        "open": None,
                        "close": None
                    }
                ]
            }
        }
        actual = api_library_to_orm_library(library)
        self.assertEquals(actual.nypl_id, 'ABC')
        self.assertEquals(actual.name, 'Greg Memorial Library')
        self.assertEquals(actual.about_text, 'RIP Greg')
        self.assertEquals(actual.cross_street, '42nd and 178th')
        self.assertEquals(actual.street_address, '27 West 42nd Street')

        self.assertEquals(actual.alert_set.all().count(), 1)
        self.assertEquals(actual.location_set.all().count(), 1)
        self.assertEquals(actual.hour_set.all().count(), 1)
