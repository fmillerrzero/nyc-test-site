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

def run_command(cmd, cwd=None, show_output=False):
    """Run a shell command and handle errors"""
    try:
        if show_output:
            # Run without capturing output so it shows in terminal
            result = subprocess.run(cmd, shell=True, check=True, cwd=cwd)
            return "Success"
        else:
            result = subprocess.run(cmd, shell=True, check=True, cwd=cwd, 
                                  capture_output=True, text=True)
            return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed: {cmd}")
        if not show_output and hasattr(e, 'stderr'):
            print(f"Error: {e.stderr}")
        return None

def modify_building_script(version_text):
    """Create modified building.py that only processes test BBLs"""
    original_file = os.path.join(SOURCE_DIR, "building.py")
    temp_file = os.path.join(TEST_DIR, "temp_building_test.py")
    
    print("🔧 Creating modified building script...")
    
    # Step 1: COPY - Copy the original file exactly as-is
    shutil.copy2(original_file, temp_file)
    print("   ✓ Copied building.py")
    
    # Step 2: EDIT - Read the copy and modify it
    with open(temp_file, 'r') as f:
        content = f.read()
    
    # Apply modifications
    modified_content = content
    
    # Modification 1: Change all data file paths to use current directory
    # The building script uses relative paths like 'data/file.csv'
    # No need to change since we're running from TEST_DIR which has data/
    
    # Modification 2: Filter to test BBLs only
    modified_content = modified_content.replace(
        "# For each building\nfor i, row in scoring.iterrows():",
        f"""# For each building - TEST MODE: Only process specific BBLs
test_bbls = {TEST_BBLS}
scoring_filtered = scoring[scoring['bbl'].isin(test_bbls)]
print(f"TEST MODE: Processing {{len(scoring_filtered)}} buildings: {TEST_BBLS}")
for i, row in scoring_filtered.iterrows():"""
    )
    
    # Modification 3: Change output directory
    modified_content = modified_content.replace(
        'with open(f"{bbl}.html", \'w\') as f:',
        f'with open(f"{{bbl}}.html", \'w\') as f:'
    )
    
    # Modification 4: Change GitHub URLs to test site
    modified_content = modified_content.replace(
        "https://raw.githubusercontent.com/fmillerrzero/nyc-odcv-site/main/",
        "https://raw.githubusercontent.com/fmillerrzero/nyc-test-site/main/"
    )
    
    # Modification 5: Add version text
    modified_content = modified_content.replace(
        "Build: {datetime.now(pytz.timezone('America/Mexico_City')).strftime('%I:%M:%S %p CST')}",
        f"Build: {{datetime.now(pytz.timezone('America/Mexico_City')).strftime('%I:%M:%S %p CST')}} | {version_text}"
    )
    
    # Write modifications back to the temp file
    with open(temp_file, 'w') as f:
        f.write(modified_content)
    print("   ✓ Applied modifications")
    
    return temp_file

def modify_homepage_script(version_text):
    """Create modified homepage.py that outputs to test folder"""
    original_file = os.path.join(SOURCE_DIR, "homepage.py")
    temp_file = os.path.join(TEST_DIR, "temp_homepage_test.py")
    
    print("🔧 Creating modified homepage script...")
    
    # Step 1: COPY - Copy the original file exactly as-is
    shutil.copy2(original_file, temp_file)
    print("   ✓ Copied homepage.py")
    
    # Step 2: EDIT - Read the copy and modify it
    with open(temp_file, 'r') as f:
        content = f.read()
    
    # Apply modifications
    modified_content = content
    
    # Modification 1: Change output path
    modified_content = modified_content.replace(
        "with open('index.html', 'w', encoding='utf-8') as f:",
        f"with open('{TEST_DIR}/index.html', 'w', encoding='utf-8') as f:"
    )
    
    # Modification 2: Filter to only show test BBLs
    # The homepage iterates through scoring dataframe, so we need to filter it
    modified_content = modified_content.replace(
        "scoring = pd.read_csv('data/odcv_scoring.csv')",
        f"""scoring = pd.read_csv('data/odcv_scoring.csv')
# TEST MODE: Filter to only test BBLs
test_bbls = {TEST_BBLS}
scoring = scoring[scoring['bbl'].isin(test_bbls)]
print(f"TEST MODE: Homepage will show {{len(scoring)}} buildings: {TEST_BBLS}")"""
    )
    
    # Modification 3: Change GitHub URLs to test site
    modified_content = modified_content.replace(
        "https://raw.githubusercontent.com/fmillerrzero/nyc-odcv-site/main/",
        "https://raw.githubusercontent.com/fmillerrzero/nyc-test-site/main/"
    )
    
    # Modification 4: Add version text
    modified_content = modified_content.replace(
        "Build: {datetime.now(pytz.timezone('America/Mexico_City')).strftime('%I:%M:%S %p CST')}",
        f"Build: {{datetime.now(pytz.timezone('America/Mexico_City')).strftime('%I:%M:%S %p CST')}} | {version_text}"
    )
    
    # Write modifications back to the temp file
    with open(temp_file, 'w') as f:
        f.write(modified_content)
    print("   ✓ Applied modifications")
    
    return temp_file

def setup_git_branch():
    """Set up the test repository"""
    print("🌿 Setting up Git repository...")
    
    # Change to test directory
    os.chdir(TEST_DIR)
    
    # Git is already set up, just make sure we're in the right place
    # No need to create branches or do anything else

def deploy_to_github(version_text):
    """Add, commit, and push files to test repository"""
    print("📤 Deploying to GitHub test repository...")
    
    os.chdir(TEST_DIR)
    
    # Add all HTML files
    run_command("git add *.html")
    
    # Check if there are changes to commit
    status = run_command("git status --porcelain")
    if not status:
        print("   ℹ️  No changes to commit")
        return
    
    # Use version text as commit message
    commit_msg = version_text
    
    result = run_command(f'git commit -m "{commit_msg}"')
    if result is None:
        print("   ⚠️  Commit failed, but continuing...")
        return
    
    # Push to main branch of test repository
    push_result = run_command("git push -u origin main")
    if push_result is None:
        print("   ⚠️  Push failed")
    else:
        print("   ✓ Pushed to GitHub")

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
    print(f"📦 Test repo: nyc-test-site")
    print(f"🌐 Test site URL: https://fmillerrzero.github.io/nyc-test-site/")
    
    # Get version text
    version_text = input("\n📝 Version text (optional): ").strip()
    if not version_text:
        version_text = "Test Build"
    
    # Confirm deployment
    confirm = input(f"\n🚀 Deploy test version with '{version_text}'? (y/n): ")
    if confirm.lower() != 'y':
        print("❌ Cancelled.")
        return
    
    try:
        # Ensure test directory exists
        os.makedirs(TEST_DIR, exist_ok=True)
        
        # Step 1: Generate modified homepage
        print("\n📋 Generating test homepage...")
        homepage_script = modify_homepage_script(version_text)
        os.chdir(TEST_DIR)  # Run from test directory for full separation
        run_command(f"python3 '{homepage_script}'", show_output=True)
        
        # Step 2: Generate modified building reports
        print(f"\n🏢 Generating {len(TEST_BBLS)} test building reports...")
        building_script = modify_building_script(version_text)
        result = run_command(f"python3 '{building_script}'", show_output=True)
        if result is None:
            print("   ⚠️  Building script failed!")
        
        # Step 3: Set up Git and deploy
        setup_git_branch()
        deploy_to_github(version_text)
        
        # Cleanup
        cleanup_temp_files()
        
        print(f"\n✅ Test deployment completed successfully!")
        print(f"📁 Local files: {TEST_DIR}")
        print(f"🔗 GitHub repository: https://github.com/fmillerrzero/nyc-test-site")
        print(f"🌐 View test site: https://fmillerrzero.github.io/nyc-test-site/")
        
    except Exception as e:
        print(f"\n❌ Deployment failed: {e}")
        cleanup_temp_files()
        sys.exit(1)

if __name__ == "__main__":
    main()