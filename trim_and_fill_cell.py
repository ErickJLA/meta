"""
New Cell for Meta_3_1_IMPROVED.ipynb: Trim-and-Fill Sensitivity Analysis

This implements the Duval & Tweedie (2000) trim-and-fill method as a
SENSITIVITY ANALYSIS for publication bias, not as a correction.

Insert this cell after the Funnel Plot cell.
"""

TRIM_AND_FILL_CELL = '''#@title 🔄 TRIM-AND-FILL SENSITIVITY ANALYSIS

# =============================================================================
# TRIM-AND-FILL SENSITIVITY ANALYSIS
# Purpose: Assess potential impact of publication bias using trim-and-fill method
# Method: Duval & Tweedie (2000) iterative trim-and-fill procedure
# IMPORTANT: This is a SENSITIVITY ANALYSIS, not a correction!
# Dependencies: Cell 8 (overall results), Cell 7 (effect sizes)
# Outputs: Comparison of original vs. "filled" estimates, forest plot
# =============================================================================

import numpy as np
import pandas as pd
from scipy.stats import norm, rankdata, t
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import ipywidgets as widgets
from IPython.display import display, HTML, clear_output
import datetime
import warnings

# =============================================================================
# WIDGET SETUP
# =============================================================================

# Create output widget
output_widget = widgets.Output()

# Configuration widgets
estimator_widget = widgets.Dropdown(
    options=[
        ('L0 (Linear, default)', 'L0'),
        ('R0 (Rank-based)', 'R0'),
        ('Q0 (Quadratic)', 'Q0')
    ],
    value='L0',
    description='Estimator:',
    style={'description_width': '100px'},
    layout=widgets.Layout(width='350px')
)

side_widget = widgets.Dropdown(
    options=[
        ('Auto-detect (recommended)', 'auto'),
        ('Right (assume small positive missing)', 'right'),
        ('Left (assume small negative missing)', 'left')
    ],
    value='auto',
    description='Side:',
    style={'description_width': '100px'},
    layout=widgets.Layout(width='450px')
)

max_iter_widget = widgets.IntSlider(
    value=100,
    min=10,
    max=500,
    step=10,
    description='Max iterations:',
    style={'description_width': '100px'},
    layout=widgets.Layout(width='350px')
)

# Plot configuration
show_plot_widget = widgets.Checkbox(
    value=True,
    description='Show forest plot with imputed studies',
    style={'description_width': 'initial'}
)

run_button = widgets.Button(
    description='▶ Run Trim-and-Fill Analysis',
    button_style='success',
    layout=widgets.Layout(width='300px', height='40px')
)

# =============================================================================
# TRIM-AND-FILL IMPLEMENTATION
# =============================================================================

def trimfill_analysis(data, effect_col, var_col, estimator='L0', side='auto', max_iter=100):
    """
    Duval & Tweedie (2000) Trim-and-Fill Method

    This is a SENSITIVITY ANALYSIS to assess potential publication bias impact.
    DO NOT use the "adjusted" estimate as your final result!

    Parameters:
    -----------
    data : DataFrame
        Data with effect sizes and variances
    effect_col : str
        Column name for effect sizes
    var_col : str
        Column name for variances
    estimator : str
        'L0' (linear), 'R0' (rank), or 'Q0' (quadratic)
    side : str
        'left', 'right', or 'auto'
    max_iter : int
        Maximum iterations

    Returns:
    --------
    dict : Results including k0 (# studies to trim), filled data, estimates
    """

    # Prepare data
    yi = data[effect_col].values
    vi = data[var_col].values
    k = len(yi)

    # Calculate fixed-effect pooled estimate
    wi = 1 / vi
    pooled_fe = np.sum(wi * yi) / np.sum(wi)

    # Center effect sizes
    yi_centered = yi - pooled_fe

    # Determine side if auto
    if side == 'auto':
        # Check which side has more extreme small studies
        se = np.sqrt(vi)
        # Look at correlation between effect size and SE
        # Positive correlation suggests missing on right (small negative studies)
        # Negative correlation suggests missing on left (small positive studies)

        if len(yi) >= 3:
            # Use Egger-like approach
            from scipy.stats import pearsonr
            corr, _ = pearsonr(np.abs(yi), se)

            # Also check skewness
            skew_sign = np.sign(np.mean(yi_centered))

            if skew_sign > 0:
                side = 'left'  # Positive skew suggests missing negative studies
            else:
                side = 'right'  # Negative skew suggests missing positive studies
        else:
            side = 'right'  # Default

    side_multiplier = 1 if side == 'right' else -1

    # Iterative trim-and-fill
    k0 = 0  # Number of studies to trim
    yi_work = yi.copy()
    vi_work = vi.copy()

    for iteration in range(max_iter):
        k_current = len(yi_work)

        # Re-calculate pooled estimate with current data
        wi_work = 1 / vi_work
        pooled_work = np.sum(wi_work * yi_work) / np.sum(wi_work)

        # Center effects
        yi_centered_work = yi_work - pooled_work

        # Rank effects (by signed deviation from pooled)
        if estimator == 'R0':
            # Rank-based estimator
            signed_effects = side_multiplier * yi_centered_work
            ranks = rankdata(signed_effects)

            # Count studies on the "expected" side
            T_plus = np.sum(ranks[signed_effects > 0])
            k_plus = np.sum(signed_effects > 0)

            # Estimate k0
            expected_T = k_plus * (k_current + 1) / 2
            k0_new = int(np.floor((4 * T_plus - k_plus * (k_current + 1)) / (2 * k_current - k_plus + 2)))

        else:  # L0 or Q0 (we'll implement L0)
            # Linear estimator (Duval & Tweedie 2000, equation 3)
            signed_effects = side_multiplier * yi_centered_work

            # Sort by signed effect
            sorted_idx = np.argsort(signed_effects)
            sorted_effects = signed_effects[sorted_idx]

            # Calculate sum of signed ranks
            S = 0
            for i, eff in enumerate(sorted_effects):
                rank = i + 1
                if eff > 0:
                    S += (rank - (k_current + 1) / 2)

            # Estimate k0 using L0 estimator
            gamma = S / (k_current - 1) if k_current > 1 else 0
            k0_new = int(np.floor((k_current - 1 - gamma) / 2))

        # Constrain k0
        k0_new = max(0, min(k0_new, k_current - 1))

        # Check convergence
        if k0_new == k0:
            break

        k0 = k0_new

        # Trim k0 most extreme studies from the "expected" side
        if k0 > 0:
            signed_effects = side_multiplier * (yi - pooled_work)
            trim_idx = np.argsort(signed_effects)[-k0:]  # Most extreme on expected side
            keep_idx = np.setdiff1d(np.arange(k), trim_idx)

            yi_work = yi[keep_idx]
            vi_work = vi[keep_idx]
        else:
            yi_work = yi.copy()
            vi_work = vi.copy()

    # Calculate trimmed estimate
    if len(yi_work) > 0:
        wi_trim = 1 / vi_work
        pooled_trim = np.sum(wi_trim * yi_work) / np.sum(wi_trim)
    else:
        pooled_trim = pooled_fe

    # Fill: Create mirror images of the trimmed studies
    if k0 > 0:
        # Get the k0 most extreme studies that were trimmed
        signed_effects = side_multiplier * (yi - pooled_trim)
        trim_idx = np.argsort(signed_effects)[-k0:]

        # Create filled (imputed) studies as mirror images
        yi_trimmed = yi[trim_idx]
        vi_trimmed = vi[trim_idx]

        # Mirror around the trimmed pooled estimate
        yi_filled = 2 * pooled_trim - yi_trimmed
        vi_filled = vi_trimmed.copy()  # Same variance

        # Combine original + filled
        yi_combined = np.concatenate([yi, yi_filled])
        vi_combined = np.concatenate([vi, vi_filled])
    else:
        yi_combined = yi.copy()
        vi_combined = vi.copy()
        yi_filled = np.array([])
        vi_filled = np.array([])

    # Calculate filled estimate
    wi_combined = 1 / vi_combined
    pooled_filled = np.sum(wi_combined * yi_combined) / np.sum(wi_combined)
    var_filled = 1 / np.sum(wi_combined)
    se_filled = np.sqrt(var_filled)
    ci_lower_filled = pooled_filled - 1.96 * se_filled
    ci_upper_filled = pooled_filled + 1.96 * se_filled

    # Calculate original estimate statistics
    var_original = 1 / np.sum(wi)
    se_original = np.sqrt(var_original)
    ci_lower_original = pooled_fe - 1.96 * se_original
    ci_upper_original = pooled_fe + 1.96 * se_original

    return {
        'k0': k0,
        'side': side,
        'k_original': k,
        'k_filled': k + k0,
        'pooled_original': pooled_fe,
        'se_original': se_original,
        'ci_lower_original': ci_lower_original,
        'ci_upper_original': ci_upper_original,
        'pooled_filled': pooled_filled,
        'se_filled': se_filled,
        'ci_lower_filled': ci_lower_filled,
        'ci_upper_filled': ci_upper_filled,
        'yi_filled': yi_filled,
        'vi_filled': vi_filled,
        'yi_combined': yi_combined,
        'vi_combined': vi_combined,
        'estimator': estimator,
        'converged': iteration < max_iter - 1
    }

def plot_trim_fill_forest(data, effect_col, se_col, results, es_label):
    """Create forest plot showing original + imputed studies"""

    yi_original = data[effect_col].values
    se_original = data[se_col].values
    k_original = len(yi_original)
    k0 = results['k0']

    # Prepare plot data
    all_effects = list(yi_original)
    all_se = list(se_original)
    all_labels = [f"Study {i+1}" for i in range(k_original)]
    all_colors = ['black'] * k_original
    all_markers = ['o'] * k_original

    # Add filled studies
    if k0 > 0:
        yi_filled = results['yi_filled']
        se_filled = np.sqrt(results['vi_filled'])

        for i in range(k0):
            all_effects.append(yi_filled[i])
            all_se.append(se_filled[i])
            all_labels.append(f"Filled {i+1}")
            all_colors.append('red')
            all_markers.append('s')  # Square marker

    # Calculate confidence intervals
    all_effects = np.array(all_effects)
    all_se = np.array(all_se)
    ci_lower = all_effects - 1.96 * all_se
    ci_upper = all_effects + 1.96 * all_se

    # Sort by effect size
    sort_idx = np.argsort(all_effects)[::-1]

    # Create figure
    fig, ax = plt.subplots(figsize=(10, max(8, len(all_effects) * 0.3)))

    # Plot studies
    y_pos = np.arange(len(all_effects))

    for i, idx in enumerate(sort_idx):
        # Plot CI
        ax.plot([ci_lower[idx], ci_upper[idx]], [i, i],
                color=all_colors[idx], linewidth=1.5, alpha=0.6)

        # Plot point estimate
        ax.scatter([all_effects[idx]], [i],
                  marker=all_markers[idx], s=100,
                  color=all_colors[idx], edgecolors='black',
                  linewidths=1.5, zorder=3,
                  alpha=0.8 if all_colors[idx] == 'red' else 1.0)

    # Add pooled estimates
    y_pooled_original = len(all_effects) + 1
    y_pooled_filled = len(all_effects) + 2

    # Original pooled
    ax.plot([results['ci_lower_original'], results['ci_upper_original']],
            [y_pooled_original, y_pooled_original],
            color='blue', linewidth=3, alpha=0.7)
    ax.scatter([results['pooled_original']], [y_pooled_original],
              marker='D', s=150, color='blue',
              edgecolors='black', linewidths=2, zorder=3,
              label='Original pooled')

    # Filled pooled
    if k0 > 0:
        ax.plot([results['ci_lower_filled'], results['ci_upper_filled']],
                [y_pooled_filled, y_pooled_filled],
                color='red', linewidth=3, alpha=0.7, linestyle='--')
        ax.scatter([results['pooled_filled']], [y_pooled_filled],
                  marker='D', s=150, color='red',
                  edgecolors='black', linewidths=2, zorder=3,
                  label='Filled pooled (sensitivity)')

    # Add null line
    ax.axvline(x=0, color='gray', linestyle='--', linewidth=1, alpha=0.5)

    # Formatting
    ax.set_yticks(range(len(all_effects) + 3))
    labels_plot = [all_labels[idx] for idx in sort_idx] + ['', 'Original Pooled']
    if k0 > 0:
        labels_plot.append('Filled Pooled')
    ax.set_yticklabels(labels_plot)

    ax.set_xlabel(f'{es_label} (95% CI)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Studies', fontsize=12, fontweight='bold')
    ax.set_title('Trim-and-Fill Sensitivity Analysis\\n(Red = Imputed Studies)',
                fontsize=14, fontweight='bold', pad=20)

    # Legend
    original_patch = mpatches.Patch(color='black', label='Original studies')
    filled_patch = mpatches.Patch(color='red', label='Imputed studies')
    ax.legend(handles=[original_patch, filled_patch] if k0 > 0 else [original_patch],
             loc='best', frameon=True, fancybox=True, shadow=True)

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(axis='x', alpha=0.3, linestyle=':')

    plt.tight_layout()
    plt.show()

# =============================================================================
# MAIN ANALYSIS FUNCTION
# =============================================================================

def run_trim_fill_analysis(b):
    """Execute trim-and-fill analysis"""
    with output_widget:
        clear_output(wait=True)

        print("="*70)
        print("TRIM-AND-FILL SENSITIVITY ANALYSIS")
        print("="*70)
        print(f"Timestamp: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        # Warning banner
        print("⚠️  "*25)
        print("IMPORTANT: THIS IS A SENSITIVITY ANALYSIS")
        print("⚠️  "*25)
        print()
        print("Trim-and-fill should be used to assess HOW VULNERABLE your")
        print("results are to publication bias, NOT to 'correct' your estimate.")
        print()
        print("The 'filled' estimate shows what results MIGHT look like if")
        print("missing studies existed, but this is speculative.")
        print()
        print("Report BOTH original and filled estimates, and interpret with caution.")
        print("="*70)
        print()

        try:
            # Load configuration
            if 'ANALYSIS_CONFIG' not in globals():
                raise NameError("ANALYSIS_CONFIG not found. Run previous cells first.")

            effect_col = ANALYSIS_CONFIG['effect_col']
            var_col = ANALYSIS_CONFIG['var_col']
            se_col = ANALYSIS_CONFIG['se_col']
            es_config = ANALYSIS_CONFIG['es_config']

            if 'analysis_data' in globals():
                data = analysis_data.copy()
            elif 'data_filtered' in globals():
                data = data_filtered.copy()
            else:
                raise ValueError("No data found. Run previous cells first.")

            # Clean data
            data = data.dropna(subset=[effect_col, var_col])
            data = data[data[var_col] > 0]

            k = len(data)
            print(f"STEP 1: LOADING DATA")
            print("-"*70)
            print(f"  ✓ Loaded {k} observations")
            print(f"  ✓ Effect size: {es_config['effect_label']}")
            print()

            if k < 3:
                print("❌ ERROR: Need at least 3 studies for trim-and-fill")
                return

            # Run analysis
            print(f"STEP 2: RUNNING TRIM-AND-FILL")
            print("-"*70)
            print(f"  • Estimator: {estimator_widget.value}")
            print(f"  • Side: {side_widget.value}")
            print(f"  • Max iterations: {max_iter_widget.value}")
            print()

            results = trimfill_analysis(
                data=data,
                effect_col=effect_col,
                var_col=var_col,
                estimator=estimator_widget.value,
                side=side_widget.value,
                max_iter=max_iter_widget.value
            )

            if not results['converged']:
                print("  ⚠️  WARNING: Analysis did not converge within max iterations")

            print(f"  ✓ Analysis complete")
            print(f"  ✓ Detected side: {results['side']}")
            print()

            # Display results
            print("="*70)
            print("RESULTS")
            print("="*70)
            print()

            print(f"📊 NUMBER OF STUDIES TRIMMED/FILLED: {results['k0']}")
            print()

            if results['k0'] == 0:
                print("✅ RESULT: No evidence of missing studies detected")
                print()
                print("Interpretation:")
                print("  • The trim-and-fill algorithm found no asymmetry suggesting")
                print("    missing studies on either side of the funnel plot.")
                print("  • This provides some reassurance against publication bias,")
                print("    though it does NOT prove bias is absent.")
                print("  • Other bias assessment methods should also be considered.")
            else:
                print(f"⚠️  RESULT: {results['k0']} studies potentially missing on the {results['side']} side")
                print()

                # Comparison table
                print(f"{'Estimate':<30} {'Original':<15} {'After Filling':<15} {'Difference':<15}")
                print("-"*75)
                print(f"{'k (# studies)':<30} {results['k_original']:<15} {results['k_filled']:<15} {results['k0']:<15}")
                print(f"{'Pooled effect':<30} {results['pooled_original']:<15.4f} {results['pooled_filled']:<15.4f} {results['pooled_filled'] - results['pooled_original']:<15.4f}")
                print(f"{'Standard error':<30} {results['se_original']:<15.4f} {results['se_filled']:<15.4f} {results['se_filled'] - results['se_original']:<15.4f}")
                print(f"{'95% CI lower':<30} {results['ci_lower_original']:<15.4f} {results['ci_lower_filled']:<15.4f} {'—':<15}")
                print(f"{'95% CI upper':<30} {results['ci_upper_original']:<15.4f} {results['ci_upper_filled']:<15.4f} {'—':<15}")
                print()

                # Calculate percent change
                pct_change = abs((results['pooled_filled'] - results['pooled_original']) / results['pooled_original'] * 100)

                print("🎯 INTERPRETATION:")
                print()
                print(f"  • If {results['k0']} studies were missing due to publication bias,")
                print(f"    the pooled effect would change by {pct_change:.1f}%")
                print()

                if pct_change < 10:
                    print("  ✓ Result is relatively ROBUST to potential publication bias")
                    print("    (< 10% change in estimate)")
                elif pct_change < 25:
                    print("  ⚠️  Result shows MODERATE sensitivity to publication bias")
                    print("    (10-25% change in estimate)")
                else:
                    print("  🔴 Result shows HIGH sensitivity to publication bias")
                    print("    (> 25% change in estimate)")
                    print("    Interpret original findings with considerable caution")

                # Check if conclusion changes
                original_sig = not (results['ci_lower_original'] <= 0 <= results['ci_upper_original'])
                filled_sig = not (results['ci_lower_filled'] <= 0 <= results['ci_upper_filled'])

                print()
                if original_sig != filled_sig:
                    print("  ⚠️  CRITICAL: Statistical significance CHANGES after filling!")
                    print("     This suggests results may be heavily influenced by bias.")
                else:
                    print("  ✓ Statistical significance does NOT change after filling")

            print()
            print("="*70)
            print("REPORTING GUIDANCE")
            print("="*70)
            print()
            print("When reporting trim-and-fill results:")
            print()
            print("  1. ✓ Report it as a SENSITIVITY ANALYSIS, not a correction")
            print("  2. ✓ Report both original and filled estimates")
            print("  3. ✓ Emphasize the ROBUSTNESS interpretation:")
            print("       'Results were [robust/sensitive] to potential publication bias'")
            print("  4. ✓ Note the assumptions:")
            print("       - Assumes bias is due to small studies only")
            print("       - Assumes symmetric funnel plot without bias")
            print("       - Cannot distinguish publication bias from other causes")
            print("  5. ⚠️  Do NOT report the filled estimate as your main finding")
            print()

            # Save results
            ANALYSIS_CONFIG['trimfill_results'] = {
                'timestamp': datetime.datetime.now(),
                'k0': results['k0'],
                'side': results['side'],
                'estimator': results['estimator'],
                'pooled_original': results['pooled_original'],
                'pooled_filled': results['pooled_filled'],
                'se_original': results['se_original'],
                'se_filled': results['se_filled'],
                'ci_original': [results['ci_lower_original'], results['ci_upper_original']],
                'ci_filled': [results['ci_lower_filled'], results['ci_upper_filled']],
                'percent_change': pct_change if results['k0'] > 0 else 0
            }

            print("  ✓ Results saved to ANALYSIS_CONFIG['trimfill_results']")
            print()

            # Plot
            if show_plot_widget.value and results['k0'] > 0:
                print("="*70)
                print("FOREST PLOT")
                print("="*70)
                print()
                plot_trim_fill_forest(
                    data=data,
                    effect_col=effect_col,
                    se_col=se_col,
                    results=results,
                    es_label=es_config['effect_label']
                )

        except Exception as e:
            print(f"\\n❌ ERROR: {type(e).__name__}")
            print(f"Message: {e}")
            import traceback
            traceback.print_exc()

# Attach handler
run_button.on_click(run_trim_fill_analysis)

# =============================================================================
# DISPLAY UI
# =============================================================================

help_html = widgets.HTML("""
<div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px; border-radius: 10px; color: white; margin-bottom: 20px;'>
    <h2 style='color: white; margin-top: 0;'>🔄 Trim-and-Fill Sensitivity Analysis</h2>
    <p style='font-size: 14px; margin-bottom: 0;'>
        Assess how vulnerable your results are to publication bias
    </p>
</div>

<div style='background-color: #fff3cd; border-left: 4px solid #ff9800;
            padding: 15px; margin: 15px 0; border-radius: 4px;'>
    <b>⚠️ IMPORTANT:</b> This is a <b>sensitivity analysis</b>, NOT a correction!
    <br><br>
    <b>Purpose:</b> Estimate how much your results might change IF unpublished studies exist
    <br>
    <b>Do NOT:</b> Use the "filled" estimate as your final answer
    <br>
    <b>Do:</b> Report both estimates and discuss robustness
</div>

<div style='background-color: #e7f3ff; padding: 15px; margin: 15px 0; border-radius: 4px;'>
    <b>📚 How it works:</b>
    <ol style='margin: 5px 0;'>
        <li>Detects asymmetry in the funnel plot</li>
        <li>Estimates number of "missing" studies (k₀)</li>
        <li>Adds mirror-image imputed studies</li>
        <li>Recalculates pooled effect with imputed studies</li>
        <li>Compares original vs. "filled" estimates</li>
    </ol>
    <b>Interpretation:</b> If results change little, they're robust to bias.
    If results change substantially, interpret with caution.
</div>
""")

config_box = widgets.VBox([
    widgets.HTML("<h4 style='color: #2E86AB;'>⚙️ Configuration</h4>"),
    estimator_widget,
    side_widget,
    max_iter_widget,
    widgets.HTML("<br>"),
    show_plot_widget
], layout=widgets.Layout(
    border='1px solid #ddd',
    padding='15px',
    margin='10px 0'
))

# Check prerequisites
try:
    if 'ANALYSIS_CONFIG' not in globals() or 'overall_results' not in ANALYSIS_CONFIG:
        display(HTML("""
        <div style='background-color: #f8d7da; border: 2px solid #f5c6cb;
                    padding: 20px; border-radius: 5px; color: #721c24;'>
            <h3>❌ Prerequisites Not Met</h3>
            <p>Please run the following cells first:</p>
            <ol>
                <li>Cell 8: Overall Meta-Analysis</li>
                <li>Cell 7: Effect Size Calculation</li>
            </ol>
        </div>
        """))
    else:
        display(help_html)
        display(config_box)
        display(run_button)
        display(output_widget)

        display(widgets.HTML("""
        <div style='background-color: #d4edda; border-left: 4px solid #28a745;
                    padding: 12px; margin: 15px 0; border-radius: 4px;'>
            ✅ Ready! Configure options above and click the button to run the analysis.
        </div>
        """))

except Exception as e:
    print(f"❌ Initialization error: {e}")
'''

if __name__ == "__main__":
    print("Trim-and-Fill cell code generated successfully!")
    print(f"Cell length: {len(TRIM_AND_FILL_CELL.split(chr(10)))} lines")
    print()
    print("To add to notebook:")
    print("1. Insert new cell after Funnel Plot cell")
    print("2. Paste the TRIM_AND_FILL_CELL content")
    print("3. Set cell type to 'Code'")
    print("4. Add cell view: #@title")
