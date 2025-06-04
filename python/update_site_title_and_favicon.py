#!/usr/bin/env python3
"""
Update Site Title and Favicon

This script updates the website title to "MTG Quiz" and configures
the HTML to use a locally saved MTG card back favicon.

Prerequisites: Save an MTG card back image as public/favicon.ico
"""

import os
import sys
import re
from pathlib import Path

def verify_favicon_exists():
    """Check if favicon.ico exists in public directory"""
    favicon_path = Path('public/favicon.ico')
    
    if favicon_path.exists():
        file_size = favicon_path.stat().st_size
        print(f"✅ Found favicon: {favicon_path} ({file_size} bytes)")
        return True
    else:
        print(f"❌ Favicon not found: {favicon_path}")
        print("\n📥 Please download an MTG card back image:")
        print("   1. Recommended: http://eakett.ca/mtgimage/back.png")
        print("   2. Alternative: https://cards.scryfall.io/large/back/6/7/67f4c93b-080c-4196-b095-6a120a221988.jpg")
        print("   3. Official: https://gatherer.wizards.com/Content/CardBack.png")
        print(f"\n💾 Save as: {favicon_path}")
        print("   Right-click URL → Save As... → public/favicon.ico")
        return False

def update_html_title_and_favicon():
    """Update the index.html file with new title and favicon reference"""
    print("📝 Updating index.html...")
    
    html_path = Path('index.html')
    
    if not html_path.exists():
        print("❌ index.html not found in project root")
        return False
    
    # Read current HTML
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Update title
    if '<title>' in html_content:
        # Replace existing title
        html_content = re.sub(r'<title>.*?</title>', '<title>MTG Quiz</title>', html_content, flags=re.IGNORECASE)
        print("✅ Updated page title to 'MTG Quiz'")
    else:
        # Add title if it doesn't exist
        head_pos = html_content.find('<head>')
        if head_pos != -1:
            insert_pos = html_content.find('>', head_pos) + 1
            html_content = html_content[:insert_pos] + '\n    <title>MTG Quiz</title>' + html_content[insert_pos:]
            print("✅ Added page title 'MTG Quiz'")
    
    # Remove existing favicon links
    html_content = re.sub(r'<link[^>]*rel=["\']icon["\'][^>]*>', '', html_content, flags=re.IGNORECASE)
    html_content = re.sub(r'<link[^>]*rel=["\']shortcut icon["\'][^>]*>', '', html_content, flags=re.IGNORECASE)
    
    # Add new favicon link
    favicon_html = '    <link rel="icon" type="image/x-icon" href="/favicon.ico">'
    
    # Insert favicon link in head section
    head_end = html_content.find('</head>')
    if head_end != -1:
        html_content = html_content[:head_end] + favicon_html + '\n  ' + html_content[head_end:]
        print("✅ Added favicon link to HTML")
    
    # Write updated HTML
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return True

def main():
    print("🎮 Updating MTG Quiz site title and favicon...")
    print("=" * 50)
    
    # Verify we're in the correct directory
    if not os.path.exists('public'):
        print("❌ Error: 'public' directory not found")
        print("Please run this script from the mtg-quiz-app project root")
        return False
    
    # Create public directory if it doesn't exist
    os.makedirs('public', exist_ok=True)
    
    # Check if favicon exists
    favicon_exists = verify_favicon_exists()
    
    if not favicon_exists:
        print("\n⚠️ Cannot proceed without favicon file")
        print("Please download and save the favicon first, then run this script again")
        return False
    
    # Update HTML
    html_success = update_html_title_and_favicon()
    
    print("\n" + "=" * 50)
    if html_success:
        print("🎉 Successfully updated site branding!")
        print("\n✅ Changes made:")
        print("   • Page title changed to 'MTG Quiz'")
        print("   • Favicon configured to use local public/favicon.ico")
        print("   • Updated HTML head section with proper favicon link")
        
        print("\n🚀 Test the changes:")
        print("   npm run dev")
        print("   • Check browser tab - should show 'MTG Quiz'")
        print("   • Check favicon - should show MTG card back")
        print("   • Hard refresh (Ctrl+F5) may be needed for favicon to update")
        
    else:
        print("❌ HTML update failed - check errors above")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)