import os
import json
import sys
from pathlib import Path



env = sys.argv[1]
tenantcode = sys.argv[2]
workdir = sys.argv[3]

# 2. Define absolute paths for validation targets
filepath1 = f"{workdir}/config/apps/{env}/{tenantcode}"
filepath2 = f"{workdir}/config/tenants/{env}/{tenantcode}/tenant.conf"
filepath3 = f"{workdir}/portfolios/{env}/portfolios.conf"

all_errors = []

def validate_json_file(file_path): 
    path = Path(file_path)
    
    # 3. File Handling and Safety Checks
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

    # 4. Custom Line-by-Line Checker to Detect Multiple Errors
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    open_braces = 0
    open_brackets = 0

    for line_no, line in enumerate(lines, start=1):
        line_str = line.strip()
        
        # Skip empty lines
        if not line_str:
            continue

        # Check 1: Bracket Matching and Structural Integrity Tracking
        open_braces += line_str.count('{') - line_str.count('}')
        open_brackets += line_str.count('[') - line_str.count(']')

        # Check 2: Missing Quotes or Colons in Key-Value Pairs
        if ":" in line_str:
            parts = line_str.split(":", 1)
            key = parts[0].strip()
            value = parts[1].strip()
            
            # If Key lacks double quotes
            if key and not (key.startswith('"') and key.endswith('"')):
                if not key.startswith('{'):  # Exclude opening braces
                    all_errors.append({
                        "file": str(file_path),
                        "error": f"Invalid Key format (Missing double quotes around key: {key})",
                        "line": line_no,
                        "column": 1
                    })
            
            # If Value is a string but misses closing quotes or terminal delimiters
            if value.startswith('"') and not (value.endswith('"') or value.endswith('",') or value.endswith('"}') or value.endswith('"]')):
                all_errors.append({
                    "file": str(file_path),
                    "error": "Unterminated string constant or invalid delimiter in value",
                    "line": line_no,
                    "column": len(line)
                })

        # Check 3: Missing Commas
        # If the line contains a value, and the next line introduces a new key but this line misses a comma
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

    # Check 4: Unclosed Braces or Brackets at EOF
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

# --- Main Execution --- 
path1 = Path(filepath1)
if path1.exists() and path1.is_dir():
    for file in path1.iterdir():
        validate_json_file(file)

validate_json_file(filepath2)
validate_json_file(filepath3)


# 5. Final Report Generation & TeamCity Build Control Logic
if all_errors:
 
    RED_COLOR   = "\033[91m"
    RESET_COLOR = "\033[0m"
    # Print the primary header statement
    print(f"\n{RED_COLOR}Validation Report - Found {len(all_errors)} errors{RESET_COLOR}")
    
    # Define table column widths: File, Line, Column, Error Message
    # Column width is configured to 12 to cleanly contain "End of file" without overflowing layout blocks
    col_widths = [50, 6, 12, 65]
    row_format = "│ {{:<{}}} │ {{:<{}}} │ {{:<{}}} │ {{:<{}}} │".format(*col_widths)
    
    # Generate static grid lines for text-based tables
    top_border    = "┌─" + "─" * col_widths[0] + "─┬─" + "─" * col_widths[1] + "─┬─" + "─" * col_widths[2] + "─┬─" + "─" * col_widths[3] + "─┐"
    header_border = "├─" + "─" * col_widths[0] + "─┼─" + "─" * col_widths[1] + "─┼─" + "─" * col_widths[2] + "─┼─" + "─" * col_widths[3] + "─┤"
    bottom_border = "└─" + "─" * col_widths[0] + "─┴─" + "─" * col_widths[1] + "─┴─" + "─" * col_widths[2] + "─┴─" + "─" * col_widths[3] + "─┘"
    
    # Print Table Header
    print(top_border)
    print(row_format.format("File Path", "Line", "Column", "Error Description"))
    print(header_border)
    
    # Print Table Rows dynamically
    for err in all_errors:
        # Strip TeamCity's local agent path prefix to compute a clean repository path
        clean_path = os.path.relpath(err['file'], start=workdir)
        
        # Truncate clean file path from the left only if it exceeds 50 characters
        if len(clean_path) > col_widths[0]:
            clean_path = "..." + clean_path[-(col_widths[0] - 3):]
            
        print(row_format.format(
            clean_path, 
            str(err['line']), 
            str(err['column']), 
            err['error']
        ))
        
    print(bottom_border)
    
    print("\n Result: JSON Validation Failed. Failing the TeamCity build!")
    sys.stdout.flush()
    sys.exit(1)  # Signal exit code 1 to explicitly fail the execution pipeline step

else:
    print("\n Result: All JSON files are perfectly valid! ")
    sys.exit(0)  # Signal exit code 0 for a successful step completion