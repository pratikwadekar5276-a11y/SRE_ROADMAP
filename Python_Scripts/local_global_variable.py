a = int(input("Enter a number: "))

def sum ():
    b = int(input("Enter another number: "))
    total = a + b
    print(f"The sum of {a} and {b} is: {total}")# This will raise an error because b is not defined in this scope
sum()