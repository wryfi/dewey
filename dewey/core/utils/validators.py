import base64
import binascii
import re
import struct

from dewey.core.exceptions import InvalidKeyError


def validate_openssh_key(key_type, key):
    try:
        decoded = base64.b64decode(key)
    except binascii.Error:
        raise InvalidKeyError(key_type, key, 'key is not valid base64-encoded data')
    # the first 4 bytes tell us how many of the proceeding bytes correspond to the key type
    typestring_length = struct.unpack('>I', decoded[:4])[0]
    offset = typestring_length + 4
    # the next N bytes should match the key_type argument
    typestring = decoded[4:offset].decode('utf-8')
    if typestring != key_type:
        raise InvalidKeyError(key_type, key, 'key does not match specified type')
    return True

