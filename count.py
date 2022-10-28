# open file in read mode
with open(r"number1mil.csv", 'r') as fp:
    for count, line in enumerate(fp):
        pass
print('Total Lines', count + 1)