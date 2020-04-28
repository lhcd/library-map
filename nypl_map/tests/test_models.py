from datetime import datetime, timezone, timedelta

from freezegun import freeze_time
from django.test import TestCase

from nypl_map.models import Library, Hour
from nypl_map.tests.factories import LibraryFactory, HourFactory, AlertFactory

class MapperTestCase(TestCase):
    def setUp(self):
        self.library = LibraryFactory()

    @freeze_time('2020-01-01 15:00:00')
    def test_library_would_be_open(self):
        open_library = LibraryFactory(nypl_id='1')
        closed_library_after_hours = LibraryFactory(nypl_id='2')
        closed_library_closed_today = LibraryFactory(nypl_id='3')
        closed_library_no_hour_info = LibraryFactory(nypl_id='4')

        HourFactory(
            library=open_library,
            day=2,
            open_time=datetime(1900, 1, 1, 10, tzinfo=timezone(timedelta(hours=-5))),
            close_time=datetime(1900, 1, 1, 18, tzinfo=timezone(timedelta(hours=-5))),
        )
        HourFactory(
            library=closed_library_after_hours,
            day=2,
            open_time=datetime(1900, 1, 1, 10, tzinfo=timezone(timedelta(hours=-5))),
            close_time=datetime(1900, 1, 1, 13, 30, tzinfo=timezone(timedelta(hours=-5))),
        )
        HourFactory(
            library=closed_library_after_hours,
            day=3,
            open_time=datetime(1900, 1, 1, 10, tzinfo=timezone(timedelta(hours=-5))),
            close_time=datetime(1900, 1, 1, 19, 30, tzinfo=timezone(timedelta(hours=-5))),
        )
        HourFactory(
            library=closed_library_closed_today,
            day=2,
            open_time=None,
            close_time=None
        )

        self.assertTrue(open_library.would_be_open())
        self.assertFalse(closed_library_after_hours.would_be_open())
        self.assertFalse(closed_library_closed_today.would_be_open())
        self.assertFalse(closed_library_no_hour_info.would_be_open())

    @freeze_time('2020-01-01 15:00:00')
    def test_library_is_open_evaluation(self):
        open_library = LibraryFactory(nypl_id='1')
        open_library_with_closure_alert = LibraryFactory(nypl_id='2')

        HourFactory(
            library=open_library,
            day=2,
            open_time=datetime(1900, 1, 1, 10, tzinfo=timezone(timedelta(hours=-5))),
            close_time=datetime(1900, 1, 1, 18, tzinfo=timezone(timedelta(hours=-5))),
        )
        HourFactory(
            library=open_library_with_closure_alert,
            day=2,
            open_time=datetime(1900, 1, 1, 10, tzinfo=timezone(timedelta(hours=-5))),
            close_time=datetime(1900, 1, 1, 18, tzinfo=timezone(timedelta(hours=-5))),
        )

        AlertFactory(
            library=open_library,
            is_closed=False,
            period_start=datetime(2019, 1, 1, 18, tzinfo=timezone(timedelta(hours=-5))),
            period_end=datetime(2020, 1, 1, 18, tzinfo=timezone(timedelta(hours=-5))),
        )
        AlertFactory(
            library=open_library_with_closure_alert,
            is_closed=True,
            period_start=datetime(2019, 1, 1, 18, tzinfo=timezone(timedelta(hours=-5))),
            period_end=datetime(2020, 1, 1, 18, tzinfo=timezone(timedelta(hours=-5))),
        )

        self.assertTrue(open_library.is_open())
        todays_hour = HourFactory(library=self.library)

    def test_get_or_update_by_nypl_id(self):
        existing_match = LibraryFactory(nypl_id='F', name='Not This')
        unsaved_matchable_library_with_match = Library(
            nypl_id='F',
            name='Test Library'
        )
        unsaved_unmatchable_library_with_match = Library(
            nypl_id='X',
            name='Test Library'
        )
        actual_matched = Library.get_or_update_by_nypl_id(unsaved_matchable_library_with_match)
        self.assertEquals(actual_matched, existing_match)
        self.assertEquals(actual_matched.nypl_id, 'F')
        self.assertEquals(actual_matched.name, 'Test Library')
        self.assertNotEquals(Library.get_or_update_by_nypl_id(unsaved_unmatchable_library_with_match), existing_match)

    def test_hour_is_open_today(self):
        closed_hour = HourFactory(
            open_time=None,
            close_time=None,
            library=LibraryFactory(nypl_id='closed_hour')
        )
        open_hour = HourFactory(
            open_time=datetime.now().time(),
            close_time=datetime.now().time(),
            library=LibraryFactory(nypl_id='open_hour')
        )

        self.assertFalse(closed_hour.open_today())
        self.assertTrue(open_hour.open_today())
