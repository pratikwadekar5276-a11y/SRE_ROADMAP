a = "pratik"
for i in a:
    if i == "a" or i == "e" or i == "i" or i == "o" or i == "u":
        print(f"{i} is vowel")
    else:
        print(f"{i} is not vowel")

a = int(input("Enter Range: "))
for i in range (0 , a ):
    if i == 0 or i == 1:
        print(f"{i} is neither even or odd")
    else:
        if(i%2==0):
            print(f"{i} is even")
        else:
            print(f"{i} is odd")