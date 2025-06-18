#!/usr/bin/env python3
"""
Cleanup script to identify and optionally remove Weaviate-related code
from the codebase as part of the migration to OpenAI Vector Store.
"""

import os
import re
import argparse
import shutil
from datetime import datetime

# Files that are known to be Weaviate-related and can be safely removed
WEAVIATE_FILES = [
    "services/weaviate_service.py",
    "services/mock_weaviate.py",
    "services/ocr_weaviate.py",
]

# Files that need to be checked for Weaviate references
FILES_TO_CHECK = [
    "app.py",
    "services/ocr_service.py",
    "routes/document_routes.py",
    "routes/ai_query_routes.py",
]

# Patterns to look for in files
WEAVIATE_PATTERNS = [
    r"import\s+weaviate",
    r"from\s+weaviate",
    r"weaviate\.",
    r"WeaviateService",
    r"mock_weaviate",
    r"ocr_weaviate",
]

def backup_file(file_path):
    """Create a backup of a file before modifying it"""
    backup_path = f"{file_path}.bak.{datetime.now().strftime('%Y%m%d%H%M%S')}"
    shutil.copy2(file_path, backup_path)
    print(f"Created backup: {backup_path}")
    return backup_path

def scan_directory(base_dir, dry_run=True):
    """Scan the directory for Weaviate-related files and code"""
    results = {
        "files_to_remove": [],
        "files_with_references": {}
    }
    
    # Check for known Weaviate files
    for weaviate_file in WEAVIATE_FILES:
        full_path = os.path.join(base_dir, weaviate_file)
        if os.path.exists(full_path):
            results["files_to_remove"].append(full_path)
    
    # Check other files for Weaviate references
    for check_file in FILES_TO_CHECK:
        full_path = os.path.join(base_dir, check_file)
        if os.path.exists(full_path):
            with open(full_path, 'r') as f:
                content = f.read()
                
            matches = []
            for pattern in WEAVIATE_PATTERNS:
                found = re.findall(pattern, content)
                if found:
                    matches.extend(found)
            
            if matches:
                results["files_with_references"][full_path] = matches
    
    return results

def remove_files(files, dry_run=True):
    """Remove the specified files"""
    for file_path in files:
        if dry_run:
            print(f"Would remove file: {file_path}")
        else:
            backup_file(file_path)
            os.remove(file_path)
            print(f"Removed file: {file_path}")

def main():
    parser = argparse.ArgumentParser(description='Cleanup Weaviate-related code')
    parser.add_argument('--backend-dir', default='./backend', 
                        help='Path to the backend directory')
    parser.add_argument('--frontend-dir', default='./frontend/src', 
                        help='Path to the frontend source directory')
    parser.add_argument('--remove', action='store_true', 
                        help='Actually remove files (default is dry run)')
    
    args = parser.parse_args()
    
    # Scan backend
    print("Scanning backend for Weaviate references...")
    backend_results = scan_directory(args.backend_dir, not args.remove)
    
    print("\nWeaviate files to remove:")
    for file_path in backend_results["files_to_remove"]:
        print(f"  - {file_path}")
    
    print("\nFiles with Weaviate references:")
    for file_path, references in backend_results["files_with_references"].items():
        print(f"  - {file_path}: {len(references)} references")
        for ref in references[:5]:  # Show first 5 references
            print(f"    - {ref}")
        if len(references) > 5:
            print(f"    - ... and {len(references) - 5} more")
    
    # Remove files if requested
    if args.remove:
        print("\nRemoving Weaviate files...")
        remove_files(backend_results["files_to_remove"], dry_run=False)
        print("\nNOTE: Files with Weaviate references need to be manually updated.")
    else:
        print("\nThis was a dry run. Use --remove to actually remove files.")
    
    # Frontend scan would be similar but would need to be adapted for TypeScript/JavaScript

if __name__ == "__main__":
    main()
