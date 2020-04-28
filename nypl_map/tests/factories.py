import factory
from datetime import datetime
from nypl_map import models


class LibraryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Library

class HourFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Hour

    day = 0
    library = factory.SubFactory(LibraryFactory)

class AlertFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Alert
    library = factory.SubFactory(LibraryFactory)
    period_start = None
    period_end = None