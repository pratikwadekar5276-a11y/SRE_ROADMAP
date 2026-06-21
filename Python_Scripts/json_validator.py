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