"""Print the current TOTP 6-digit code for a base32 secret.

Usage: python research/totp.py <base32 secret> [offset steps]
"""
import base64
import hashlib
import hmac
import struct
import sys
import time


def totp(secret_b32, step=30, digits=6, t=None):
    pad = '=' * ((8 - len(secret_b32) % 8) % 8)
    key = base64.b32decode(secret_b32.upper() + pad)
    if t is None:
        t = int(time.time())
    counter = t // step + (int(sys.argv[2]) if len(sys.argv) > 2 else 0)
    msg = struct.pack('>Q', counter)
    digest = hmac.new(key, msg, hashlib.sha1).digest()
    o = digest[-1] & 0x0F
    code = (struct.unpack('>I', digest[o:o + 4])[0] & 0x7FFFFFFF) % (10 ** digits)
    return str(code).zfill(digits)


if __name__ == '__main__':
    print(totp(sys.argv[1]))
