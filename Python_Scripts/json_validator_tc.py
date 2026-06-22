import json
import sys
from pathlib import Path


env = sys.argv[1]
tenantcode = sys.argv[2]
workdir = sys.argv[3]
filepath1 = f"{workdir}/config/apps/{env}/{tenantcode}"
filepath2 = f"{workdir}/config/tenants/{env}/{tenantcode}/tenant.json"
filepath3 = f"{workdir}/portfolios/{env}/portfolios"

all_errors = []

def validate_json_file(file_path): 
    path = Path(file_path)
    
    # १. फाईल हँडलिंग आणि सुरक्षा
    if not path.exists():
        all_errors.append({
            "file": str(file_path),
            "error": "File does not exist",
            "line": 0,
            "column": 0
        })
        return
        
    if path.is_dir():
        return

    # २. मल्टिपल एरर्स शोधण्यासाठी कस्टम लाईन-बाय-लाईन चेकर
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    open_braces = 0
    open_brackets = 0

    for line_no, line in enumerate(lines, start=1):
        line_str = line.strip()
        
        # रिकाम्या लाईन्स सोडून द्या
        if not line_str:
            continue

        # चेक १: ब्रॅकेट्स मॅचिंग ट्रॅक करणे (Structural Integrity)
        open_braces += line_str.count('{') - line_str.count('}')
        open_brackets += line_str.count('[') - line_str.count(']')

        # चेक २: की-व्हॅल्यू जोडीमध्ये कोट्स (Quotes) किंवा कोलन (Colon) सुटलाय का?
        if ":" in line_str:
            parts = line_str.split(":", 1)
            key = parts[0].strip()
            value = parts[1].strip()
            
            # जर की (Key) ला कोट्स नसतील
            if key and not (key.startswith('"') and key.endswith('"')):
                if not key.startswith('{'):  # ओपनिंग ब्रॅकेट नसेल तरच
                    all_errors.append({
                        "file": str(file_path),
                        "error": f"Invalid Key format (Missing double quotes around key: {key})",
                        "line": line_no,
                        "column": 1
                    })
            
            # जर व्हॅल्यू (Value) स्ट्रिंग आहे पण शेवटी कोट्स किंवा कॉमा नाहीये
            if value.startswith('"') and not (value.endswith('"') or value.endswith('",') or value.endswith('"}') or value.endswith('"]')):
                all_errors.append({
                    "file": str(file_path),
                    "error": f"Unterminated string constant or invalid delimiter in value",
                    "line": line_no,
                    "column": len(line)
                })

        # चेक ३: कॉमा (Comma) चा राडा
        # जर लाईनच्या शेवटी व्हॅल्यू आहे, आणि पुढच्या लाईनवर नवीन की सुरू होतेय, पण इथे कॉमा नाहीये
        if line_no < len(lines):
            next_line_str = lines[line_no].strip()
            if next_line_str and (next_line_str.startswith('"') or next_line_str.startswith('{')):
                if not (line_str.endswith(',') or line_str.endswith('{') or line_str.endswith('[') or line_str.endswith('}') or line_str.endswith(']')):
                    all_errors.append({
                        "file": str(file_path),
                        "error": "Missing comma (,) at the end of this line",
                        "line": line_no,
                        "column": len(line)
                    })

    # चेक ४: फाईलच्या शेवटी ब्रॅकेट्स व्यवस्थित बंद झालेत का?
    if open_braces != 0:
        all_errors.append({
            "file": str(file_path),
            "error": f"Mismatched curly braces {{}}. Open count remaining: {abs(open_braces)}",
            "line": len(lines),
            "column": "End of file"
        })
    if open_brackets != 0:
        all_errors.append({
            "file": str(file_path),
            "error": f"Mismatched square brackets []. Open count remaining: {abs(open_brackets)}",
            "line": len(lines),
            "column": "End of file"
        })

# --- मुख्य एक्झिक्युशन --- 
path1 = Path(filepath1)
if path1.exists() and path1.is_dir():
    for file in path1.iterdir():
        validate_json_file(file)

validate_json_file(filepath2)
validate_json_file(filepath3)

# फायनल रिपोर्ट प्रिंटिंग (तुझा मूळ फॉरमॅट)
if all_errors:
    print(f"\nValidation Report - Found {len(all_errors)} errors\n")
    for err in all_errors:
        print(f"File: {err['file']}")
        print(f"Error: {err['error']}")
        print(f"Line: {err['line']}")
        print(f"Column: {err['column']}")
        print("-" * 50)
else:
    print("All JSON files are valid 🚀")

if all_errors:
    print(f"\n🛑 Validation Report - Found {len(all_errors)} errors\n")
    for err in all_errors:
        print(f"File: {err['file']}")
        print(f"Error: {err['error']}")
        print(f"Line: {err['line']}")
        print(f"Column: {err['column']}")
        print("-" * 50)
    
    print("\n❌ Result: JSON Validation Failed. Failing the TeamCity build!")
    sys.stdout.flush()
    sys.exit(1)  # 🔥 क्रिटिकल: हा कोड टीमसिटीला सांगेल की बिल्ड FAIL झाला आहे!

else:
    print("\n🚀 Result: All JSON files are perfectly valid! Exit Code 0.")
    sys.exit(0)  # सक्सेस! बिल्ड ग्रीन होईल.