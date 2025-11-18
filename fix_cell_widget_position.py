#!/usr/bin/env python3
"""
Fix the widget position in Cell 9 (OVERALL POOLED EFFECT SIZE)
Move widgets to the end of the output instead of the beginning.
"""

import json
import sys
from pathlib import Path

def load_notebook(path):
    """Load notebook from JSON."""
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_notebook(notebook, path):
    """Save notebook to JSON."""
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(notebook, f, indent=1, ensure_ascii=False)

def fix_cell_9(notebook):
    """Fix Cell 9 to move widgets to the end."""
    cell = notebook['cells'][9]

    # Convert source array to string
    source = ''.join(cell['source'])

    # Find the widget display section
    widget_section_start = source.find('# --- ADD THIS AT THE START OF CELL 6 (before main analysis) ---')
    widget_section_end = source.find('print("\\n" + "="*70)\n\nprint("\\n" + "="*70)\nprint("OVERALL META-ANALYSIS")')

    if widget_section_start == -1 or widget_section_end == -1:
        print("⚠ Could not find widget section markers")
        return False

    # Extract the widget code
    widget_code = source[widget_section_start:widget_section_end]

    # Remove the widget section from its current position
    source_without_widgets = source[:widget_section_start] + source[widget_section_end:]

    # Now we need to restructure the cell:
    # 1. Create an output widget at the start
    # 2. Wrap all analysis in that output widget
    # 3. Display interactive widgets at the end

    new_source = '''#@title 📊 OVERALL POOLED EFFECT SIZE & HETEROGENEITY

# =============================================================================
# CELL 6: OVERALL META-ANALYSIS
# Purpose: Calculate pooled effect sizes and assess heterogeneity
# Dependencies: Cell 5 (data_filtered with effect sizes, ANALYSIS_CONFIG)
# Outputs: Overall pooled estimates (fixed & random effects), heterogeneity stats
# =============================================================================

from scipy.stats import norm, chi2, t
import ipywidgets as widgets
from IPython.display import display, clear_output

# =============================================================================
# WIDGET SETUP - Create widgets first (they'll be displayed at the end)
# =============================================================================

# Check if advanced estimators available
if 'calculate_tau_squared' in globals():
    method_options = [
        ('REML (Recommended)', 'REML'),
        ('DerSimonian-Laird (Classic)', 'DL'),
        ('Maximum Likelihood', 'ML'),
        ('Paule-Mandel', 'PM'),
        ('Sidik-Jonkman', 'SJ')
    ]

    method_help = widgets.HTML(
        "<div style='background-color: #e8f4f8; padding: 10px; margin: 10px 0; border-radius: 5px;'>"
        "<b>💡 Method Guide:</b><br>"
        "• <b>REML:</b> ⭐ Best choice for most analyses. Unbiased and accurate.<br>"
        "• <b>DL:</b> Fast but can underestimate τ² with few studies.<br>"
        "• <b>ML:</b> Efficient but biased downward.<br>"
        "• <b>PM:</b> Exact Q = k-1 solution.<br>"
        "• <b>SJ:</b> Conservative, good for k < 10."
        "</div>"
    )
else:
    method_options = [('DerSimonian-Laird', 'DL')]

    method_help = widgets.HTML(
        "<div style='background-color: #fff3cd; padding: 10px; margin: 10px 0; border-radius: 5px;'>"
        "⚠️ Run <b>Cell 4.5 (Heterogeneity Estimators)</b> to access REML and other methods."
        "</div>"
    )

tau_method_widget = widgets.Dropdown(
    options=method_options,
    value='REML' if 'calculate_tau_squared' in globals() else 'DL',
    description='τ² Method:',
    style={'description_width': '100px'},
    layout=widgets.Layout(width='400px')
)

# Save selection to config
if 'ANALYSIS_CONFIG' not in globals():
    ANALYSIS_CONFIG = {}
ANALYSIS_CONFIG['tau_method'] = tau_method_widget.value

def on_method_change(change):
    ANALYSIS_CONFIG['tau_method'] = change['new']

tau_method_widget.observe(on_method_change, names='value')

rerun_message = widgets.HTML(
    "<div style='background-color: #fffbf0; padding: 8px; margin: 10px 0; border-left: 3px solid #ff9800; border-radius: 3px;'>"
    "⚠️ <b>Important:</b> After changing the method, you must re-run this cell to apply the new estimator."
    "</div>"
)

# Create the configuration widget box (will be displayed at the end)
config_widget_box = widgets.VBox([
    widgets.HTML("<h3 style='color: #2E86AB; margin-top: 20px;'>⚙️ Analysis Configuration</h3>"),
    method_help,
    tau_method_widget,
    rerun_message
])

# =============================================================================
# ANALYSIS OUTPUT - All analysis happens in this output widget
# =============================================================================

analysis_output = widgets.Output()

with analysis_output:
'''

    # Add the analysis code (everything after the widget section)
    # We need to indent it by 4 spaces to be inside the "with analysis_output:" block
    analysis_part = source_without_widgets[widget_section_start:]

    # Find where the actual analysis starts (after the imports)
    analysis_start = analysis_part.find('print("\\n" + "="*70)\nprint("OVERALL META-ANALYSIS")')

    if analysis_start != -1:
        analysis_code = analysis_part[analysis_start:]

        # Indent all lines by 4 spaces
        indented_analysis = '\n'.join('    ' + line if line.strip() else line
                                      for line in analysis_code.split('\n'))

        new_source += indented_analysis

        # Add the widget display at the very end
        new_source += '''

# =============================================================================
# DISPLAY WIDGETS - Output first, then interactive configuration
# =============================================================================

# Display the analysis output
display(analysis_output)

# Display the configuration widget at the end (so it's visible and not buried)
display(config_widget_box)

# Add helpful message
display(widgets.HTML(
    "<div style='background-color: #d4edda; border-left: 4px solid #28a745; padding: 10px; margin-top: 10px;'>"
    "✅ <b>Analysis Complete!</b> You can modify the τ² method above and re-run this cell to see different results."
    "</div>"
))
'''

        # Convert back to source array
        cell['source'] = [line + '\n' for line in new_source.split('\n')[:-1]] + [new_source.split('\n')[-1]]

        print("✅ Successfully restructured Cell 9")
        print("   Widgets now appear at the end of the output")
        return True
    else:
        print("⚠ Could not find analysis start marker")
        return False

def main():
    notebook_path = Path("/home/user/meta/Meta_3_1_IMPROVED.ipynb")

    print("="*70)
    print("FIX CELL 9 WIDGET POSITION")
    print("="*70)
    print()

    print(f"Loading: {notebook_path}")
    notebook = load_notebook(notebook_path)

    print(f"Fixing Cell 9 widget position...")
    success = fix_cell_9(notebook)

    if success:
        print(f"\nSaving improved notebook...")
        save_notebook(notebook, notebook_path)
        print(f"✅ Done! Widgets will now appear at the end of the output.")
    else:
        print(f"❌ Fix failed. See warnings above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
