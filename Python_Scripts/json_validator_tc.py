import os
import sys
from pathlib import Path

# 1. Parse TeamCity Environment Parameters
env = sys.argv[1]
tenantcode = sys.argv[2]
workdir = sys.argv[3]

all_errors = []

def validate_json_file(file_path): 
    path = Path(file_path)
    
    # Print statement before scanning, relative to workdir
    rel_display_path = os.path.relpath(path, workdir)
    print(f"--- Scanning file: {rel_display_path} ---")
    
    if not path.exists():
        all_errors.append({"file": str(file_path), "error": "File does not exist", "line": 0, "column": 0})
        return
        
    if path.is_dir():
        return

    # Full Original Logic
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    open_braces = 0
    open_brackets = 0
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

        # Original Complexity Logic
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
                        all_errors.append({"file": str(file_path), "error": f"Invalid Key format: {key}", "line": real_line_no, "column": 1})
                
                if clean_value and clean_value not in ['true', 'false', 'null'] and not clean_value.replace('.', '', 1).isdigit():
                    if not clean_value.startswith(('{', '[')):
                        if clean_key != "Content-Security-Policy":
                            starts_with_special = clean_value.startswith(('$', '@', '#', '%', '&', '*', '_', '-'))
                            if starts_with_special:
                                if clean_value.count('"') % 2 != 0:
                                    all_errors.append({"file": str(file_path), "error": "Malformed dynamic value", "line": real_line_no, "column": len(line)})
                            else:
                                starts_with_quote = clean_value.startswith('"')
                                ends_with_quote = clean_value.endswith('"') or clean_value.rstrip(',"').endswith('=')
                                is_entire_line_quoted = line_str.startswith('"') and line_str.rstrip(',').endswith('"')
                                if starts_with_quote != ends_with_quote and not clean_value.endswith('=') and not is_entire_line_quoted:
                                    all_errors.append({"file": str(file_path), "error": "Malformed string value", "line": real_line_no, "column": len(line)})

        if line_no < total_clean_lines:
            next_line_str = cleaned_lines[line_no]['text'].strip()
            if not next_line_str.startswith(('}', ']')):
                if (line_str.endswith('}') or line_str.endswith('"')) and not line_str.endswith(','):
                    if any(x in next_line_str for x in [":", "=", "{"]) or next_line_str.startswith('"'):
                        all_errors.append({"file": str(file_path), "error": "Missing comma", "line": real_line_no, "column": len(line)})

    if open_braces != 0 or open_brackets != 0:
        all_errors.append({"file": str(file_path), "error": "Mismatched braces/brackets", "line": len(lines), "column": "EOF"})

# --- Search Logic ---
print(f"Target Environment: [{env}] | Target Tenant: [{tenantcode}]")
targets_found = False

for root, dirs, files in os.walk(workdir):
    path_str = Path(root).as_posix()
    
    if f"/config/apps/{env}/{tenantcode}" in path_str:
        targets_found = True
        for file in files:
            if file.endswith(('.json', '.conf')): validate_json_file(Path(root) / file)

    if f"/config/tenants/{env}/{tenantcode}" in path_str and "tenant.conf" in files:
        targets_found = True
        validate_json_file(Path(root) / "tenant.conf")

    if f"/portfolios/{env}" in path_str and "portfolios.conf" in files:
        targets_found = True
        validate_json_file(Path(root) / "portfolios.conf")

if not targets_found:
    print("Warning: No targets found. Check directory structure.")
    sys.exit(1)

if all_errors:
    print(f"\nValidation Failed! Found {len(all_errors)} errors.")
    # Safe table printing
    print("+" + "-"*52 + "+" + "-"*8 + "+" + "-"*14 + "+" + "-"*67 + "+")
    print(f"| {'File Path':<50} | {'Line':<6} | {'Column':<12} | {'Error Description':<65} |")
    print("+" + "-"*52 + "+" + "-"*8 + "+" + "-"*14 + "+" + "-"*67 + "+")
    for err in all_errors:
        clean_path = os.path.relpath(err['file'], start=workdir)
        print(f"| {clean_path[:50]:<50} | {str(err['line']):<6} | {str(err['column']):<12} | {str(err['error']):<65} |")
    print("+" + "-"*52 + "+" + "-"*8 + "+" + "-"*14 + "+" + "-"*67 + "+")
    sys.exit(1)

print("\nResult: All files are perfectly valid!")
sys.exit(0)