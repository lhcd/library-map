from django.db import models
from datetime import datetime
import pytz

class BaseDataModel(models.Model):
    modified_date = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Library(BaseDataModel):
    nypl_id = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=1000, null=False)
    about_text = models.TextField(null=False, default='')

    cross_street = models.CharField(max_length=1000, null=False)
    street_address = models.CharField(max_length=1000, null=False)

    def __str__(self):
        return '({}) {}: {}'.format(self.nypl_id, self.name, self.is_open())

    def would_be_open(self):
        today = datetime.today().weekday()
        return self.hour_set.filter(
            day=today,
            open_time__lt=datetime.now().time(),
            close_time__gt=datetime.now().time()
        ).exists()

    def is_open(self):
        scheduled_open = self.would_be_open()
        has_closure_alert = self.alert_set.filter(
            period_start__lt=datetime.now(pytz.timezone('America/New_York')),
            period_end__gt=datetime.now(pytz.timezone('America/New_York')),
            is_closed=True
        ).exists()
        return (scheduled_open and not has_closure_alert)

    def get_or_update_by_nypl_id(library_object):
        library, created = Library.objects.update_or_create(
            nypl_id=library_object.nypl_id,
            defaults={
                field.name: getattr(library_object, str(field.name))
                for field in library_object._meta.get_fields(
                    include_parents=False, include_hidden=False
                ) if not (isinstance(field, models.ForeignKey) or isinstance(field, models.ManyToOneRel)) and field.name not in ['id', 'nypl_id']
            }
        )
        return library

class Location(BaseDataModel):
    library = models.ForeignKey(
        Library,
        on_delete=models.CASCADE,
        null=False
    )
    latitude = models.FloatField(null=False)
    longitude = models.FloatField(null=False)

    def __str__(self):
        return '({}, {})'.format(self.latitude, self.longitude)

class Hour(BaseDataModel):
    library = models.ForeignKey(
        Library,
        on_delete=models.CASCADE,
        null=False
    )
    DAY_CHOICES = (
        (0, 'Sunday'),
        (1, 'Monday'),
        (2, 'Tuesday'),
        (3, 'Wednesday'),
        (4, 'Thursday'),
        (5, 'Friday'),
        (6, 'Saturday'),
    )
    day = models.IntegerField(
        choices=DAY_CHOICES,
        null=False
    )
    open_time = models.TimeField(null=True)
    close_time = models.TimeField(null=True)

    def __str__(self):
        return '{}: {} - {}'.format(self.get_day_display(), self.open_time, self.close_time)

    def open_today(self):
        return self.open_time is not None and self.close_time is not None

class Alert(BaseDataModel):
    library = models.ForeignKey(
        Library,
        on_delete=models.CASCADE,
        null=False
    )
    message = models.TextField(null=False, default='')

    closure_reason = models.CharField(null=False, default='', max_length=1000)
    is_closed = models.BooleanField(null=False, default=False)

    period_start = models.DateTimeField(null=True)
    period_end = models.DateTimeField(null=True)

    hyperlink = models.URLField(blank=True, null=False)

class LastRefreshed(models.Model):
    refresh_time = models.DateTimeField()