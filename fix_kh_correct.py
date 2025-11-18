#!/usr/bin/env python3
"""
Fix K-H indentation correctly:
- Lines 724-731: Comments and if statement = 8 spaces (already fixed)
- Lines 732-823: Content inside if block = need +4 more spaces
"""

import json

notebook_path = '/home/user/meta/Meta_3_3.ipynb'

print("Loading notebook...")
with open(notebook_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

# Find Cell 9
target_idx = None
for idx, cell in enumerate(nb['cells']):
    if cell['cell_type'] == 'code':
        source_text = ''.join(cell['source'])
        if 'OVERALL POOLED EFFECT SIZE & HETEROGENEITY' in source_text:
            target_idx = idx
            break

print(f"Found cell at index {target_idx}")

# Get source lines
lines = nb['cells'][target_idx]['source']

# Find the specific lines that need +4 spaces
# Start: line after "if k > 1 and use_kh_widget.value:"
# End: line before "# Display results" (which is at correct indentation)

# Find start
if_line_idx = None
for i in range(700, 750):
    if 'if k > 1 and use_kh_widget.value:' in lines[i]:
        if_line_idx = i
        break

# Find end
display_line_idx = None
for i in range(800, 850):
    if '# Display results' in lines[i] and lines[i].startswith('        #'):
        display_line_idx = i
        break

if not if_line_idx or not display_line_idx:
    print(f"ERROR: Could not find boundaries (if={if_line_idx}, display={display_line_idx})")
    exit(1)

print(f"Found if statement at line {if_line_idx}")
print(f"Found display results at line {display_line_idx}")

# Lines to fix: if_line_idx+1 to display_line_idx (exclusive)
# But skip:
# - Lines already at correct level (elif/else at same level as if)
# - Empty lines

START_FIX = if_line_idx + 1
END_FIX = display_line_idx

# First pass: check for elif/else that should stay at 8 spaces
elif_else_lines = set()
for i in range(START_FIX, END_FIX):
    line = lines[i]
    stripped = line.lstrip()
    if stripped.startswith('elif ') or stripped.startswith('else:'):
        if line.startswith('        ') and not line.startswith('            '):
            # This is at 8 spaces - keep it there
            elif_else_lines.add(i)

print(f"Fixing lines {START_FIX} to {END_FIX-1}...")
print(f"elif/else lines to skip: {elif_else_lines}")

# Fix: Add 4 spaces to all non-empty lines
fixed_count = 0
for i in range(START_FIX, END_FIX):
    line = lines[i]

    # Skip empty lines
    if line.strip() == '':
        continue

    # Skip elif/else lines that should stay at 8
    if i in elif_else_lines:
        continue

    # Count current leading spaces
    stripped = line.lstrip()
    current_spaces = len(line) - len(stripped)

    # Add 4 spaces
    lines[i] = '    ' + line
    fixed_count += 1

# Update notebook
nb['cells'][target_idx]['source'] = lines

# Save
print(f"Saving notebook...")
with open(notebook_path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

print(f"\n✅ Done! Added 4 spaces to {fixed_count} lines")
print(f"   Lines {START_FIX}-{END_FIX-1} now have correct indentation")
