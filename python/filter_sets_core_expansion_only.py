#!/usr/bin/env python3
"""
Filter Sets to Core and Expansion Only

This script updates the fetchSets function in scryfall.ts to only return sets
with set_type "core" and "expansion", filtering out supplemental products,
promos, funny sets, etc.
"""

import os
import sys
import re

def main():
    print("🔧 Filtering sets to core and expansion types only...")
    
    # Verify we're in the correct directory
    if not os.path.exists('src/services/scryfall.ts'):
        print("❌ Error: src/services/scryfall.ts not found")
        print("Please run this script from the mtg-quiz-app project root")
        return False
    
    # Read current scryfall service
    with open('src/services/scryfall.ts', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find and replace the fetchSets function
    fetchsets_pattern = r'export async function fetchSets\(\): Promise<ScryfallSet\[\]> \{[^}]+\}'
    
    # Look for the function more broadly if exact pattern doesn't match
    if not re.search(fetchsets_pattern, content, re.DOTALL):
        # Try a broader pattern
        fetchsets_pattern = r'export async function fetchSets\(\)[^{]*\{.*?\n\}'
    
    # Find the function using a more flexible approach
    start_marker = 'export async function fetchSets(): Promise<ScryfallSet[]> {'
    
    if start_marker not in content:
        print("❌ Could not find fetchSets function")
        return False
    
    # Find the start and end of the function
    start_pos = content.find(start_marker)
    
    # Find the matching closing brace
    brace_count = 0
    pos = start_pos + len(start_marker)
    brace_count = 1  # We already have one opening brace
    
    while pos < len(content) and brace_count > 0:
        if content[pos] == '{':
            brace_count += 1
        elif content[pos] == '}':
            brace_count -= 1
        pos += 1
    
    if brace_count != 0:
        print("❌ Could not find end of fetchSets function")
        return False
    
    end_pos = pos
    old_function = content[start_pos:end_pos]
    
    # Define the new function with filtering
    new_function = '''export async function fetchSets(): Promise<ScryfallSet[]> {
  try {
    const response = await makeRequest<ScryfallSetsResponse>('/sets');
    
    // Filter to only include core and expansion sets, then sort by release date
    const filteredSets = response.data
      .filter((set: ScryfallSet) => {
        return set.set_type === 'core' || set.set_type === 'expansion';
      })
      .sort((a: ScryfallSet, b: ScryfallSet) => 
        new Date(b.released_at).getTime() - new Date(a.released_at).getTime()
      );
    
    console.log(`Filtered ${response.data.length} total sets down to ${filteredSets.length} core/expansion sets`);
    
    return filteredSets;
  } catch (error) {
    console.error('Failed to fetch sets:', error);
    throw new ScryfallApiError('Failed to load MTG sets');
  }
}'''
    
    # Replace the old function with the new one
    new_content = content.replace(old_function, new_function)
    
    # Write the updated content back
    with open('src/services/scryfall.ts', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ Successfully updated fetchSets function!")
    print("📊 Changes made:")
    print("   • Added filtering for set_type === 'core' || set_type === 'expansion'")
    print("   • Maintained sorting by release date (newest first)")
    print("   • Added console logging to show filtering results")
    print("   • Preserves existing error handling")
    
    print("\n🗑️ This will filter out:")
    print("   • funny (Unglued, Unstable, etc.)")
    print("   • memorabilia (From the Vault, etc.)")
    print("   • token (token sets)")
    print("   • box (box sets)")
    print("   • promo (promotional sets)")
    print("   • draft_innovation (draft boosters)")
    print("   • planechase, archenemy, vanguard, etc.")
    
    print("\n✅ This will keep:")
    print("   • core (Core Set 2019, 2020, 2021, etc.)")
    print("   • expansion (Standard sets, premier sets)")
    
    print("\n🚀 Test the changes:")
    print("   npm run dev")
    print("   • Check the sets dropdown - should be much cleaner")
    print("   • Should only see main Magic releases")
    print("   • Console will show filtering stats")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)