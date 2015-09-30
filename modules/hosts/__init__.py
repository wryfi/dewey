from django_enumfield import enum


class ClusterType(enum.Enum):
    ESX = 1
    JUNIPER = 2
    APPLICATION = 3

    labels = {
        ESX: 'VMWare ESX cluster',
        JUNIPER: 'JunOS cluster',
        APPLICATION: 'Generic application cluster'
    }


class OperatingSystem(enum.Enum):
    LINUX = 1
    WINDOWS = 2
    MAC_OS = 3
    JUNOS = 4
    OTHER = 5

    labels = {
        LINUX: 'gnu/linux',
        WINDOWS: 'Windows',
        MAC_OS: 'Mac OS',
        JUNOS: 'JunOS',
        OTHER: 'Other'
    }
