#!/usr/bin/env python3
"""Add Knapp-Hartung widget definition to Meta_3_3.ipynb Cell 9"""

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

# Find insertion point: after "tau_method_widget.observe(on_method_change, names='value')"
insert_idx = None
for i, line in enumerate(lines):
    if "tau_method_widget.observe(on_method_change, names='value')" in line:
        insert_idx = i + 1
        break

if not insert_idx:
    print("ERROR: Could not find tau_method_widget.observe line")
    exit(1)

print(f"Found insertion point at line {insert_idx}")

# Widget definition code to insert
kh_widget_code = [
    "\n",
    "# Knapp-Hartung correction widget\n",
    "use_kh_widget = widgets.Checkbox(\n",
    "    value=True,  # Default ON (recommended)\n",
    "    description='Use Knapp-Hartung correction for confidence intervals',\n",
    "    style={'description_width': 'initial'},\n",
    "    layout=widgets.Layout(width='500px')\n",
    ")\n",
    "\n",
    "kh_help = widgets.HTML(\n",
    "    \"<div style='background-color: #e7f3ff; padding: 10px; margin: 10px 0; border-radius: 5px;'>\"\n",
    "    \"<b>ℹ️ Knapp-Hartung Correction:</b><br>\"\n",
    "    \"• Uses t-distribution instead of normal (better for small k)<br>\"\n",
    "    \"• Adjusts SE based on observed variability (Q statistic)<br>\"\n",
    "    \"• <b>Recommended</b>, especially for k < 20 studies<br>\"\n",
    "    \"• Produces more conservative (wider) confidence intervals<br>\"\n",
    "    \"• Reduces false positive rate (better Type I error control)\"\n",
    "    \"</div>\"\n",
    ")\n",
    "\n"
]

# Insert the widget code
new_lines = lines[:insert_idx] + kh_widget_code + lines[insert_idx:]

# Update notebook
nb['cells'][target_idx]['source'] = new_lines

# Save
print(f"Saving notebook...")
with open(notebook_path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

print(f"\n✅ Done! Added Knapp-Hartung widget definition")
print(f"   Inserted {len(kh_widget_code)} lines at position {insert_idx}")
print(f"\nThe widget will default to ON (checked) when you run the cell.")
print(f"Users can uncheck it to disable K-H correction if needed.")
