from django.apps import AppConfig
class ClassAppConfig(AppConfig):
    name = 'ClassApp'
    verbose_name = 'TeachTrack'
    def ready(self):
        from . import signals  # noqa: F401
