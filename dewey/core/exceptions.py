class InvalidKeyError(Exception):
    def __init__(self, key_type, key_value, message):
        self.key_type = key_type
        self.key_value = key_value
        self.message = message
