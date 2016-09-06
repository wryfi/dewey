from django.apps import AppConfig


class EnvironmentsConfig(AppConfig):
    name = 'environments'

    def ready(self):
        import environments.signals
