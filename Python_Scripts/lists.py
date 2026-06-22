name = ["Pratik", "Pranav", "Shiro"]

if "Pandu" in name:
    print(f"{guest} Was in Party")
else:
    print("Unknown guest in party")

print("New Guest arrived register his name")
guest = input("Enter Your name: ")
name.append(guest)
if "Pandu" in name:
    print(f"{guest} Was in Party")
else:
    print("Unknown guest in party")
name.insert(1,"Abhishek")
print(name)

new_guest = ["Abhay", "Shubham"]
name.extend(new_guest)
print(name)