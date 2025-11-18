#!/usr/bin/env python3
"""Fix K-H indentation by adding 8 spaces to all K-H lines"""

import json

notebook_path = '/home/user/meta/Meta_3_3.ipynb'

# Read notebook
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

if target_idx is None:
    print("ERROR: Could not find target cell")
    exit(1)

print(f"Found target cell at index {target_idx}")

# Get lines
lines = nb['cells'][target_idx]['source']

# Find K-H section
kh_start = None
kh_end = None

for i, line in enumerate(lines):
    # Find start: the comment line before "APPLY KNAPP-HARTUNG"
    if 'APPLY KNAPP-HARTUNG CORRECTION (if enabled)' in line:
        # Go back to find the ==== line
        for j in range(i-1, max(0, i-10), -1):
            if '# ============' in lines[j]:
                kh_start = j
                break
        if kh_start is None:
            kh_start = i

    # Find end: look for "# Display results" with 8 spaces
    if kh_start is not None and kh_end is None and i > kh_start + 10:
        if '# Display results' in line and line.startswith('        #'):
            kh_end = i
            break

if kh_start is None or kh_end is None:
    print(f"ERROR: Could not find K-H boundaries (start={kh_start}, end={kh_end})")
    exit(1)

print(f"K-H section: lines {kh_start} to {kh_end-1}")
print(f"Total lines to fix: {kh_end - kh_start}")

# Fix: Add 8 spaces to lines that don't have proper indentation
fixed_lines = []
for i in range(kh_start, kh_end):
    line = lines[i]

    # Empty line or just \n
    if line.strip() == '':
        fixed_lines.append(line)
        continue

    # Count leading spaces
    stripped = line.lstrip()
    leading_spaces = len(line) - len(stripped)

    if leading_spaces < 8 and stripped:
        # Need to add 8 spaces
        fixed_lines.append('        ' + stripped)
    else:
        # Already has 8+ spaces, keep as-is
        fixed_lines.append(line)

# Rebuild cell
new_cell_lines = lines[:kh_start] + fixed_lines + lines[kh_end:]

# Update
nb['cells'][target_idx]['source'] = new_cell_lines

# Save
with open(notebook_path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

print(f"\n✅ Fixed {len(fixed_lines)} lines")
print("Done!")
