from django_enumfield import enum


class ProtocolEnum(enum.Enum):
    HTTPS = 1
    HTTP = 2

    labels = {
        HTTPS: 'https',
        HTTP: 'http'
    }