b = 1
N = 52
d = 5
sum = 0

while (abs(N - sum) > 0.1):
    sum = 0
    for x in range(1,d+1):
        sum += b**x

    b += 0.0001

print(b)