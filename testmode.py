#!/usr/bin/env python3
"""
NYC ODCV Test Deployment Script
Generates homepage + top 5 building reports for testing
Deploys to separate GitHub branch and folder
"""

import subprocess
import os
import shutil
import sys

# === CONFIGURATION ===
SOURCE_DIR = "/Users/forrestmiller/Desktop/New"
TEST_DIR = "/Users/forrestmiller/Desktop/NYC Test"
TEST_REPO = "https://github.com/fmillerrzero/nyc-test-site.git"

# Top 5 BBLs from odcv_scoring.csv (hardcoded)
TEST_BBLS = [1009950005, 1000940025, 1010160036, 1012670001, 1013010001]

def run_command(cmd, cwd=None):
    """Run a shell command and handle errors"""
    try:
        result = subprocess.run(cmd, shell=True, check=True, cwd=cwd, 
                              capture_output=True, text=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed: {cmd}")
        print(f"Error: {e.stderr}")
        return None

def modify_building_script():
    """Create modified building.py that only processes test BBLs"""
    original_file = os.path.join(SOURCE_DIR, "building.py")
    temp_file = os.path.join(TEST_DIR, "temp_building_test.py")
    
    print("🔧 Creating modified building script...")
    
    # Read original file
    with open(original_file, 'r') as f:
        content = f.read()
    
    # Find the main loop and modify it
    # Look for: for i, row in scoring.iterrows():
    modified_content = content.replace(
        "# For each building\nfor i, row in scoring.iterrows():",
        f"""# For each building - TEST MODE: Only process specific BBLs
test_bbls = {TEST_BBLS}
scoring_filtered = scoring[scoring['bbl'].isin(test_bbls)]
print(f"TEST MODE: Processing {{len(scoring_filtered)}} buildings: {TEST_BBLS}")
for i, row in scoring_filtered.iterrows():"""
    )
    
    # Also modify the output directory to save to test folder
    modified_content = modified_content.replace(
        'with open(f"{bbl}.html", \'w\') as f:',
        f'with open(f"{TEST_DIR}/{bbl}.html", \'w\') as f:'
    )
    
    # Write modified file
    with open(temp_file, 'w') as f:
        f.write(modified_content)
    
    return temp_file

def modify_homepage_script():
    """Create modified homepage.py that outputs to test folder"""
    original_file = os.path.join(SOURCE_DIR, "homepage.py")
    temp_file = os.path.join(TEST_DIR, "temp_homepage_test.py")
    
    print("🔧 Creating modified homepage script...")
    
    # Read original file
    with open(original_file, 'r') as f:
        content = f.read()
    
    # Modify the output path
    modified_content = content.replace(
        "with open('index.html', 'w', encoding='utf-8') as f:",
        f"with open('{TEST_DIR}/index.html', 'w', encoding='utf-8') as f:"
    )
    
    # Write modified file
    with open(temp_file, 'w') as f:
        f.write(modified_content)
    
    return temp_file

def setup_git_branch():
    """Set up the test repository"""
    print("🌿 Setting up Git repository...")
    
    # Change to test directory
    os.chdir(TEST_DIR)
    
    # Initialize git if needed
    if not os.path.exists('.git'):
        run_command("git init")
        run_command("git remote add origin https://github.com/fmillerrzero/nyc-test-site.git")
    
    # Fetch latest from remote
    run_command("git fetch origin")
    
    # Use main branch for test site
    run_command("git checkout -b main")
    # Try to pull if branch exists on remote
    run_command("git pull origin main --allow-unrelated-histories")

def deploy_to_github():
    """Add, commit, and push files to test repository"""
    print("📤 Deploying to GitHub test repository...")
    
    os.chdir(TEST_DIR)
    
    # Add all HTML files
    run_command("git add *.html")
    
    # Commit with timestamp
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    commit_msg = f"Test deployment - {timestamp} (5 buildings + homepage)"
    
    run_command(f'git commit -m "{commit_msg}"')
    
    # Push to main branch of test repository
    run_command("git push -u origin main")

def cleanup_temp_files():
    """Remove temporary modified scripts"""
    temp_files = [
        os.path.join(TEST_DIR, "temp_building_test.py"),
        os.path.join(TEST_DIR, "temp_homepage_test.py")
    ]
    
    for temp_file in temp_files:
        if os.path.exists(temp_file):
            os.remove(temp_file)
            print(f"🗑️  Cleaned up {os.path.basename(temp_file)}")

def main():
    print("\n🌆 NYC ODCV Test Deployment 🌆")
    print(f"📁 Test folder: {TEST_DIR}")
    print(f"🎯 Building BBLs: {TEST_BBLS}")
    print(f"🌿 Git repository: nyc-test-site")
    
    # Confirm deployment
    confirm = input("\n🚀 Deploy test version? (y/n): ")
    if confirm.lower() != 'y':
        print("❌ Cancelled.")
        return
    
    try:
        # Ensure test directory exists
        os.makedirs(TEST_DIR, exist_ok=True)
        
        # Step 1: Generate modified homepage
        print("\n📋 Generating test homepage...")
        homepage_script = modify_homepage_script()
        os.chdir(SOURCE_DIR)  # Run from source directory to access data files
        run_command(f"python3 '{homepage_script}'")
        
        # Step 2: Generate modified building reports
        print(f"\n🏢 Generating {len(TEST_BBLS)} test building reports...")
        building_script = modify_building_script()
        run_command(f"python3 '{building_script}'")
        
        # Step 3: Set up Git and deploy
        setup_git_branch()
        deploy_to_github()
        
        # Cleanup
        cleanup_temp_files()
        
        print(f"\n✅ Test deployment completed successfully!")
        print(f"🌐 View at: https://fmillerrzero.github.io/nyc-test-site/")
        print(f"📁 Local files: {TEST_DIR}")
        
    except Exception as e:
        print(f"\n❌ Deployment failed: {e}")
        cleanup_temp_files()
        sys.exit(1)

if __name__ == "__main__":
    main()