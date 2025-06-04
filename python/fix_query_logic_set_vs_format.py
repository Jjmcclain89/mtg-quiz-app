#!/usr/bin/env python3
"""
Fix Query Logic - Set vs Format Filter Script
Updates the search query logic so format filter is only used when no specific set is selected
"""

import os
from pathlib import Path

def update_scryfall_service():
    """Update the buildSearchQuery function to use proper set vs format logic"""
    
    # Read the current file
    service_file = Path('src/services/scryfall.ts')
    if not service_file.exists():
        print("❌ Error: Scryfall service file not found!")
        return False
    
    with open(service_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Simple approach: replace the specific logic inside the function
    # Find the current implementation and replace it
    old_logic = '''  if (format && format !== 'all') {
    queryParts.push(`format:${format}`);
  }
  
  if (setCode && setCode !== 'all') {
    queryParts.push(`set:${setCode}`);
  }'''
    
    new_logic = '''  // If a specific set is selected, only use the set filter (don't include format)
  if (setCode && setCode !== 'all') {
    queryParts.push(`set:${setCode}`);
  } else {
    // Only use format filter when no specific set is selected ("all sets")
    if (format && format !== 'all') {
      queryParts.push(`format:${format}`);
    }
  }'''
    
    # Replace the logic
    if old_logic in content:
        updated_content = content.replace(old_logic, new_logic)
        
        # Write the updated content back
        with open(service_file, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        print(f"✅ Updated buildSearchQuery function logic in: {service_file}")
        return True
    else:
        print("❌ Could not find the expected buildSearchQuery logic to replace!")
        print("The function may have been modified or have different formatting.")
        return False

def main():
    """Main function to fix the query logic"""
    
    print("🔧 Fixing Query Logic - Set vs Format Filter")
    print("=" * 60)
    
    # Verify we're in the right directory
    if not os.path.exists('package.json'):
        print("❌ Error: package.json not found!")
        print("   Make sure you're running this from the mtg-quiz-app/ root directory")
        return False
    
    # Verify the service file exists
    if not os.path.exists('src/services/scryfall.ts'):
        print("❌ Error: Scryfall API service not found!")
        print("   Please run the setup_scryfall_api_foundation.py script first")
        return False
    
    try:
        # Update the buildSearchQuery function
        success = update_scryfall_service()
        
        if success:
            print("=" * 60)
            print("✅ Query Logic Fixed!")
            print()
            print("🔧 New Search Logic:")
            print("   • Set selected → Only use set filter (no format filter)")
            print("   • All sets + Format → Use format filter to show cards legal in format")
            print("   • All sets + All formats → Search all cards")
            print()
            print("📊 Query Examples:")
            print("   • Format: Standard, Set: Aetherdrift → 'set:dft' (only set, no format)")
            print("   • Format: Standard, Set: All Sets → 'format:standard' (all Standard cards)")
            print("   • Format: All, Set: Bloomburrow → 'set:blb' (only set, no format)")
            print("   • Format: All, Set: All Sets → '*' (all cards)")
            print()
            print("🎯 Benefits:")
            print("   • More logical filtering behavior")
            print("   • Set selection overrides format filter when specific set chosen")
            print("   • Format filter only applies when browsing 'All Sets'")
            print("   • Cleaner API queries with better performance")
            print("   • Less redundant filtering (set already constrains results)")
            print()
            print("🧪 Test Your Fix:")
            print("   1. Refresh browser")
            print("   2. Select Standard format + specific set → should show only that set's cards")
            print("   3. Select Standard format + All Sets → should show all Standard-legal cards")
            print("   4. Check browser Network tab to verify query URLs")
            print("   5. Verify search results make logical sense")
            
        return success
        
    except Exception as e:
        print(f"❌ Error during fix: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
