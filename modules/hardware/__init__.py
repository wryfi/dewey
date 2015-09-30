from django_enumfield import enum

class RackOrientation(enum.Enum):
    FRONT = 1
    BACK = 2

    labels = {
        FRONT: 'Facing front',
        BACK: 'Facing back',
    }


class SwitchSpeed(enum.Enum):
    TEN = 1
    ONE_HUNDRED = 2
    GIGABIT = 3
    TEN_GIGABIT = 4
    FORTY_GIGABIT = 5

    labels = {
        TEN: '10 Mbps',
        ONE_HUNDRED: '100 Mbps',
        GIGABIT: '1 Gbps',
        TEN_GIGABIT: '10 Gbps',
        FORTY_GIGABIT: '40 Gbps'
    }


class SwitchInterconnect(enum.Enum):
    RJ45 = 1
    TWINAX = 2

    labels = {
        RJ45: 'RJ-45',
        TWINAX: 'Twinaxial'
    }