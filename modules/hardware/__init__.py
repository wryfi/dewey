from django_enumfield import enum

class RackOrientation(enum.Enum):
    FRONT = 1
    BACK = 2

    labels = {
        FRONT: 'Facing front',
        BACK: 'Facing back',
    }
