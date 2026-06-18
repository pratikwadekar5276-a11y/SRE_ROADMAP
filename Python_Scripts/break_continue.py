ranges = int(input("Enter Range: "))

for i in range (1, ranges):
    print(i)
    if(i==5):
        break


for i in range (1, ranges):
    if(i==3):
        continue
    print(i)