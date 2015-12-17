from django_enumfield import enum


default_app_config = 'hosts.apps.HostsAppConfig'


class ClusterType(enum.Enum):
    ESX = 1
    JUNIPER = 2
    APPLICATION = 3

    labels = {
        ESX: 'VMWare ESX/ESXi cluster',
        JUNIPER: 'JunOS cluster',
        APPLICATION: 'Generic application cluster'
    }


class OperatingSystem(enum.Enum):
    UBUNTU = 1
    CENTOS = 2
    WINDOWS = 3
    MAC_OS = 4
    JUNOS = 5
    ESX = 6
    OTHER = 7

    labels = {
        UBUNTU: 'ubuntu',
        CENTOS: 'CentOS',
        WINDOWS: 'Windows',
        MAC_OS: 'Mac OS',
        JUNOS: 'JunOS',
        ESX: 'VMware ESX/ESXi',
        OTHER: 'other'
    }
