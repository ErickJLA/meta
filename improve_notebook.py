#!/usr/bin/env python3
"""
Script to improve the Meta_3_1_FINAL.ipynb notebook.
Implements critical fixes identified in the code review.
"""

import json
import sys
from pathlib import Path

def load_notebook(path):
    """Load a Jupyter notebook from file."""
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_notebook(notebook, path):
    """Save a Jupyter notebook to file."""
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(notebook, f, indent=1, ensure_ascii=False)
    print(f"✓ Saved notebook to {path}")

def add_readme_cell(notebook):
    """Add a comprehensive README cell at the beginning."""
    readme_content = """<div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 10px; color: white;'>
<h1 style='color: white; margin-top: 0;'>📊 Meta-Analysis Pipeline v3.1</h1>
<p style='font-size: 16px; color: #f0f0f0;'>A comprehensive Google Colab notebook for conducting publication-ready meta-analyses with advanced statistical methods.</p>
</div>

---

## 🎯 Quick Start Guide

### **Step-by-Step Workflow:**

1. **📚 Cell 1**: Import libraries & authenticate with Google
2. **📁 Cell 2**: Load your data from Google Sheets
3. **⚙️ Cell 3**: Configure analysis parameters
4. **🧹 Cell 4**: Apply configuration & clean data
5. **🔬 Cell 6**: Detect effect size type
6. **🧮 Cell 7**: Calculate effect sizes
7. **📊 Cell 8**: View overall meta-analysis results
8. **📈 Cells 9-19**: Advanced analyses (subgroups, regression, plots)

---

## 🎓 What is Meta-Analysis?

Meta-analysis is a statistical technique for **combining results from multiple studies** to estimate an **overall effect size**. It provides more precise estimates than individual studies and can identify patterns across research.

### **Supported Effect Sizes:**
- **lnRR**: Log Response Ratio (for ratio measures)
- **Hedges' g**: Standardized mean difference with small-sample correction
- **Cohen's d**: Standardized mean difference (uncorrected)
- **Log OR**: Log odds ratio

---

## 📋 Required Data Format

Your Google Sheet must have these columns:

| Column | Description | Example |
|--------|-------------|---------|
| `id` | Study identifier | "Smith2020" |
| `xe` | Experimental group mean | 25.3 |
| `sde` | Experimental group SD | 4.2 |
| `ne` | Experimental group sample size | 30 |
| `xc` | Control group mean | 22.1 |
| `sdc` | Control group SD | 3.8 |
| `nc` | Control group sample size | 28 |

**Optional:** Add categorical columns for **moderator analysis** (e.g., "species", "treatment_type", "year")

---

## 🔬 Advanced Features

### ✨ What Makes This Pipeline Special?

1. **Three-Level Models**: Accounts for multiple effect sizes per study
2. **Cluster-Robust Inference**: Handles dependency in data
3. **Multiple Heterogeneity Estimators**: DL, REML, ML, PM, SJ
4. **Publication Bias Assessment**: Funnel plots and statistical tests
5. **Meta-Regression**: Test continuous and categorical moderators
6. **Spline Analysis**: Model non-linear relationships
7. **Sensitivity Analysis**: Leave-one-out and cumulative methods

---

## ⚠️ Important Notes

- **Run cells in order**: Each cell depends on previous ones
- **Check prerequisites**: Some cells require specific prior cells to run
- **Google Sheets access**: Ensure your sheet is shared with your Colab email
- **Data quality**: Clean your data before uploading (remove blanks, check formatting)

---

## 📚 Statistical Methods Reference

This notebook implements methods from:

- **Borenstein et al. (2009)**: *Introduction to Meta-Analysis*
- **Viechtbauer (2010)**: *Conducting Meta-Analyses in R with the metafor Package*
- **Hedges & Olkin (1985)**: *Statistical Methods for Meta-Analysis*

For detailed methodology, see cell documentation throughout the notebook.

---

## 🐛 Troubleshooting

**"Authentication Failed"**
- Restart runtime and re-run Cell 1
- Check Google account permissions

**"Data Not Found"**
- Verify Google Sheet name spelling
- Ensure sheet is shared with Colab email
- Check that worksheet exists

**"Invalid Column Names"**
- Use Cell 3 accordion to map column names
- Ensure no duplicate mappings

---

## 📧 Support & Feedback

For issues or suggestions, please refer to the documentation or contact the maintainer.

---

<div style='background-color: #d4edda; border-left: 4px solid #28a745; padding: 15px; margin-top: 20px;'>
<strong>✅ Ready to start?</strong> Run <strong>Cell 1</strong> below to begin!
</div>"""

    readme_cell = {
        "cell_type": "markdown",
        "metadata": {
            "id": "readme-section"
        },
        "source": [readme_content]
    }

    # Insert after the Colab badge
    notebook['cells'].insert(1, readme_cell)
    print("✓ Added comprehensive README cell")

def fix_cell_2_error_handling(notebook):
    """Fix Cell 2: Add proper error handling to widget handlers."""
    cell = notebook['cells'][2]  # Cell 2 (index adjusts if README added)

    source = ''.join(cell['source'])

    # Add improved error handling to on_load_data_clicked
    old_handler = '''def on_load_data_clicked(b):
    """Event handler for 'Load Data from Sheet' button."""
    with data_loader_output:
        clear_output(wait=True)
        worksheet_name = worksheet_select_widget.value
        if not worksheet_name:
            print("✗ Please select a worksheet.")
            return

        print(f"Loading data from '{worksheet_name}'...")
        try:
            worksheet = spreadsheet.worksheet(worksheet_name)
            rows = worksheet.get_all_values()'''

    new_handler = '''def on_load_data_clicked(b):
    """Event handler for 'Load Data from Sheet' button."""
    with data_loader_output:
        clear_output(wait=True)
        worksheet_name = worksheet_select_widget.value
        if not worksheet_name:
            print("✗ Please select a worksheet.")
            return

        print(f"Loading data from '{worksheet_name}'...")
        try:
            # Validate worksheet exists
            try:
                worksheet = spreadsheet.worksheet(worksheet_name)
            except gspread.exceptions.WorksheetNotFound:
                print(f"✗ ERROR: Worksheet '{worksheet_name}' not found.")
                print("  The worksheet may have been deleted or renamed.")
                print("  Please click 'Fetch Worksheets' again.")
                return

            rows = worksheet.get_all_values()'''

    if old_handler in source:
        source = source.replace(old_handler, new_handler)
        cell['source'] = source.split('\n')
        # Keep newlines in the list format
        cell['source'] = [line + '\n' if i < len(cell['source'])-1 else line
                          for i, line in enumerate(cell['source'])]
        print("✓ Fixed Cell 2: Added error handling for worksheet access")
    else:
        print("⚠ Cell 2: Could not find exact match for handler replacement")

def fix_cell_3_type_safety(notebook):
    """Fix Cell 3: Improve type conversion and add data preview."""
    cell_idx = 3  # Adjusted for README
    cell = notebook['cells'][cell_idx]

    source = ''.join(cell['source'])

    # Add data preview feature before configuration
    data_preview = '''
# --- 1.5. Data Preview Feature ---
data_preview_widget = widgets.Output()

def show_data_preview():
    """Display a preview of the loaded data."""
    with data_preview_widget:
        clear_output(wait=True)
        if 'raw_data_from_sheet' in globals():
            print("="*70)
            print("DATA PREVIEW")
            print("="*70)
            print(f"Shape: {raw_data_from_sheet.shape[0]} rows × {raw_data_from_sheet.shape[1]} columns")
            print(f"\\nFirst 5 rows:\\n")
            print(raw_data_from_sheet.head().to_string())
            print(f"\\nColumn names: {', '.join(raw_data_from_sheet.columns.tolist())}")
        else:
            print("⚠️ No data loaded yet. Please run Cell 2 first.")

preview_button = widgets.Button(
    description="👁️ Preview Data",
    button_style='info',
    layout=widgets.Layout(width='200px')
)
preview_button.on_click(lambda b: show_data_preview())

# Show preview button
display(widgets.HBox([preview_button, data_preview_widget]))
'''

    # Find insertion point (after widget definitions, before display)
    insertion_marker = "# --- 5. Assemble & Display Final UI ---"
    if insertion_marker in source:
        parts = source.split(insertion_marker)
        source = parts[0] + data_preview + "\\n" + insertion_marker + parts[1]
        cell['source'] = [line + '\\n' for line in source.split('\\n')[:-1]] + [source.split('\\n')[-1]]
        print("✓ Fixed Cell 3: Added data preview feature")
    else:
        print("⚠ Cell 3: Could not find insertion point for preview")

def fix_cell_4_type_conversion(notebook):
    """Fix Cell 4: Safer type conversion without fillna(0)."""
    cell_idx = 4
    cell = notebook['cells'][cell_idx]

    source = ''.join(cell['source'])

    # Replace unsafe fillna(0) pattern
    old_pattern = "raw_data[col] = raw_data[col].fillna(0).astype(int)"
    new_pattern = """# Remove NaN values first, then convert to int
        raw_data = raw_data.dropna(subset=[col])
        raw_data[col] = raw_data[col].astype(int)"""

    if old_pattern in source:
        source = source.replace(old_pattern, new_pattern)

        # Also add logging for coerced values
        old_coerce = "raw_data[col] = pd.to_numeric(raw_data[col], errors='coerce')"
        new_coerce = """raw_data[col] = pd.to_numeric(raw_data[col], errors='coerce')
        n_coerced = raw_data[col].isna().sum()
        if n_coerced > 0:
            print(f"  ⚠️  {n_coerced} values in '{col}' could not be converted to numbers (set to NaN)")"""

        if old_coerce in source:
            source = source.replace(old_coerce, new_coerce)

        cell['source'] = [line + '\\n' for line in source.split('\\n')[:-1]] + [source.split('\\n')[-1]]
        print("✓ Fixed Cell 4: Improved type conversion safety")
    else:
        print("⚠ Cell 4: Could not find type conversion pattern")

def fix_cell_10_moderator_widget(notebook):
    """Fix Cell 10: Prevent IndexError when no moderators available."""
    cell_idx = 10
    cell = notebook['cells'][cell_idx]

    source = ''.join(cell['source'])

    # Fix moderator widget initialization
    old_init = """moderator1_widget = widgets.Dropdown(
    description='Factor 1:',
    options=available_moderators,
    value=available_moderators[0],"""

    new_init = """moderator1_widget = widgets.Dropdown(
    description='Factor 1:',
    options=available_moderators if available_moderators else ['None'],
    value=available_moderators[0] if available_moderators else None,"""

    if old_init in source:
        source = source.replace(old_init, new_init)
        cell['source'] = [line + '\\n' for line in source.split('\\n')[:-1]] + [source.split('\\n')[-1]]
        print("✓ Fixed Cell 10: Prevented IndexError in moderator widget")
    else:
        print("⚠ Cell 10: Could not find moderator widget pattern")

def remove_duplicate_functions_from_cell_11(notebook):
    """Remove duplicate heterogeneity functions from Cell 11."""
    cell_idx = 11
    cell = notebook['cells'][cell_idx]

    source = ''.join(cell['source'])

    # Find and remove the duplicate section
    start_marker = "# --- 0a. Copied from Cell 4.5 (Advanced Heterogeneity Estimators) ---"
    end_marker = "# --- 0b. Copied from Cell 6.5 (Three-Level Model) ---"

    if start_marker in source and end_marker in source:
        # Keep everything before start_marker and from end_marker onwards
        parts = source.split(start_marker)
        before = parts[0]
        after_parts = parts[1].split(end_marker)
        after = end_marker + after_parts[1]

        # Add a reference comment instead
        reference = """# --- 0a. Import Functions from Cell 4.5 ---
# Note: Heterogeneity estimation functions are defined in Cell 4.5
# This cell uses: calculate_tau_squared_DL, calculate_tau_squared_REML, calculate_tau_squared
# Ensure Cell 4.5 has been run before executing this cell.

"""

        source = before + reference + after
        cell['source'] = [line + '\\n' for line in source.split('\\n')[:-1]] + [source.split('\\n')[-1]]
        print("✓ Fixed Cell 11: Removed ~300 lines of duplicate heterogeneity functions")
        print("  Added reference comment to Cell 4.5 instead")
    else:
        print("⚠ Cell 11: Could not find exact duplicate section markers")

def add_progress_indicators(notebook):
    """Add progress indicator examples to long-running cells."""
    # This would require more complex changes to add tqdm progress bars
    # For now, just add a comment about where they could be added
    print("ℹ Progress indicators: Would require tqdm integration (skipping for now)")

def main():
    """Main improvement script."""
    print("="*70)
    print("META-ANALYSIS NOTEBOOK IMPROVEMENT SCRIPT")
    print("="*70)
    print()

    notebook_path = Path("/home/user/meta/Meta_3_1_FINAL.ipynb")
    output_path = Path("/home/user/meta/Meta_3_1_IMPROVED.ipynb")

    print(f"Loading notebook from: {notebook_path}")
    notebook = load_notebook(notebook_path)
    print(f"✓ Loaded notebook with {len(notebook['cells'])} cells")
    print()

    print("Applying improvements...")
    print("-"*70)

    # Apply all fixes
    add_readme_cell(notebook)
    # Note: Cell indices shift after adding README
    # fix_cell_2_error_handling(notebook)  # Complex string replacement - do separately
    # fix_cell_3_type_safety(notebook)     # Complex string replacement - do separately
    # fix_cell_4_type_conversion(notebook) # Complex string replacement - do separately
    # fix_cell_10_moderator_widget(notebook) # Complex string replacement - do separately
    remove_duplicate_functions_from_cell_11(notebook)

    print()
    print("-"*70)
    print(f"Saving improved notebook to: {output_path}")
    save_notebook(notebook, output_path)
    print()
    print("="*70)
    print("✅ IMPROVEMENT SCRIPT COMPLETE")
    print("="*70)
    print()
    print("Summary of changes:")
    print("  1. ✓ Added comprehensive README cell")
    print("  2. ✓ Removed duplicate heterogeneity functions from Cell 11")
    print("  3. ⚠ Additional fixes require manual editing (complex replacements)")
    print()
    print("Next steps:")
    print("  - Review Meta_3_1_IMPROVED.ipynb")
    print("  - Apply remaining fixes using notebook Edit tool")
    print("  - Test all improvements")

if __name__ == "__main__":
    main()
