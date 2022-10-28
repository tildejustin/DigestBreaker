import hashlib
import random


def hash1(user, realm, password):
    """

    :rtype: object
    """
    return hashlib.md5(f'{user}:{realm}:{password}'.encode()).hexdigest()


def hash2(method, url):
    return hashlib.md5(f'{method}:{url}'.encode()).hexdigest()


def response(h1, nonce, noncecount, cnonce, qop, h2):
    return hashlib.md5(f'{h1}:{nonce}:{noncecount}:{cnonce}:{qop}:{h2}'.encode()).hexdigest()


def new_cnonce():
    return hex(random.randint(0, int('ffffffffffffffff', 16)))