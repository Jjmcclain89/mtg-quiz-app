#!/usr/bin/env python3
"""
File Combiner Script for Claude Import

This script combines multiple files into claude_input.txt with clear formatting
for easy import into Claude conversations.

Usage:
    python file_combiner.py file1.py file2.js config.json
    python file_combiner.py src/*.py docs/*.md
"""

import sys
import os
import argparse
from pathlib import Path
import glob


def get_file_type_comment(file_path):
    """Return appropriate comment syntax based on file extension."""
    ext = Path(file_path).suffix.lower()
    
    comment_styles = {
        '.py': '#',
        '.js': '//',
        '.ts': '//',
        '.java': '//',
        '.cpp': '//',
        '.c': '//',
        '.h': '//',
        '.hpp': '//',
        '.cs': '//',
        '.php': '//',
        '.rb': '#',
        '.sh': '#',
        '.yml': '#',
        '.yaml': '#',
        '.sql': '--',
        '.html': '<!--',
        '.xml': '<!--',
        '.css': '/*',
        '.scss': '//',
        '.less': '//',
    }
    
    return comment_styles.get(ext, '#')


def combine_files(file_paths, output_file):
    """Combine multiple files into a single formatted output."""
    
    output = open(output_file, 'w', encoding='utf-8')
    
    try:
        # Write header
        output.write("=" * 80 + "\n")
        output.write("COMBINED FILES FOR CLAUDE IMPORT\n")
        output.write(f"Generated from {len(file_paths)} files\n")
        output.write("=" * 80 + "\n\n")
        
        # Write table of contents
        output.write("TABLE OF CONTENTS:\n")
        for i, file_path in enumerate(file_paths, 1):
            output.write(f"{i:2d}. {file_path}\n")
        output.write("\n" + "=" * 80 + "\n\n")
        
        # Process each file
        for file_path in file_paths:
            try:
                # Resolve any glob patterns and relative paths
                resolved_path = Path(file_path).resolve()
                
                if not resolved_path.exists():
                    output.write(f"ERROR: File not found: {file_path}\n\n")
                    continue
                
                if resolved_path.is_dir():
                    output.write(f"SKIPPING: {file_path} (is a directory)\n\n")
                    continue
                
                # Read file content
                try:
                    with open(resolved_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                except UnicodeDecodeError:
                    # Try reading as binary for non-text files
                    output.write(f"SKIPPING: {file_path} (binary file or encoding issue)\n\n")
                    continue
                
                # Write file header
                output.write("=" * 60 + "\n")
                output.write(f"FILE: {file_path}\n")
                output.write(f"PATH: {resolved_path}\n")
                output.write(f"SIZE: {len(content)} characters\n")
                output.write("=" * 60 + "\n")
                
                # Write content
                if content.strip():
                    output.write(content)
                    # Ensure file ends with newline
                    if not content.endswith('\n'):
                        output.write('\n')
                else:
                    output.write("(Empty file)\n")
                
                output.write("\n\n")
                
            except Exception as e:
                output.write(f"ERROR reading {file_path}: {str(e)}\n\n")
        
        # Write footer
        output.write("=" * 80 + "\n")
        output.write("END OF COMBINED FILES\n")
        output.write("=" * 80 + "\n")
        
    finally:
        output.close()


def expand_glob_patterns(patterns):
    """Expand glob patterns and return list of actual file paths."""
    files = []
    for pattern in patterns:
        if '*' in pattern or '?' in pattern:
            # Expand glob pattern
            expanded = glob.glob(pattern, recursive=True)
            if expanded:
                files.extend(expanded)
            else:
                print(f"Warning: No files matched pattern '{pattern}'", file=sys.stderr)
        else:
            files.append(pattern)
    return files


def main():
    parser = argparse.ArgumentParser(
        description="Combine multiple files into claude_input.txt for Claude import",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s file1.py file2.js
  %(prog)s src/*.py
  %(prog)s "src/**/*.py" docs/*.md
  %(prog)s $(find . -name "*.py" -type f)
        """
    )
    
    parser.add_argument(
        'files',
        nargs='+',
        help='File paths to combine (supports glob patterns like src/*.py)'
    )
    
    parser.add_argument(
        '--recursive',
        action='store_true',
        help='Enable recursive glob patterns (e.g., src/**/*.py)'
    )
    
    args = parser.parse_args()
    
    # Expand glob patterns
    file_paths = expand_glob_patterns(args.files)
    
    if not file_paths:
        print("Error: No files specified or found", file=sys.stderr)
        return 1
    
    # Remove duplicates while preserving order
    seen = set()
    unique_files = []
    for f in file_paths:
        if f not in seen:
            seen.add(f)
            unique_files.append(f)
    
    print(f"Combining {len(unique_files)} files...", file=sys.stderr)
    
    try:
        combine_files(unique_files, "claude_input.txt")
        print(f"Combined files written to: claude_input.txt", file=sys.stderr)
        return 0
    except KeyboardInterrupt:
        print("\nOperation cancelled", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())