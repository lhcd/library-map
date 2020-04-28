from django.apps import AppConfig


class NyplMapConfig(AppConfig):
    name = 'nypl_map'

    def ready(self):
        from nypl_map.library_updater import updater
        updater.start()