import hashlib
import random


# proud of this one
def md5(*args):
    string = ':'.join(str(x) for x in args)
    return(hashlib.md5(string.encode()).hexdigest())

# def hash1(user, realm, password):
#     return hashlib.md5(f'{user}:{realm}:{password}'.encode()).hexdigest()


# def hash2(method, url):
#     return hashlib.md5(f'{method}:{url}'.encode()).hexdigest()


# def response(h1, nonce, noncecount, cnonce, qop, h2):
#     return hashlib.md5(f'{h1}:{nonce}:{noncecount}:{cnonce}:{qop}:{h2}'.encode()).hexdigest()


def new_cnonce():
    # I don't think I've written something as convoluted as this monstrosity
    return hex(random.randint(0, int('ffffffffffffffff', 16)))[2:]
