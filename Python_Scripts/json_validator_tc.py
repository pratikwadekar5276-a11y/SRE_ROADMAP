import os
import json
import sys
from pathlib import Path

# 1. Parse TeamCity Environment Parameters passed from command line
env = sys.argv[1]
tenantcode = sys.argv[2]
workdir = sys.argv[3]

# 2. Define absolute paths for validation targets dynamically based on environment
filepath1 = f"{workdir}/config/apps/{env}/{tenantcode}"
filepath2 = f"{workdir}/config/tenants/{env}/{tenantcode}/tenant.conf"
filepath3 = f"{workdir}/portfolios/{env}/portfolios.conf"

# Global array to collect all structural and syntax errors across files
all_errors = []

def validate_json_file(file_path): 
    path = Path(file_path)
    
    # 3. File Handling, Existence, and Safety Checks
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

    # 4. Custom Line-by-Line Checker to Detect Multiple Syntax & Structural Errors
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    open_braces = 0
    open_brackets = 0

    # First pass: Filter out comments and empty lines completely, preserve original line numbers
    cleaned_lines = []
    for idx, line in enumerate(lines, start=1):
        raw_line = line.strip()
        
        # Strip inline comments
        if raw_line.startswith("//"):
            continue
        elif "//" in raw_line:
            clean_text = line.split("//", 1)[0].strip()
        else:
            clean_text = raw_line
            
        # Only keep it if it has actual JSON data
        if clean_text:
            cleaned_lines.append({"line_no": idx, "text": clean_text, "raw": line})

    total_clean_lines = len(cleaned_lines)

    for line_no, line_data in enumerate(cleaned_lines, start=1):
        line_str = line_data['text']
        real_line_no = line_data['line_no']
        line = line_data['raw']
        
        # Initialize clean_key to avoid UnboundLocalError
        clean_key = ""

        # Check 1: Bracket Matching and Structural Integrity Tracking
        open_braces += line_str.count('{') - line_str.count('}')
        open_brackets += line_str.count('[') - line_str.count(']')

        # CRITICAL REUSABLE CHECKS
        is_standalone_arn = "arn:" in line_str.lower()
        is_url_line = "https:" in line_str.lower() or "http:" in line_str.lower() or "s3://" in line_str.lower()

        # Check 2: Missing Quotes, Colons/Equals or Malformed Key-Value Pairs
        # If it's a direct URL element inside an array, don't treat it as a key-value split unless it has a real assignment
        has_real_separator = (":" in line_str and not is_url_line) or "=" in line_str or (":" in line_str and line_str.count(":") > 1 and "content-security-policy" not in line_str.lower())
        
        if (has_real_separator or ":" in line_str or "=" in line_str) and not is_standalone_arn:
            # Determine the real structural separator
            if "=" in line_str:
                separator = "="
            elif ":" in line_str:
                # If it's a URL like "url" : "https://abc.com", find the first colon outside the URL protocol
                first_colon = line_str.find(":")
                first_quote = line_str.find('"')
                second_quote = line_str.find('"', first_quote + 1) if first_quote != -1 else -1
                
                # If colon is inside the first key's quotes, or part of http:, adjust smart split
                if "https:" in line_str or "http:" in line_str:
                    separator = "=" if "=" in line_str else ":"
                else:
                    separator = ":"
            else:
                separator = ":"
                
            if separator in line_str:
                parts = line_str.split(separator, 1)
                key = parts[0].strip()
                value = parts[1].strip()
                
                clean_value = value.rstrip(',}]').strip()
                clean_key = key.replace('"', '').strip()
                
                # Validation A: If Key lacks enclosing double quotes
                if key and not (key.startswith('"') and key.endswith('"')):
                    is_portfolio_file = "portfolios.conf" in str(file_path)
                    is_valid_portfolio_key = is_portfolio_file and key.replace('-', '').isalnum()
                    
                    if not key.startswith('{') and not is_valid_portfolio_key and not is_url_line:
                        all_errors.append({
                            "file": str(file_path),
                            "error": f"Invalid Key format (Missing double quotes around key: {key})",
                            "line": real_line_no,
                            "column": 1
                        })
                
                # Validation B: Catch mismatched quotes
                if clean_value and clean_value not in ['true', 'false', 'null'] and not clean_value.replace('.', '', 1).isdigit():
                    if not clean_value.startswith(('{', '[')):
                        
                        # 🔹 CRITICAL SPECIFIC OVERRIDE FOR Content-Security-Policy 🔹
                        if clean_key == "Content-Security-Policy":
                            continue

                        # Skip validation if the entire value line is just a properly enclosed URL string or array element
                        if is_url_line and clean_value.startswith('"') and clean_value.endswith('"'):
                            continue

                        starts_with_special = clean_value.startswith(('$', '@', '#', '%', '&', '*', '_', '-'))
                        
                        if starts_with_special:
                            if clean_value.count('"') % 2 != 0:
                                all_errors.append({
                                    "file": str(file_path),
                                    "error": f"Malformed dynamic value expression (Mismatched quotes in special expression: {value})",
                                    "line": real_line_no,
                                    "column": len(line)
                                })
                        else:
                            starts_with_quote = clean_value.startswith('"')
                            ends_with_quote = clean_value.endswith('"')
                            
                            if starts_with_quote != ends_with_quote:
                                # Safe guard for pure array strings containing URLs
                                if not (line_str.startswith('"') and line_str.rstrip(',').endswith('"')):
                                    all_errors.append({
                                        "file": str(file_path),
                                        "error": f"Malformed string value (Mismatched or missing double quotes around value: {value})",
                                        "line": real_line_no,
                                        "column": len(line)
                                    })

        # Check 3: Universal Missing Commas Check (Object Braces, Strings & Arrays Aware)
        if line_no == total_clean_lines:
            continue

        next_line_str = cleaned_lines[line_no]['text'].strip()
        is_next_closing = next_line_str.startswith(('}', ']'))
        
        if is_next_closing:
            continue

        # CASE A: Line ends with closing brace '}'
        if line_str.endswith('}'):
            if not line_str.endswith(',') and (":" in next_line_str or "=" in next_line_str or next_line_str.startswith('{')):
                all_errors.append({
                    "file": str(file_path),
                    "error": "Missing comma (,) after closing brace '}' before the next field/block starts",
                    "line": real_line_no,
                    "column": len(line)
                })
        
        # CASE B: Line ends with string quotes '"'
        elif line_str.endswith('"') or line_str.rstrip(',').endswith('"') or clean_key == "Content-Security-Policy":
            if not line_str.endswith(','):
                is_next_field = ":" in next_line_str or "=" in next_line_str
                
                # Smart Array Element Check: Handles URLs safely by validating line context
                is_array_element = next_line_str.startswith('"') and (is_url_line or ("=" not in line_str and (line_str.count(":") <= 1 or "http" in line_str)))
                
                if is_next_field or is_array_element:
                    if not is_standalone_arn:
                        all_errors.append({
                            "file": str(file_path),
                            "error": f"Missing comma (,) after string/ARN value before the next field or element starts",
                            "line": real_line_no,
                            "column": len(line)
                        })

    # Check 4: Unclosed Braces or Brackets at End Of File (EOF)
    if open_braces != 0:
        all_errors.append({
            "file": str(file_path),
            "error": f"Mismatched curly braces {{}}. Open count remaining: {abs(open_braces)} (Check missing structural brackets)",
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

# --- Main Runtime Execution Pipeline --- 
path1 = Path(filepath1)
if path1.exists() and path1.is_dir():
    for file in path1.iterdir():
        validate_json_file(file)

validate_json_file(filepath2)
validate_json_file(filepath3)


# 5. Final Report Generation & TeamCity Build Control Logic
if all_errors:
    BLUE_COLOR  = "\033[94m"
    RESET_COLOR = "\033[0m"
    
    print(f"\n{BLUE_COLOR}🔹 Validation Report - Found {len(all_errors)} errors{RESET_COLOR}")
    
    col_widths = [50, 6, 12, 65]
    row_format = "│ {{:<{}}} │ {{:<{}}} │ {{:<{}}} │ {{:<{}}} │".format(*col_widths)
    
    top_border = "┌─" + "─" * col_widths[0] + "─┬─" + "─" * col_widths[1] + "─┬─" + "─" * col_widths[2] + "─┬─" + "─" * col_widths[3] + "─┐"
    header_border = "├─" + "─" * col_widths[0] + "─┼─" + "─" * col_widths[1] + "─┼─" + "─" * col_widths[2] + "─┼─" + "─" * col_widths[3] + "─┤"
    bottom_border = "└─" + "─" * col_widths[0] + "─┴─" + "─" * col_widths[1] + "─┴─" + "─" * col_widths[2] + "─┴─" + "─" * col_widths[3] + "─┘"
    
    print(top_border)
    print(row_format.format("File Path", "Line", "Column", "Error Description"))
    print(header_border)
    
    for err in all_errors:
        clean_path = os.path.relpath(err['file'], start=workdir)
        if len(clean_path) > col_widths[0]:
            clean_path = "..." + clean_path[-(col_widths[0] - 3):]
            
        print(row_format.format(
            clean_path, 
            str(err['line']), 
            str(err['column']), 
            err['error']
        ))
        
    print(bottom_border)
    
    print("\n Result: JSON Validation Failed. Please review the above errors and fix them before proceeding.")
    sys.stdout.flush()
    sys.exit(1)

else:
    print("\n Result: All JSON configuration targets are perfectly valid!")
    sys.exit(0)