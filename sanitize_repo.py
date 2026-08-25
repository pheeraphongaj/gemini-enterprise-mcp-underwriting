"""Sanitize repository: Remove internal paths, project numbers, .pyc files, and add .gitignore."""

import os
import re
import shutil
import subprocess

REPO_DIR = "~/gemini-enterprise-mcp-underwriting"

# 1. Create .gitignore
gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv/

# Environment & Secrets
.env
*.token
*.key
*.pem

# Logs & OS
*.log
.DS_Store
.vscode/
.idea/
"""

with open(os.path.join(REPO_DIR, ".gitignore"), "w") as f:
    f.write(gitignore_content)
print("✅ Created .gitignore")

# 2. Remove all __pycache__ directories and .pyc files
for root, dirs, files in os.walk(REPO_DIR):
    if "__pycache__" in dirs:
        pycache_dir = os.path.join(root, "__pycache__")
        shutil.rmtree(pycache_dir)
        print(f"Removed {pycache_dir}")

# 3. Sanitize files: replace internal paths and specific IDs with clean variables/placeholders
replacements = [
    ("gcloud", "gcloud"),
    ("~/", "~/"),
    ("./", "./"),
    ("YOUR_PROJECT_NUMBER", "YOUR_PROJECT_NUMBER"),
    ("YOUR_ORG_ID", "YOUR_ORG_ID"),
]

for root, dirs, files in os.walk(REPO_DIR):
    if ".git" in dirs:
        dirs.remove(".git")
    for file in files:
        if file.endswith(".pyc"):
            continue
        filepath = os.path.join(root, file)
        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            new_content = content
            for old_val, new_val in replacements:
                new_content = new_content.replace(old_val, new_val)

            if new_content != content:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(new_content)
                print(f"✅ Sanitized {os.path.relpath(filepath, REPO_DIR)}")
        except Exception as e:
            print(f"Error sanitizing {filepath}: {e}")

# 4. Clean git index: remove cached .pyc and stage all changes
subprocess.run(["git", "rm", "-r", "--cached", "**/*.pyc"], cwd=REPO_DIR, shell=True)
subprocess.run(["git", "add", "."], cwd=REPO_DIR, check=True)
subprocess.run(["git", "commit", "-m", "Security & sanitization: remove internal paths, project numbers, and pycache"], cwd=REPO_DIR, check=True)

print("\n✅ All files sanitized and committed.")
