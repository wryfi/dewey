from django.apps import AppConfig


class NetworksConfig(AppConfig):
    name = 'networks'

    def ready(self):
        import networks.signals
