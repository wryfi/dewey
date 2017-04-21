from enumfields import Enum


default_app_config = 'dewey.environments.apps.EnvironmentsConfig'


class ClusterType(Enum):
    ESX = 1
    JUNIPER = 2
    APPLICATION = 3

    class Labels:
        ESX = 'VMWare ESX/ESXi cluster'
        JUNIPER = 'JunOS cluster'
        APPLICATION = 'Generic application cluster'


class OperatingSystem(Enum):
    UBUNTU = 1
    CENTOS = 2
    WINDOWS = 3
    MAC_OS = 4
    JUNOS = 5
    ESX = 6
    OTHER = 7

    class Labels:
        UBUNTU = 'ubuntu'
        CENTOS = 'CentOS'
        WINDOWS = 'Windows'
        MAC_OS = 'Mac OS'
        JUNOS = 'JunOS'
        ESX = 'VMware ESX/ESXi'
        OTHER = 'other'
