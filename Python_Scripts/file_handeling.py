'''  
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
        '''
''' 
import json

keys_to_fetch = [
    "idmurl",
    "serviceaccount",
    "serviceaccountpassword"
]

source_file = "/Users/pratikwadekar/Desktop/python_automation/file1.json"
target_file = "/Users/pratikwadekar/Desktop/SRE_ROADMAP/Python_Scripts/idm.json"

with open(source_file, "r") as f:
    source_data = json.load(f)

with open(target_file, "r") as f:
    target_data = json.load(f)

# Replace values in target file
for key in keys_to_fetch:
    if key in source_data and key in target_data:
        target_data[key] = source_data[key]

with open(target_file, "w") as f:
    json.dump(target_data, f, indent=4)

print("Values substituted successfully")
'''

import json

files = [
    "/path/file1.json",
    "/path/file2.json",
    "/path/file3.json"
]

all_errors = []

for file in files:

    try:
        with open(file, "r") as f:
            json.load(f)

    except json.JSONDecodeError as e:

        all_errors.append({
            "file": file,
            "error": e.msg,
            "line": e.lineno,
            "column": e.colno
        })

    except FileNotFoundError:

        all_errors.append({
            "file": file,
            "error": "File not found"
        })

# Final Report

if all_errors:

    print("\nValidation Report\n")

    for err in all_errors:

        print(f"File: {err['file']}")
        print(f"Error: {err['error']}")

        if "line" in err:
            print(f"Line: {err['line']}")
            print(f"Column: {err['column']}")

        print("-" * 50)

else:
    print("All JSON files are valid")

