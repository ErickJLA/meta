#!/usr/bin/env python3
"""
Add Trim-and-Fill cell to Meta_3_1_IMPROVED.ipynb
Inserts after the Funnel Plot cell (index 18)
"""

import json
from trim_and_fill_cell import TRIM_AND_FILL_CELL

def add_trim_fill_cell():
    # Load notebook
    with open('/home/user/meta/Meta_3_1_IMPROVED.ipynb', 'r') as f:
        nb = json.load(f)

    print("="*70)
    print("ADDING TRIM-AND-FILL CELL TO NOTEBOOK")
    print("="*70)
    print()
    print(f"Current cells: {len(nb['cells'])}")

    # Create new cell
    new_cell = {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {
            "cellView": "form",
            "id": "trim_and_fill_analysis"
        },
        "outputs": [],
        "source": [line + '\n' for line in TRIM_AND_FILL_CELL.split('\n')[:-1]] + [TRIM_AND_FILL_CELL.split('\n')[-1]]
    }

    # Insert after funnel plot (index 18)
    insert_position = 19
    nb['cells'].insert(insert_position, new_cell)

    print(f"✓ Inserted Trim-and-Fill cell at position {insert_position}")
    print(f"New total cells: {len(nb['cells'])}")

    # Save notebook
    with open('/home/user/meta/Meta_3_1_IMPROVED.ipynb', 'w') as f:
        json.dump(nb, f, indent=1, ensure_ascii=False)

    print("✓ Notebook saved successfully")
    print()
    print("="*70)
    print("TRIM-AND-FILL CELL ADDED")
    print("="*70)
    print()
    print("Cell details:")
    print(f"  • Position: Cell 19 (after Funnel Plot)")
    print(f"  • Type: Code cell with form view")
    print(f"  • Lines: {len(TRIM_AND_FILL_CELL.split(chr(10)))}")
    print()
    print("Features:")
    print("  ✓ Interactive widgets for configuration")
    print("  ✓ L0, R0, Q0 estimators supported")
    print("  ✓ Auto-detection of asymmetry side")
    print("  ✓ Forest plot with imputed studies (red squares)")
    print("  ✓ Comprehensive interpretation guidance")
    print("  ✓ Strong warnings about sensitivity analysis")
    print("  ✓ Comparison table: original vs. filled")
    print("  ✓ Robustness assessment (% change)")
    print()
    print("The cell is ready to use in Google Colab!")

if __name__ == "__main__":
    add_trim_fill_cell()
