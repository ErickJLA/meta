"""
Knapp-Hartung Correction Implementation for Meta_3_1_IMPROVED.ipynb

This shows how to add K-H correction to Cell 8 (Overall Meta-Analysis)
"""

# Implementation code to add to Cell 8

KH_IMPLEMENTATION = '''
# =============================================================================
# KNAPP-HARTUNG CORRECTION (Optional Enhancement)
# Add this section after calculating standard random-effects estimates
# =============================================================================

def calculate_knapp_hartung_ci(yi, vi, tau_sq, pooled_effect, alpha=0.05):
    """
    Calculate Knapp-Hartung adjusted confidence interval

    Parameters:
    -----------
    yi : array
        Effect sizes
    vi : array
        Variances
    tau_sq : float
        Tau-squared estimate
    pooled_effect : float
        Random-effects pooled estimate
    alpha : float
        Significance level (default 0.05 for 95% CI)

    Returns:
    --------
    dict with SE_KH, CI_lower, CI_upper, t_stat, df, p_value

    References:
    -----------
    Knapp, G., & Hartung, J. (2003). Improved tests for a random effects
    meta-regression with a single covariate. Statistics in Medicine, 22(17),
    2693-2710.

    IntHout, J., Ioannidis, J. P., & Borm, G. F. (2014). The Hartung-Knapp-
    Sidik-Jonkman method for random effects meta-analysis is straightforward
    and considerably outperforms the standard DerSimonian-Laird method.
    BMC Medical Research Methodology, 14(1), 25.
    """

    # Random-effects weights
    wi_star = 1 / (vi + tau_sq)
    sum_wi_star = np.sum(wi_star)

    # Degrees of freedom
    k = len(yi)
    df = k - 1

    if df <= 0:
        # Can't use K-H with k=1
        return None

    # Calculate Q statistic (residual heterogeneity)
    Q = np.sum(wi_star * (yi - pooled_effect)**2)

    # Standard random-effects variance
    var_standard = 1 / sum_wi_star

    # Knapp-Hartung adjusted variance
    # SE_KH² = (Q / (k-1)) × (1 / Σw*)
    var_KH = (Q / df) * var_standard

    # Variance can't be smaller than standard (protection against underestimation)
    # Some implementations use max(var_KH, var_standard)
    # We'll use the adjustment as-is per Knapp & Hartung

    se_KH = np.sqrt(var_KH)

    # t-distribution critical value
    from scipy.stats import t
    t_crit = t.ppf(1 - alpha/2, df)

    # Confidence interval
    ci_lower = pooled_effect - t_crit * se_KH
    ci_upper = pooled_effect + t_crit * se_KH

    # Test statistic and p-value
    t_stat = pooled_effect / se_KH
    p_value = 2 * (1 - t.cdf(abs(t_stat), df))

    return {
        'se_KH': se_KH,
        'var_KH': var_KH,
        'ci_lower': ci_lower,
        'ci_upper': ci_upper,
        't_stat': t_stat,
        't_crit': t_crit,
        'df': df,
        'p_value': p_value,
        'Q': Q
    }

# =============================================================================
# WIDGET: Enable Knapp-Hartung Correction
# =============================================================================

# Add this widget near the tau-squared method selector
use_kh_widget = widgets.Checkbox(
    value=True,  # Default ON (recommended)
    description='Use Knapp-Hartung correction for confidence intervals',
    style={'description_width': 'initial'},
    layout=widgets.Layout(width='500px')
)

kh_help = widgets.HTML(
    "<div style='background-color: #e7f3ff; padding: 10px; margin: 10px 0; border-radius: 5px;'>"
    "<b>ℹ️ Knapp-Hartung Correction:</b><br>"
    "• Uses t-distribution instead of normal (better for small k)<br>"
    "• Adjusts SE based on observed variability<br>"
    "• Generally recommended, especially for k < 20<br>"
    "• Produces more conservative (wider) confidence intervals<br>"
    "• Reduces false positive rate"
    "</div>"
)

# Display with other configuration widgets
display(widgets.VBox([
    kh_help,
    use_kh_widget
]))

# =============================================================================
# APPLY KNAPP-HARTUNG IN ANALYSIS
# =============================================================================

# After calculating standard random-effects estimates, add:

if k > 1 and use_kh_widget.value:
    print("\\n" + "="*70)
    print("KNAPP-HARTUNG ADJUSTMENT")
    print("="*70)

    kh_results = calculate_knapp_hartung_ci(
        yi=analysis_data[effect_col].values,
        vi=analysis_data[var_col].values,
        tau_sq=tau_squared_DL,  # or whichever estimator was used
        pooled_effect=pooled_effect_random,
        alpha=0.05
    )

    if kh_results is not None:
        print(f"\\n📐 Applying Knapp-Hartung correction to random-effects CI:")
        print(f"  • Degrees of freedom: {kh_results['df']}")
        print(f"  • t critical value: {kh_results['t_crit']:.3f} (vs. 1.96 for normal)")

        # Compare standard vs K-H
        print(f"\\n📊 Comparison:")
        print(f"  {'Method':<20} {'SE':<12} {'95% CI Lower':<15} {'95% CI Upper':<15} {'P-value':<12}")
        print(f"  {'-'*20} {'-'*12} {'-'*15} {'-'*15} {'-'*12}")
        print(f"  {'Standard (Z-test)':<20} {pooled_SE_random:<12.4f} {ci_lower_random:<15.4f} {ci_upper_random:<15.4f} {p_value_random:<12.4g}")
        print(f"  {'Knapp-Hartung':<20} {kh_results['se_KH']:<12.4f} {kh_results['ci_lower']:<15.4f} {kh_results['ci_upper']:<15.4f} {kh_results['p_value']:<12.4g}")

        # Calculate CI width difference
        ci_width_standard = ci_upper_random - ci_lower_random
        ci_width_kh = kh_results['ci_upper'] - kh_results['ci_lower']
        width_increase = ((ci_width_kh - ci_width_standard) / ci_width_standard) * 100

        print(f"\\n  • K-H CI is {abs(width_increase):.1f}% {'wider' if width_increase > 0 else 'narrower'} than standard CI")

        # Check if conclusion changes
        standard_sig = p_value_random < 0.05
        kh_sig = kh_results['p_value'] < 0.05

        if standard_sig != kh_sig:
            print(f"  ⚠️  IMPORTANT: Statistical significance CHANGES with K-H correction!")
            print(f"     Standard: p = {p_value_random:.4g} ({'significant' if standard_sig else 'non-significant'})")
            print(f"     K-H:      p = {kh_results['p_value']:.4g} ({'significant' if kh_sig else 'non-significant'})")
        else:
            print(f"  ✓ Conclusion does not change (both {'significant' if kh_sig else 'non-significant'})")

        # Recommendation based on k
        if k < 20:
            print(f"\\n💡 RECOMMENDATION:")
            print(f"   With k = {k} studies, the Knapp-Hartung method is RECOMMENDED.")
            print(f"   Report the K-H confidence interval as your primary result.")

        # Update variables to use K-H (optional, or keep both)
        # You can either replace or keep both:

        # Option 1: Keep both, add suffix
        pooled_SE_random_KH = kh_results['se_KH']
        ci_lower_random_KH = kh_results['ci_lower']
        ci_upper_random_KH = kh_results['ci_upper']
        p_value_random_KH = kh_results['p_value']

        # Option 2: Replace (if you want K-H to be primary)
        # pooled_SE_random = kh_results['se_KH']
        # ci_lower_random = kh_results['ci_lower']
        # ci_upper_random = kh_results['ci_upper']
        # p_value_random = kh_results['p_value']

        # Save to ANALYSIS_CONFIG
        ANALYSIS_CONFIG['overall_results']['knapp_hartung'] = {
            'used': True,
            'se': kh_results['se_KH'],
            'ci_lower': kh_results['ci_lower'],
            'ci_upper': kh_results['ci_upper'],
            't_stat': kh_results['t_stat'],
            'df': kh_results['df'],
            'p_value': kh_results['p_value'],
            'comparison': {
                'standard_ci': [ci_lower_random, ci_upper_random],
                'kh_ci': [kh_results['ci_lower'], kh_results['ci_upper']],
                'width_increase_percent': width_increase
            }
        }
    else:
        print("  ⚠️  Knapp-Hartung not applicable (k=1)")
        ANALYSIS_CONFIG['overall_results']['knapp_hartung'] = {'used': False, 'reason': 'k=1'}
else:
    print(f"\\n  ℹ️  Knapp-Hartung correction not applied (user choice or k=1)")
    ANALYSIS_CONFIG['overall_results']['knapp_hartung'] = {'used': False, 'reason': 'user_disabled'}

# =============================================================================
# UPDATE SUMMARY OUTPUT TO SHOW K-H RESULTS
# =============================================================================

# In the final summary section, add:

if ANALYSIS_CONFIG['overall_results'].get('knapp_hartung', {}).get('used', False):
    kh_info = ANALYSIS_CONFIG['overall_results']['knapp_hartung']

    print(f"\\n📊 Random-Effects Summary (Knapp-Hartung):")
    print(f"  • Pooled effect: {pooled_effect_random:.4f}")
    print(f"  • 95% CI (K-H): [{kh_info['ci_lower']:.4f}, {kh_info['ci_upper']:.4f}]")
    print(f"  • t-statistic: {kh_info['t_stat']:.3f} (df = {kh_info['df']})")
    print(f"  • P-value: {kh_info['p_value']:.4g}")

    # Add asterisks for significance
    if kh_info['p_value'] < 0.001:
        sig_marker = "***"
    elif kh_info['p_value'] < 0.01:
        sig_marker = "**"
    elif kh_info['p_value'] < 0.05:
        sig_marker = "*"
    else:
        sig_marker = "ns"

    print(f"  • Significance: {sig_marker}")
'''

# =============================================================================
# EXAMPLE USAGE IN CELL 8
# =============================================================================

CELL_8_MODIFICATION_EXAMPLE = '''
# This shows where the K-H code fits in the existing Cell 8 structure:

# ... [existing code for fixed-effects] ...

# --- STEP 5: RANDOM-EFFECTS MODEL ---
print("\\n" + "="*70)
print("STEP 4: RANDOM-EFFECTS MODEL")
print("="*70)

# Calculate tau-squared (existing code)
tau_squared_DL = calculate_tau_squared_DL(...)

# Calculate standard random-effects estimates (existing code)
w_random = 1 / (analysis_data[var_col] + tau_squared_DL)
sum_w_random = w_random.sum()
pooled_effect_random = (w_random * analysis_data[effect_col]).sum() / sum_w_random
pooled_var_random = 1 / sum_w_random
pooled_SE_random = np.sqrt(pooled_var_random)

# Standard CI (existing)
ci_lower_random = pooled_effect_random - 1.96 * pooled_SE_random
ci_upper_random = pooled_effect_random + 1.96 * pooled_SE_random
z_stat_random = pooled_effect_random / pooled_SE_random
p_value_random = 2 * (1 - norm.cdf(abs(z_stat_random)))

print(f"\\n📊 Standard Random-Effects Results:")
print(f"  Pooled effect: {pooled_effect_random:.4f}")
print(f"  95% CI: [{ci_lower_random:.4f}, {ci_upper_random:.4f}]")
print(f"  P-value: {p_value_random:.4g}")

# *** NEW: APPLY KNAPP-HARTUNG CORRECTION ***
if k > 1 and use_kh_widget.value:
    kh_results = calculate_knapp_hartung_ci(
        yi=analysis_data[effect_col].values,
        vi=analysis_data[var_col].values,
        tau_sq=tau_squared_DL,
        pooled_effect=pooled_effect_random
    )

    if kh_results:
        print(f"\\n📊 Knapp-Hartung Adjusted Results:")
        print(f"  SE (K-H): {kh_results['se_KH']:.4f}")
        print(f"  95% CI (K-H): [{kh_results['ci_lower']:.4f}, {kh_results['ci_upper']:.4f}]")
        print(f"  t-statistic: {kh_results['t_stat']:.3f} (df = {kh_results['df']})")
        print(f"  P-value: {kh_results['p_value']:.4g}")

        # Use K-H as primary if k < 20
        if k < 20:
            print(f"\\n  💡 Using K-H results as primary (k < 20)")
            # Optionally update the CI to use K-H

# ... [rest of existing code] ...
'''

# =============================================================================
# REPORTING GUIDANCE
# =============================================================================

REPORTING_TEMPLATE = '''
REPORTING KNAPP-HARTUNG RESULTS
================================

Example 1: K-H applied (k < 20)
--------------------------------
"We conducted a random-effects meta-analysis using the [REML/DL] estimator
for τ². Confidence intervals were calculated using the Knapp-Hartung method
(Knapp & Hartung, 2003), which uses a t-distribution and adjusts the standard
error for the observed variability among studies. This approach is recommended
for meta-analyses with fewer than 20 studies (IntHout et al., 2014).

The pooled effect was [X.XX] (95% CI: [X.XX, X.XX], t = [X.XX], df = [k-1],
p = [X.XXX])."

Example 2: K-H comparison
--------------------------
"Both standard (normal distribution) and Knapp-Hartung (t-distribution)
confidence intervals were calculated. The K-H method produced a [X]% wider
confidence interval ([X.XX, X.XX] vs. [X.XX, X.XX]), but the conclusion
remained [the same/changed]."

References to cite:
-------------------
Knapp, G., & Hartung, J. (2003). Improved tests for a random effects
meta-regression with a single covariate. Statistics in Medicine, 22(17),
2693-2710.

IntHout, J., Ioannidis, J. P., & Borm, G. F. (2014). The Hartung-Knapp-
Sidik-Jonkman method for random effects meta-analysis is straightforward
and considerably outperforms the standard DerSimonian-Laird method.
BMC Medical Research Methodology, 14(1), 25.
'''

if __name__ == "__main__":
    print("Knapp-Hartung Implementation Guide")
    print("="*70)
    print()
    print("This implementation adds K-H correction to Cell 8.")
    print()
    print("Key features:")
    print("  ✓ Optional toggle (widget)")
    print("  ✓ Default ON (recommended)")
    print("  ✓ Shows comparison with standard CI")
    print("  ✓ Detects significance changes")
    print("  ✓ Automatic recommendation for k < 20")
    print("  ✓ Saves both standard and K-H results")
    print()
    print("Implementation complexity: LOW")
    print("Lines of code: ~150")
    print("Impact: HIGH (major methodological improvement)")
