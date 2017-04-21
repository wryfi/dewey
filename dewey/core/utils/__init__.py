from enumfields import Enum


class ProtocolEnum(Enum):
    HTTPS = 1
    HTTP = 2

    class Labels:
        HTTPS = 'https'
        HTTP = 'http'
