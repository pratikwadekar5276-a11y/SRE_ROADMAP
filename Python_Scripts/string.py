name = input("Enter Your Name: ")
count = 0
for i in name:
    if i == "a" or i =="e" or i == "o" or i == "i" or i == "u":
        count = count + 1


print(f"Number of Vowels in string are {count}")
for i in range (2,5):
    print(name[i])