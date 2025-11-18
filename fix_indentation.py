#!/usr/bin/env python3
"""Fix indentation error in Meta_3_3.ipynb Cell 9"""

import json
import re

def fix_knapp_hartung_indentation(notebook_path):
    """Fix the Knapp-Hartung code indentation in Cell 9"""

    # Read notebook
    with open(notebook_path, 'r', encoding='utf-8') as f:
        nb = json.load(f)

    # Find Cell 9 (Overall Pooled Effect Size & Heterogeneity)
    target_cell_idx = None
    for idx, cell in enumerate(nb['cells']):
        if cell['cell_type'] == 'code':
            source = ''.join(cell['source'])
            if 'OVERALL POOLED EFFECT SIZE & HETEROGENEITY' in source:
                target_cell_idx = idx
                print(f"✓ Found target cell at index {idx}")
                break

    if target_cell_idx is None:
        print("✗ Could not find target cell")
        return False

    # Get cell source
    cell_lines = nb['cells'][target_cell_idx]['source']

    # Find the K-H section that needs fixing
    kh_start_idx = None
    kh_end_idx = None

    for i, line in enumerate(cell_lines):
        if '# APPLY KNAPP-HARTUNG CORRECTION (if enabled)' in line:
            # Find the comment block start (should be a few lines before)
            for j in range(max(0, i-5), i):
                if '# =============================================================================' in cell_lines[j]:
                    kh_start_idx = j
                    break
            if kh_start_idx is None:
                kh_start_idx = i

        # Find where K-H section ends (look for the next section that has 8 spaces of indentation)
        if kh_start_idx is not None and kh_end_idx is None:
            if i > kh_start_idx + 5:  # Skip a few lines after start
                # Look for "# Display results" or similar that's indented with 8 spaces
                if line.startswith('        # Display results') or \
                   line.startswith('        print(f"\\n') and 'Random-Effects Results' in line:
                    kh_end_idx = i
                    break
                # Also check for elif/else/other control structures at 4 spaces
                if i > kh_start_idx + 100:  # Safety limit
                    if (line.startswith('elif ') or line.startswith('else:') or
                        line.startswith('# ---') or line.startswith('print("=')):
                        kh_end_idx = i
                        break

    if kh_start_idx is None:
        print("✗ Could not find K-H section start")
        return False

    if kh_end_idx is None:
        # Scan ahead more
        for i in range(kh_start_idx + 5, len(cell_lines)):
            if cell_lines[i].startswith('        # Display results'):
                kh_end_idx = i
                break
            # Look for next major section
            if i > kh_start_idx + 120 and (cell_lines[i].startswith('# ---') or
                                           cell_lines[i].startswith('print("='*70)')):
                kh_end_idx = i
                break

    if kh_end_idx is None:
        print("✗ Could not find K-H section end")
        return False

    print(f"✓ Found K-H section: lines {kh_start_idx} to {kh_end_idx}")

    # Extract the K-H section
    kh_section = cell_lines[kh_start_idx:kh_end_idx]

    # Fix indentation: add 8 spaces to all lines that are part of the K-H section
    fixed_kh_section = []
    for line in kh_section:
        if line == '\n' or line.strip() == '':
            # Keep empty lines as-is
            fixed_kh_section.append(line)
        else:
            # Remove any existing leading indentation and add 8 spaces
            stripped = line.lstrip()
            # Calculate current indentation
            current_indent = len(line) - len(stripped)

            if current_indent < 4:
                # This line needs to be indented - add 8 spaces
                fixed_kh_section.append('        ' + stripped)
            elif current_indent == 4:
                # Add 4 more spaces (to make it 8)
                fixed_kh_section.append('        ' + stripped)
            else:
                # Already has indentation, keep it but ensure it's at least 8
                if current_indent >= 8:
                    fixed_kh_section.append(line)
                else:
                    # Add additional spaces to make it 8
                    additional = 8 - current_indent
                    fixed_kh_section.append(' ' * additional + line)

    # Rebuild the cell
    new_cell_lines = (cell_lines[:kh_start_idx] +
                      fixed_kh_section +
                      cell_lines[kh_end_idx:])

    # Update the cell
    nb['cells'][target_cell_idx]['source'] = new_cell_lines

    # Save the notebook
    with open(notebook_path, 'w', encoding='utf-8') as f:
        json.dump(nb, f, indent=1, ensure_ascii=False)

    print(f"\n✅ Fixed indentation in {notebook_path}")
    print(f"   - Lines affected: {kh_start_idx} to {kh_end_idx}")
    print(f"   - Total K-H lines: {len(kh_section)}")

    return True

if __name__ == '__main__':
    notebook_path = '/home/user/meta/Meta_3_3.ipynb'

    print("="*70)
    print("FIXING KNAPP-HARTUNG INDENTATION IN META_3_3.IPYNB")
    print("="*70)
    print()

    success = fix_knapp_hartung_indentation(notebook_path)

    if success:
        print("\n🎉 Indentation fixed successfully!")
    else:
        print("\n⚠️  Could not fix indentation")
        exit(1)
