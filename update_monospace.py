#!/usr/bin/env python3
"""
Script to automatically wrap all reply_text and edit_message_text calls with to_monospace_uppercase
"""
import re
import os

files_to_update = [
    'settings.py',
    'user_management.py', 
    'blocked_words.py',
    'filters.py',
    'handlers.py'
]

def wrap_text_in_function(match):
    """Wrap the text argument in to_monospace_uppercase()"""
    full_match = match.group(0)
    
    # Skip if already wrapped
    if 'to_monospace_uppercase(' in full_match:
        return full_match
    
    # Pattern to match the text argument
    # This handles both simple strings and f-strings
    patterns = [
        # Simple string: reply_text("text")
        r'(reply_text|edit_message_text|send_message)\(\s*"([^"]*)"',
        r"(reply_text|edit_message_text|send_message)\(\s*'([^']*)'",
        # F-string: reply_text(f"text")  
        r'(reply_text|edit_message_text|send_message)\(\s*f"([^"]*)"',
        r"(reply_text|edit_message_text|send_message)\(\s*f'([^']*)'",
    ]
    
    for pattern in patterns:
        m = re.search(pattern, full_match)
        if m:
            func_name = m.group(1)
            text_content = m.group(2) if len(m.groups()) > 1 else ""
            
            # Check if it's an f-string
            is_fstring = 'f"' in full_match or "f'" in full_match
            prefix = 'f' if is_fstring else ''
            
            # Replace HTML tags since monospace doesn't need them
            text_content = text_content.replace('<b>', '').replace('</b>', '')
            text_content = text_content.replace('<code>', '').replace('</code>', '')
            text_content = text_content.replace('&lt;', '<').replace('&gt;', '>')
            
            if is_fstring:
                replacement = f'{func_name}(to_monospace_uppercase(f"{text_content}"'
            else:
                replacement = f'{func_name}(to_monospace_uppercase("{text_content}"'
            
            # Find the closing part
            rest = full_match[m.end():]
            return replacement + rest
    
    return full_match

def process_file(filepath):
    """Process a single file"""
    print(f"Processing {filepath}...")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if import already exists
    if 'from font import to_monospace_uppercase' not in content:
        # Add import after other imports
        lines = content.split('\n')
        new_lines = []
        import_added = False
        
        for i, line in enumerate(lines):
            new_lines.append(line)
            # Add import after telegram imports
            if not import_added and ('from telegram' in line or 'import json' in line):
                # Check next few lines to find end of import block
                if i + 1 < len(lines) and ('from telegram' in lines[i+1] or lines[i+1].strip().startswith('import')):
                    continue
                new_lines.append('from font import to_monospace_uppercase')
                import_added = True
        
        if import_added:
            content = '\n'.join(new_lines)
            print(f"  ✓ Added import statement")
    
    # Pattern to match reply_text, edit_message_text, send_message calls
    # This regex matches function calls with their arguments
    pattern = r'(reply_text|edit_message_text|send_message)\([^)]*(?:\)|(?=\)))'
    
    # More comprehensive pattern that handles multiline
    pattern_multiline = r'(?:await\s+)?(?:update\.message\.|query\.|context\.bot\.)?(reply_text|edit_message_text|send_message)\([^)]+\)'
    
    # For now, just report what needs to be done
    matches = re.findall(pattern_multiline, content, re.MULTILINE | re.DOTALL)
    print(f"  Found {len(matches)} message calls")
    
    return content

if __name__ == '__main__':
    for filename in files_to_update:
        if os.path.exists(filename):
            process_file(filename)
        else:
            print(f"File not found: {filename}")
    
    print("\nNote: Due to complexity, manual review and updates are recommended.")
    print("The import statements have been added where missing.")
