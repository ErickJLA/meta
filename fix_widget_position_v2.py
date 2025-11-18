#!/usr/bin/env python3
"""
Fix Cell 9: Move widgets to end of output
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

    print("Original cell length:", len(source.split('\n')), "lines")

    # Step 1: Extract the widget creation code (but not the display calls)
    # We'll move the display calls to the end

    # Find the section where widgets are displayed
    # Pattern: from "display(widgets.VBox" to "display(rerun_message)"

    # Remove these display calls from the current location
    # Pattern 1: display(widgets.VBox([...]))
    pattern1 = r'display\(widgets\.VBox\(\[\s*method_help,\s*tau_method_widget\s*\]\)\)'

    # Pattern 2: display(rerun_message)
    pattern2 = r'display\(rerun_message\)'

    # Replace with placeholders that we'll fill in at the end
    source = re.sub(pattern1, '# Widget will be displayed at end', source, count=1)
    source = re.sub(pattern2, '# Rerun message will be displayed at end', source, count=1)

    # Step 2: Find the end of the cell (where results are saved)
    # Look for the last print or the ANALYSIS_CONFIG save section

    # Find where to insert the widget display
    # Look for the end of the main analysis (after saving results)
    insert_marker = "# Store comprehensive results in ANALYSIS_CONFIG for downstream cells"

    if insert_marker in source:
        # Split at this marker
        parts = source.split(insert_marker)
        before = parts[0]
        after = insert_marker + parts[1]

        # Find the end of the results dictionary (after the closing brace and comment)
        # Look for the pattern where results are stored
        match = re.search(r"(ANALYSIS_CONFIG\['overall_results'\] = \{[^}]+\}[^}]*\})", after, re.DOTALL)

        if match:
            # Find position after this assignment
            end_of_assignment = match.end()
            analysis_part = after[:end_of_assignment]
            remaining = after[end_of_assignment:]

            # Create widget display section
            widget_section = '''

# =============================================================================
# DISPLAY CONFIGURATION WIDGET
# =============================================================================
# Widget is displayed at the end so it's not buried by analysis output

print("\\n" + "="*70)
print("ANALYSIS CONFIGURATION")
print("="*70)

# Display method selection widget
config_box = widgets.VBox([
    widgets.HTML("<h4 style='color: #2E86AB;'>⚙️ τ² Estimator Selection</h4>"),
    method_help,
    tau_method_widget,
    rerun_message
])

display(config_box)

# Add helpful note
display(widgets.HTML(
    "<div style='background-color: #d4edda; border-left: 4px solid #28a745; padding: 12px; margin: 10px 0;'>"
    "✅ <b>Analysis Complete!</b><br>"
    "You can change the τ² estimator above and re-run this cell to recalculate with a different method."
    "</div>"
))
'''

            # Reassemble
            source = before + analysis_part + widget_section + remaining

            print("✅ Widget display moved to end successfully")
        else:
            print("⚠ Could not find results assignment pattern")
            return False
    else:
        print("⚠ Could not find insert marker")
        return False

    # Step 3: Save the modified cell
    cell['source'] = [line + '\n' for line in source.split('\n')[:-1]] + [source.split('\n')[-1]]

    # Save notebook
    with open('/home/user/meta/Meta_3_1_IMPROVED.ipynb', 'w') as f:
        json.dump(nb, f, indent=1, ensure_ascii=False)

    print("✅ Notebook saved successfully")
    print("New cell length:", len(source.split('\n')), "lines")
    return True

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
