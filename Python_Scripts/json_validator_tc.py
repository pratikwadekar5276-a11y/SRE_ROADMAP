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

    for line_no, line in enumerate(lines, start=1):
        line_str = line.strip()
        
        # Skip empty lines to prevent false missing delimiter errors
        if not line_str:
            continue

        # Check 1: Bracket Matching and Structural Integrity Tracking
        open_braces += line_str.count('{') - line_str.count('}')
        open_brackets += line_str.count('[') - line_str.count(']')

# Check 2: Missing Quotes, Colons or Malformed Key-Value Pairs
        if ":" in line_str:
            parts = line_str.split(":", 1)
            key = parts[0].strip()
            value = parts[1].strip()
            
            # Clean trailing commas or brackets from value for validation stability
            clean_value = value.rstrip(',}]')
            
            # Validation A: If Key lacks enclosing double quotes
            if key and not (key.startswith('"') and key.endswith('"')):
                # EXCLUSION FOR PORTFOLIO FILE: Allow unquoted keys with hyphens only in portfolios.conf
                is_portfolio_file = "portfolios.conf" in str(file_path)
                # Matches keys like 'abc-d', 'portfolio-1', etc.
                is_valid_portfolio_key = is_portfolio_file and key.replace('-', '').isalnum()
                
                if not key.startswith('{') and not is_valid_portfolio_key:
                    all_errors.append({
                        "file": str(file_path),
                        "error": f"Invalid Key format (Missing double quotes around key: {key})",
                        "line": line_no,
                        "column": 1
                    })
            
            # Validation B: Catch mismatched quotes like PF1001" or "PF1001
            # Explicitly ensure we skip valid nested block openings like { or [
            if clean_value and not clean_value.replace('.', '', 1).isdigit() and clean_value not in ['true', 'false', 'null']:
                if not clean_value.startswith(('{', '[')):
                    starts_with_quote = clean_value.startswith('"')
                    ends_with_quote = clean_value.endswith('"')
                    
                    if starts_with_quote != ends_with_quote:  # Mismatched quotes logic
                        all_errors.append({
                            "file": str(file_path),
                            "error": f"Malformed string value (Mismatched or missing double quotes around value: {value})",
                            "line": line_no,
                            "column": len(line)
                        })

        # Check 3: Universal Missing Commas Check (Fixed for String Lists & Blocks)
        if line_no < len(lines):
            # Evaluate the next non-empty line context
            next_line_idx = line_no
            next_line_str = ""
            while next_line_idx < len(lines):
                if lines[next_line_idx].strip():
                    next_line_str = lines[next_line_idx].strip()
                    break
                next_line_idx += 1
                
            if next_line_str:
                # Case A: Handle missing commas between JSON blocks
                if line_str.endswith('}'):
                    if next_line_str.startswith('{') or next_line_str.startswith('"'):
                        all_errors.append({
                            "file": str(file_path),
                            "error": "Missing comma (,) after closing brace '}' before the next block starts",
                            "line": line_no,
                            "column": len(line)
                        })
                # Case B: Handle missing commas between list elements / standalone strings
                elif line_str.endswith('"'):
                    if next_line_str.startswith('"'):
                        all_errors.append({
                            "file": str(file_path),
                            "error": f"Missing comma (,) between fields or array elements (Found: {line_str})",
                            "line": line_no,
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
    # ANSI Escape Codes for Dark Blue Output Colorization (\033[94m = Bright/Dark Blue)
    BLUE_COLOR  = "\033[94m"
    RESET_COLOR = "\033[0m"
    
    print(f"\n{BLUE_COLOR}🔹 Validation Report - Found {len(all_errors)} errors{RESET_COLOR}")
    
    col_widths = [50, 6, 12, 65]
    row_format = "│ {{:<{}}} │ {{:<{}}} │ {{:<{}}} │ {{:<{}}} │".format(*col_widths)
    
    top_border    = "┌─" + "─" * col_widths[0] + "─┬─" + "─" * col_widths[1] + "─┬─" + "─" * col_widths[2] + "─┬─" + "─" * col_widths[3] + "─┐"
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