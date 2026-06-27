import os
import shutil
import subprocess
import sys
from pathlib import Path


def run_git_command(command, repo_path):
    """Local Git commands run करण्यासाठी हेल्पर फंक्शन"""
    try:
        result = subprocess.run(
            command,
            cwd=repo_path,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"❌ Git Error: {e.stderr}")
        sys.exit(1)


def create_and_sync_instance():
    # --- 1. User Input आणि Paths Configuration ---
    repo_path = input("Enter your local Git repository path: ").strip()
    case_number = input("Enter Case Number (for new branch): ").strip()
    env = input("Enter Environment (e.g., dev, prod): ").strip()
    client_name = input("Enter Client Name: ").strip()

    # 🎯 तुझा 4.0 सोर्स फोल्डर पाथ इथे टाक
    source_v4_folder = Path("/path/to/your/local/version_4.0_folder")

    repo = Path(repo_path)
    apps_client_dir = repo / "apps" / env / client_name
    tenants_client_dir = repo / "tenants" / env / client_name

    # --- 2. Catch / Validation (Duplicate Check) ---
    if apps_client_dir.exists() or tenants_client_dir.exists():
        print(
            f"❌ Error: Client '{client_name}' folders already exist in main repo! Automation stopped."
        )
        sys.exit(1)

    # --- 3. Git Operations (Checkout Master -> Pull -> Create Branch) ---
    print("\n🔄 Step 1: Starting Git Operations...")
    print("🌿 Checking out to master...")
    run_git_command(["git", "checkout", "master"], repo_path)

    print("📥 Pulling latest changes from remote master...")
    run_git_command(["git", "pull"], repo_path)

    new_branch = f"feature/{case_number}"
    print(f"🌿 Creating and switching to new branch: {new_branch}")
    run_git_command(["git", "checkout", "-b", new_branch], repo_path)
    print("✅ Git operations completed successfully.")

    # --- 4. Directory Creation & File Copy ---
    print("\n📁 Step 2: Creating directories and copying 4.0 files...")

    # Main tenant directory तयार करणे
    tenants_client_dir.mkdir(parents=True, exist_ok=False)

    # 1010, 7101, 7102 मॉड्युल्स लिस्ट
    modules = ["1010", "7101", "7102"]

    # A. tenant.conf कॉपी करणे (Main tenants फोल्डरमध्ये)
    src_tenant = source_v4_folder / "tenant.conf"
    dest_tenant = tenants_client_dir / "tenant.conf"
    if src_tenant.exists():
        shutil.copy(src_tenant, dest_tenant)
        print(f"  -> Copied: tenant.conf to tenants/{env}/{client_name}/")
    else:
        print(f"⚠️ Warning: Source tenant.conf not found at {src_tenant}")

    # B. 1010, 7101, 7102 च्या tenantapp.conf फाइल्स कॉपी करणे
    for module in modules:
        # Apps च्या आत प्रत्येक मॉड्युलचा स्वतंत्र फोल्डर तयार करणे
        (apps_client_dir / module).mkdir(parents=True, exist_ok=True)

        src_app_conf = source_v4_folder / module / "tenantapp.conf"
        dest_app_conf = apps_client_dir / module / "tenantapp.conf"

        if src_app_conf.exists():
            shutil.copy(src_app_conf, dest_app_conf)
            print(
                f"  -> Copied: {module}/tenantapp.conf to apps/{env}/{client_name}/{module}/"
            )
        else:
            print(f"⚠️ Warning: Source {module}/tenantapp.conf not found!")

    print("\n🚀 All Done! Git branch is ready and 4.0 file structure is copied.")


if __name__ == "__main__":
    create_and_sync_instance()