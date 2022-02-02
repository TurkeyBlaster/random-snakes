def fizzbuzz(x):
    f = 'fizz' if not x%3 else ''
    b = 'buzz' if not x%5 else ''
    if f or b:
        print(f'{f}{b}')
    else:
        print(x)

num = input('Enter number: ')
assert num.isdigit() and int(num) >= 1, 'Number must be digit >= 1' # You don't deserve error handling
for x in range(1, int(num)):
    fizzbuzz(x)