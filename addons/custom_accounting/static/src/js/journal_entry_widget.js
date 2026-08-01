/** @odoo-module **/
/**
 * Custom Accounting — Journal Entry Balance Badge
 *
 * Adds a visual ✓/⚠ badge on the "Journal Entry Breakdown" tab
 * to indicate whether custom journal lines are balanced.
 * Pure DOM MutationObserver — no broken OWL template dependency.
 */

// ── Badge updater ─────────────────────────────────────────────────
function updateBalanceBadge() {
    const tabLink = document.querySelector(
        '.o_notebook .nav-link[name="custom_journal_breakdown"],' +
        '.o_notebook .nav-link[data-name="custom_journal_breakdown"]'
    );
    if (!tabLink) return;

    const isBalancedInput = document.querySelector(
        '[name="custom_is_balanced"] input[type="checkbox"]'
    );
    const lineRows = document.querySelectorAll(
        '[name="custom_journal_line_ids"] .o_data_row'
    );

    const old = tabLink.querySelector('.ca_balance_badge');
    if (old) old.remove();
    if (!lineRows.length) return;

    const balanced = isBalancedInput ? isBalancedInput.checked : true;
    const badge = document.createElement('span');
    badge.className = 'ca_balance_badge badge ms-2';
    badge.textContent = balanced ? '✓' : '⚠';
    badge.style.cssText = balanced
        ? 'background:#198754;color:#fff;font-size:0.7rem;padding:2px 5px;border-radius:3px;'
        : 'background:#dc3545;color:#fff;font-size:0.7rem;padding:2px 5px;border-radius:3px;';
    tabLink.appendChild(badge);
}

// ── Observe the whole app for form view changes ───────────────────
let _caObserver = null;

function startObserver() {
    if (_caObserver) _caObserver.disconnect();
    _caObserver = new MutationObserver(() => updateBalanceBadge());
    _caObserver.observe(document.body, { childList: true, subtree: true });
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', startObserver);
} else {
    startObserver();
}
