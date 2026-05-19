"""
ReportIQ Project Cleanup Script
Removes unnecessary and old files safely
"""

import os
import shutil
from pathlib import Path

# Get project root
ROOT = Path(__file__).parent

def safe_delete_folder(folder_path):
    """Safely delete a folder if it exists"""
    try:
        if folder_path.exists():
            shutil.rmtree(folder_path)
            print(f"✅ Deleted folder: {folder_path.name}")
            return True
        else:
            print(f"⚠️  Folder not found: {folder_path.name}")
            return False
    except Exception as e:
        print(f"❌ Error deleting {folder_path.name}: {e}")
        return False

def safe_delete_file(file_path):
    """Safely delete a file if it exists"""
    try:
        if file_path.exists():
            file_path.unlink()
            print(f"✅ Deleted file: {file_path.name}")
            return True
        else:
            print(f"⚠️  File not found: {file_path.name}")
            return False
    except Exception as e:
        print(f"❌ Error deleting {file_path.name}: {e}")
        return False

def main():
    print("=" * 60)
    print("🧹 ReportIQ Project Cleanup")
    print("=" * 60)
    print("\n⚠️  This will delete unnecessary files!")
    
    response = input("\nContinue? (yes/no): ").lower()
    
    if response != 'yes':
        print("❌ Cleanup cancelled.")
        return
    
    print("\n🗑️  Starting cleanup...\n")
    
    # Phase 1: Delete old frontend folder
    print("📁 Phase 1: Removing old frontend folder...")
    folders_to_delete = [
        ROOT / "frontend"
    ]
    
    for folder in folders_to_delete:
        safe_delete_folder(folder)
    
    # Phase 2: Delete old template files
    print("\n📄 Phase 2: Removing old template files...")
    template_files_to_delete = [
        ROOT / "templates" / "dashboard_voice.html",
        ROOT / "templates" / "feedbackhistory.html",
        ROOT / "templates" / "voice_query.html",
        ROOT / "templates" / "test.html"
    ]
    
    for file in template_files_to_delete:
        safe_delete_file(file)
    
    # Phase 3: Delete old JS files
    print("\n🔧 Phase 3: Removing old JavaScript files...")
    js_files_to_delete = [
        ROOT / "static" / "js" / "feedback.js"
    ]
    
    for file in js_files_to_delete:
        safe_delete_file(file)
    
    # Phase 4: Delete old documentation
    print("\n📚 Phase 4: Removing old documentation...")
    doc_files_to_delete = [
        ROOT / "CLEANUP_INSTRUCTIONS.md",
        ROOT / "DASHBOARD_VOICE_INTEGRATION.md",
        ROOT / "VOICE_FEATURE_GUIDE.md",
        ROOT / "cleanup_unnecessary_files.bat"
    ]
    
    for file in doc_files_to_delete:
        safe_delete_file(file)
    
    # Phase 5: Backup old CSS
    print("\n🎨 Phase 5: Backing up old CSS...")
    old_css = ROOT / "static" / "css" / "style.css"
    backup_css = ROOT / "static" / "css" / "style.css.backup"
    
    if old_css.exists() and not backup_css.exists():
        try:
            shutil.copy(old_css, backup_css)
            print(f"✅ Backed up: style.css → style.css.backup")
            print("   You can delete style.css.backup after testing")
        except Exception as e:
            print(f"❌ Error backing up CSS: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print("✅ Cleanup Complete!")
    print("=" * 60)
    print("\n📋 What was done:")
    print("  ✅ Removed old frontend folder")
    print("  ✅ Removed old template files")
    print("  ✅ Removed old JavaScript files")
    print("  ✅ Removed old documentation")
    print("  ✅ Backed up old CSS file")
    
    print("\n🧪 Next Steps:")
    print("  1. Test your application: start_reportiq.bat")
    print("  2. Check all pages work correctly")
    print("  3. If all works, you can delete style.css.backup")
    
    print("\n⚠️  Important Files Kept:")
    print("  ✅ modern-style.css (new CSS)")
    print("  ✅ main.js (main JavaScript)")
    print("  ✅ All new templates (index, dashboard, etc.)")
    print("  ✅ Backend code")
    print("  ✅ README.md and FRONTEND_UPGRADE.md")
    
    print("\n🎉 Your project is now clean and organized!")

if __name__ == "__main__":
    main()
