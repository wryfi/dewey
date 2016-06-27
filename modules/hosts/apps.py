from django.apps import AppConfig

class HostsAppConfig(AppConfig):
    name = 'hosts'
    verbose_name = 'Hosts'

    def ready(self):
        import hosts.signals
