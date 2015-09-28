from django_enumfield import enum

class HostType(enum.Enum):
    BARE_METAL_SERVER = 1
    VIRTUAL_MACHINE = 2
    POWER_DISTRIBUTION_UNIT = 3
    NETWORK_EQUIPMENT = 4

    labels = {
        BARE_METAL_SERVER: 'Bare metal server',
        VIRTUAL_MACHINE: 'Virtual machine',
        POWER_DISTRIBUTION_UNIT: 'Power Distribution Unit',
        NETWORK_EQUIPMENT: 'Networking equipment'
    }


class ClusterType(enum.Enum):
    ESX = 1
    JUNIPER = 2
    APPLICATION = 3

    labels = {
        ESX: 'VMWare ESX cluster',
        JUNIPER: 'JunOS cluster',
        APPLICATION: 'Generic application cluster'
    }