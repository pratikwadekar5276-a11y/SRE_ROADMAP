a = int(input("Enter Age: "))
b = input("Enter Gender: ")


if a > 18 and b == "Male":
    print("Marrige is Legal")
else:
    print("Marriage is Not Legal")

if a > 18 or b == "Male":
    print("You can Drive car")
else:
    print("You can not drive car")

    