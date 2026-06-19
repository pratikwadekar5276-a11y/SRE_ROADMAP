


dic = [{"name": "John", "age": 30, "city": "New York"},
        {"name": "Alice", "age": 25, "city": "Los Angeles"},
        { "age": 17, "city": "Chicago"}]

for person in dic:
    if person["age"] > 18 and person["city"] == "New York":
        print(f"{person.get('name')} can drive the car.")
    else:
        print(f"{person.get('name')} cannot drive the car.")


dic1 = {"name": "John", "age": 30, "city": "New York"}
dic2 = {1, 2, 3, 4, 5}

print(type(dic1))  # Output: <class 'dict'>
print(type(dic2))  # Output: <class 'set'>