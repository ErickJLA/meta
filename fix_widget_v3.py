#!/usr/bin/env python3
"""
Fix Cell 9: Move widgets to the very end of output
"""

import json
import re

def main():
    # Load notebook
    with open('/home/user/meta/Meta_3_1_IMPROVED.ipynb', 'r') as f:
        nb = json.load(f)

    # Get cell 9
    cell = nb['cells'][9]
    source = ''.join(cell['source'])

    print("="*70)
    print("FIXING CELL 9 WIDGET POSITION")
    print("="*70)
    print(f"Original cell: {len(source.split(chr(10)))} lines\n")

    # Step 1: Remove the two early display() calls
    # Pattern 1: display(widgets.VBox([method_help, tau_method_widget]))
    original_display1 = '''display(widgets.VBox([
    method_help,
    tau_method_widget
]))'''

    # Pattern 2: display(rerun_message)
    original_display2 = 'display(rerun_message)'

    if original_display1 in source:
        source = source.replace(original_display1, '# Widgets will be displayed at the end of output')
        print("✓ Removed first display() call")
    else:
        print("⚠ Could not find first display() call")

    if original_display2 in source:
        source = source.replace(original_display2, '# Rerun message will be displayed at the end')
        print("✓ Removed second display() call")
    else:
        print("⚠ Could not find second display() call")

    # Step 2: Find the end of the cell and add widget display there
    # Look for the final print statements at the end
    end_marker = 'print("\\n" + "="*70)'

    # Find the LAST occurrence (at the very end)
    last_occurrence = source.rfind(end_marker)

    if last_occurrence != -1:
        # Insert widget display right before the final separator
        widget_display_code = '''

# =============================================================================
# DISPLAY CONFIGURATION WIDGET AT END
# =============================================================================
# Widget is displayed here so it's visible and not buried by analysis output

print("\\n" + "="*70)
print("⚙️  TAU-SQUARED ESTIMATOR CONFIGURATION")
print("="*70)
print()
print("You can modify the heterogeneity estimator below:")
print()

# Display method selection widget
config_box = widgets.VBox([
    method_help,
    tau_method_widget,
    rerun_message
], layout=widgets.Layout(
    border='2px solid #2E86AB',
    padding='15px',
    margin='10px 0'
))

display(config_box)

# Add helpful completion message
display(widgets.HTML(
    "<div style='background-color: #d4edda; border-left: 4px solid #28a745; padding: 12px; margin: 15px 0; border-radius: 4px;'>"
    "✅ <b>Analysis Complete!</b><br><br>"
    "• Review the results above<br>"
    "• Modify the τ² estimator in the widget above if needed<br>"
    "• Re-run this cell to recalculate with a different method<br>"
    "• Proceed to the next cell for advanced analyses"
    "</div>"
))

'''

        # Insert before the final separator
        source = source[:last_occurrence] + widget_display_code + source[last_occurrence:]
        print("✓ Added widget display at end of cell")
    else:
        print("⚠ Could not find end marker")
        return False

    # Step 3: Save the modified cell
    cell['source'] = [line + '\n' for line in source.split('\n')[:-1]] + [source.split('\n')[-1]]

    # Save notebook
    with open('/home/user/meta/Meta_3_1_IMPROVED.ipynb', 'w') as f:
        json.dump(nb, f, indent=1, ensure_ascii=False)

    print(f"\nNew cell: {len(source.split(chr(10)))} lines")
    print("\n" + "="*70)
    print("✅ SUCCESSFULLY FIXED WIDGET POSITION")
    print("="*70)
    print("\nChanges made:")
    print("  1. Removed early display() calls that buried widgets")
    print("  2. Added widget display section at the end of output")
    print("  3. Widgets now appear after all analysis results")
    print("\nThe user will now see the configuration widget at the")
    print("bottom, where it won't be missed!")

    return True

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
