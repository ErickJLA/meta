#!/usr/bin/env python3
"""Add K-H widget to the display VBox at end of Cell 9"""

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

# Find the VBox that displays widgets
# Look for "config_box = widgets.VBox([" and add kh widgets to it
vbox_start_idx = None
tau_method_idx = None
rerun_idx = None

for i, line in enumerate(lines):
    if 'config_box = widgets.VBox([' in line:
        vbox_start_idx = i
    if vbox_start_idx and 'tau_method_widget,' in line:
        tau_method_idx = i
    if vbox_start_idx and 'rerun_message' in line and '],' in lines[i+1]:
        rerun_idx = i
        break

if not vbox_start_idx or not tau_method_idx or not rerun_idx:
    print(f"ERROR: Could not find VBox (vbox={vbox_start_idx}, tau={tau_method_idx}, rerun={rerun_idx})")
    exit(1)

print(f"Found VBox at line {vbox_start_idx}")
print(f"  tau_method_widget at line {tau_method_idx}")
print(f"  rerun_message at line {rerun_idx}")

# Insert K-H widgets after tau_method_widget
kh_widget_lines = [
    "\n",
    "    kh_help,\n",
    "\n",
    "    use_kh_widget,\n"
]

# Insert at tau_method_idx + 1
insert_pos = tau_method_idx + 1
new_lines = lines[:insert_pos] + kh_widget_lines + lines[insert_pos:]

# Update notebook
nb['cells'][target_idx]['source'] = new_lines

# Save
print(f"Saving notebook...")
with open(notebook_path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

print(f"\n✅ Done! Added K-H widgets to the VBox display")
print(f"   Inserted {len(kh_widget_lines)} lines at position {insert_pos}")
print(f"\nNow when you run Cell 9, you'll see:")
print(f"  1. Tau-squared method dropdown")
print(f"  2. Knapp-Hartung checkbox (checked by default)")
print(f"  3. Help text for K-H correction")
