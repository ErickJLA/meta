#!/usr/bin/env python3
"""Fix K-H indentation: add 8 spaces to lines 724-823"""

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
print(f"Total lines in cell: {len(lines)}")

# K-H section: lines 724 to 824 (exclusive)
KH_START = 724
KH_END = 824

print(f"\nFixing K-H section (lines {KH_START} to {KH_END-1})...")

# Fix the lines
fixed_count = 0
for i in range(KH_START, KH_END):
    line = lines[i]

    # Skip empty lines or lines that are just \n
    if line.strip() == '':
        continue

    # Check current indentation
    stripped = line.lstrip()
    current_indent = len(line) - len(stripped)

    # If less than 8 spaces, add 8 spaces
    if current_indent < 8:
        lines[i] = '        ' + stripped
        fixed_count += 1

# Update notebook
nb['cells'][target_idx]['source'] = lines

# Save
print(f"Saving notebook...")
with open(notebook_path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

print(f"\n✅ Done! Fixed {fixed_count} lines")
print(f"   Lines {KH_START}-{KH_END-1} now have proper indentation (8 spaces)")
