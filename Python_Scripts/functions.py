def candriver(name,age, has_license):
    if age >= 18 and has_license:
        return f"{name}, you can drive."
    elif age >= 18 and not has_license:
        return f"{name}, you need a driver's license to drive."
    else:
        return f"{name}, you are too young to drive."

name = input("Enter your name: ")
age = int(input("Enter your age: "))
has_license_input = input("Do you have a driver's license? (yes/no): ")
has_license = has_license_input.lower() == "yes"
can_drive = candriver(name, age, has_license)
print(can_drive)