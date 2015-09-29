from django_enumfield import enum

class RackOrientation(enum.Enum):
    FRONT = 1
    BACK = 2

    labels = {
        FRONT: 'Facing front',
        BACK: 'Facing back',
    }


class SwitchSpeed(enum.Enum):
    10Mb = 1
    100Mb = 2
    1Gb = 3
    10Gb = 4
    40Gb = 5

    labels = {
        10Mb: '10Mbps',
        100Mb: '100Mbps',
        1Gb: '1Gbps',
        10Gb: '10Gbps',
        40Gb: '40Gbps'
    }


class SwitchInterconnect(enum.Enum):
    RJ45 = 1
    TWINAX = 2

    labels = {
        RJ45: 'RJ-45',
        TWINAX: 'Twinaxial'
    }