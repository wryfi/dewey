from django.apps import AppConfig


class EnvironmentsConfig(AppConfig):
    name = 'dewey.environments'

    def ready(self):
        import dewey.environments.signals
