filename = 'rockyou_utf8.txt'
with open(filename, 'r', encoding='utf-8') as file:
    count = len(list(enumerate(file)))
print(count)
