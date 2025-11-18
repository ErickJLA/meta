#!/usr/bin/env python3
"""Fix K-H indentation properly:
- if statement: 8 spaces
- content inside if: 12 spaces
- nested if content: 16 spaces
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

# Find K-H section boundaries
KH_START = None
KH_END = None

for i, line in enumerate(lines):
    if 'APPLY KNAPP-HARTUNG CORRECTION (if enabled)' in line:
        # Go back to find ===
        for j in range(i-1, max(0, i-5), -1):
            if '# ============' in lines[j]:
                KH_START = j
                break
    if KH_START and '# Display results' in line and '        #' in line:
        KH_END = i
        break

if not KH_START or not KH_END:
    print(f"ERROR: Could not find boundaries (start={KH_START}, end={KH_END})")
    exit(1)

print(f"\nK-H section: lines {KH_START} to {KH_END-1}")

# Fix indentation properly
# Track nesting level
current_indent = 8  # Start at 8 (inside else block)
fixed_count = 0

for i in range(KH_START, KH_END):
    line = lines[i]

    # Skip pure whitespace lines
    if line.strip() == '':
        continue

    stripped = line.lstrip()

    # Determine proper indentation based on content
    if stripped.startswith('#'):
        # Comments follow current indent level
        new_line = ' ' * current_indent + stripped
    elif stripped.startswith('if '):
        # if statement at current level
        new_line = ' ' * current_indent + stripped
        current_indent += 4  # Increase for content inside if
    elif stripped.startswith('elif ') or stripped.startswith('else:'):
        # Decrease first, then apply
        current_indent -= 4
        new_line = ' ' * current_indent + stripped
        current_indent += 4  # Increase again for content
    elif 'print(' in stripped or stripped.startswith('kh_results') or \
         stripped.startswith('pooled_') or stripped.startswith('ci_') or \
         stripped.startswith('p_value') or stripped.startswith('ANALYSIS_CONFIG'):
        # Regular statements inside current block
        new_line = ' ' * current_indent + stripped
    elif stripped.startswith('yi=') or stripped.startswith('vi=') or \
         stripped.startswith('tau_sq=') or stripped.startswith('pooled_effect=') or \
         stripped.startswith('alpha='):
        # Function parameters - add extra indentation
        new_line = ' ' * (current_indent + 4) + stripped
    else:
        # Default: use current indent
        new_line = ' ' * current_indent + stripped

    if new_line != line:
        lines[i] = new_line
        fixed_count += 1

# Update notebook
nb['cells'][target_idx]['source'] = lines

# Save
print(f"Saving notebook...")
with open(notebook_path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

print(f"\n✅ Done! Fixed {fixed_count} lines with proper indentation")
