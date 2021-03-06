from enumfields import Enum


class RackOrientation(Enum):
    FRONT = 1
    BACK = 2

    class Labels:
        FRONT = 'Facing front'
        BACK = 'Facing back'


class SwitchSpeed(Enum):
    TEN = 1
    ONE_HUNDRED = 2
    GIGABIT = 3
    TEN_GIGABIT = 4
    FORTY_GIGABIT = 5

    class Labels:
        TEN = '10 Mbps'
        ONE_HUNDRED = '100 Mbps'
        GIGABIT = '1 Gbps'
        TEN_GIGABIT = '10 Gbps'
        FORTY_GIGABIT = '40 Gbps'


class SwitchInterconnect(Enum):
    RJ45 = 1
    TWINAX = 2

    class Labels:
        RJ45 = 'RJ-45'
        TWINAX = 'Twinaxial'


class RackDepth(Enum):
    FULL = 1
    HALF = 2
    QUARTER = 4

    class Labels:
        FULL = 'Full depth'
        HALF = 'Half depth'
        QUARTER = 'Quarter depth'
