import os
import json
import sys
from pathlib import Path

# 1. Parse TeamCity Environment Parameters passed from command line
env = sys.argv[1]
tenantcode = sys.argv[2]
workdir = sys.argv[3]

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
        
        if raw_line.startswith("//") or raw_line.startswith("#"):
            continue
            
        if raw_line.count("://") > 1 or "java_tool" in raw_line.lower():
            cleaned_lines.append({"line_no": idx, "text": raw_line, "raw": line, "is_immune": True})
            continue

        if "//" in raw_line:
            first_comment_idx = raw_line.find("//")
            if "://" in raw_line or raw_line[:first_comment_idx].count('"') % 2 != 0:
                clean_text = raw_line
            else:
                parts_comment = line.split("//")
                if len(parts_comment) > 2 and parts_comment[0].endswith(":"):
                    clean_text = (parts_comment[0] + "//" + parts_comment[1]).strip()
                else:
                    clean_text = line.split("//", 1)[0].strip()
        else:
            clean_text = raw_line
            
        if clean_text:
            cleaned_lines.append({"line_no": idx, "text": clean_text, "raw": line, "is_immune": False})

    total_clean_lines = len(cleaned_lines)

    for line_no, line_data in enumerate(cleaned_lines, start=1):
        line_str = line_data['text']
        real_line_no = line_data['line_no']
        line = line_data['raw']
        is_immune = line_data.get('is_immune', False)
        
        clean_key = ""

        open_braces += line_str.count('{') - line_str.count('}')
        open_brackets += line_str.count('[') - line_str.count(']')

        is_arn = "arn:" in line_str.lower()
        is_apig = "apig." in line_str.lower()
        is_java_env = "java_tool" in line_str.lower() or is_immune
        is_multiple_urls = line_str.count("://") > 1 or is_immune
        is_dynamic_template = "${" in line_str  
        
        is_pure_url = False
        if "://" in line_str and "=" not in line_str and not is_multiple_urls:
            first_colon = line_str.find(":")
            protocol_colon = line_str.find("://")
            if first_colon == protocol_colon:
                is_pure_url = True

        has_separator = ":" in line_str or "=" in line_str
        should_bypass_quotes = is_arn or is_pure_url or is_apig or is_multiple_urls or is_java_env or is_dynamic_template
        
        if has_separator and not should_bypass_quotes:
            if "=" in line_str:
                first_equal_idx = line_str.find("=")
                before_equal = line_str[:first_equal_idx].strip()
                if before_equal.startswith('"') and before_equal.endswith('"'):
                    separator = "="
                elif ":" in line_str:
                    separator = ":"
                else:
                    separator = "="
            else:
                separator = ":"
            
            if separator == ":" and "://" in line_str:
                first_colon_idx = line_str.find(":")
                before_colon = line_str[:first_colon_idx].strip()
                if not (before_colon.startswith('"') and before_colon.endswith('"')):
                    has_separator = False
            
            if has_separator:
                parts = line_str.split(separator, 1)
                key = parts[0].strip()
                value = parts[1].strip()
                
                clean_value = value.rstrip(',}]').strip()
                clean_key = key.replace('"', '').strip()
                
                if key and not (key.startswith('"') and key.endswith('"')):
                    is_portfolio_file = "portfolios.conf" in str(file_path)
                    is_valid_portfolio_key = is_portfolio_file and key.replace('-', '').isalnum()
                    
                    if not key.startswith('{') and not is_valid_portfolio_key:
                        all_errors.append({
                            "file": str(file_path),
                            "error": f"Invalid Key format (Missing double quotes around key: {key})",
                            "line": real_line_no,
                            "column": 1
                        })
                
                if clean_value and clean_value not in ['true', 'false', 'null'] and not clean_value.replace('.', '', 1).isdigit():
                    if not clean_value.startswith(('{', '[')):
                        
                        if clean_key == "Content-Security-Policy":
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
                            ends_with_quote = clean_value.endswith('"') or clean_value.rstrip(',"').endswith('=')
                            is_entire_line_quoted = line_str.startswith('"') and line_str.rstrip(',').endswith('"')
                            
                            if starts_with_quote != ends_with_quote and not clean_value.endswith('=') and not is_entire_line_quoted:
                                all_errors.append({
                                    "file": str(file_path),
                                    "error": f"Malformed string value (Mismatched or missing double quotes around value: {value})",
                                    "line": real_line_no,
                                    "column": len(line)
                                })

        if line_no == total_clean_lines:
            continue

        next_line_str = cleaned_lines[line_no]['text'].strip()
        is_next_closing = next_line_str.startswith(('}', ']'))
        
        if is_next_closing:
            continue

        if line_str.endswith('}'):
            if not line_str.endswith(',') and (":" in next_line_str or "=" in next_line_str or next_line_str.startswith('{')):
                all_errors.append({
                    "file": str(file_path),
                    "error": "Missing comma (,) after closing brace '}' before the next field/block starts",
                    "line": real_line_no,
                    "column": len(line)
                })
        
        elif line_str.endswith('"') or line_str.rstrip(',').endswith('"') or line_str.endswith('}') or line_str.rstrip(',').endswith('}') or line_str.rstrip(',"').endswith('=') or should_bypass_quotes or clean_key == "Content-Security-Policy":
            if not line_str.endswith(','):
                is_next_field = ":" in next_line_str or "=" in next_line_str
                is_array_element = next_line_str.startswith('"')
                is_next_block = next_line_str.startswith('{')  
                
                if is_next_field or is_array_element or is_next_block:
                    all_errors.append({
                        "file": str(file_path),
                        "error": f"Missing comma (,) after value/brace before the next field, block or element starts",
                        "line": real_line_no,
                        "column": len(line)
                    })

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

print(f"Starting Environment-Aware scan across VCS directories...")
print(f"Target Environment: [{env}] | Target Client: [{tenantcode}]")
targets_found = False

for root, dirs, files in os.walk(workdir):
    normalized_root = Path(root).as_posix()
    
    apps_target_part = f"config/apps/{env}/{tenantcode}"
    if apps_target_part in normalized_root:
        targets_found = True
        for file in files:
            file_full_path = Path(root) / file
            print(f" [MATCHED-{env}] Validating App Config: {file_full_path}")
            validate_json_file(file_full_path)

    tenant_target_part = f"config/tenants/{env}/{tenantcode}"
    if tenant_target_part in normalized_root:
        if "tenant.conf" in files:
            targets_found = True
            tenant_file = Path(root) / "tenant.conf"
            print(f" [MATCHED-{env}] Validating Tenant File: {tenant_file}")
            validate_json_file(tenant_file)

    portfolio_target_part = f"portfolios/{env}"
    if portfolio_target_part in normalized_root:
        if "portfolios.conf" in files:
            targets_found = True
            portfolio_file = Path(root) / "portfolios.conf"
            print(f" [MATCHED-{env}] Validating Portfolio File: {portfolio_file}")
            validate_json_file(portfolio_file)

if not targets_found:
    print(f"Warning: No valid configuration targets found for Client '{tenantcode}' explicitly inside the '{env}' environment folders.")

if all_errors:
    BLUE_COLOR  = "\033[94m"
    RESET_COLOR = "\033[0m"
    
    print(f"\n Validation Report - Found {len(all_errors)} errors{RESET_COLOR}")
    
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
    print("\n Result: All detected JSON configuration targets are perfectly valid!")
    sys.exit(0)