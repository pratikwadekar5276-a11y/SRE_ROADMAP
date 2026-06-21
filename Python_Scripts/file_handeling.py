f = open('idm.json', 'r')
text = f.readline()
print(text)
f.close()

with open('idm.json', 'r') as f:
    for i, line in enumerate(f, start=1):
       if i in [1, 3, 5]:
           print(line)


import json

keys_to_fetch = [
    "idmurl",
    "serviceaccount",
    "serviceaccountpassword"
]

with open("/Users/pratikwadekar/Desktop/python_automation/file1.json", "r") as f:
    data = json.load(f)

for key in keys_to_fetch:
    if key in data:
        print(f"{key} : {data[key]}")