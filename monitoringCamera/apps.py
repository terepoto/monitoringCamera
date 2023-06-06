from django.apps import AppConfig


class Config(AppConfig):
    name = 'monitoringCamera'

    def ready(self):
        # from .tasks.task import start
        from .tasks.searchFace import start
        start()
