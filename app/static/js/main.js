/**
 * SomCoffe POS - Global JavaScript Utilities
 * This file contains logic used across the entire system.
 */

$(document).ready(function () {
    // Shared functionality for alerts, modal triggers, or date formatting.
    console.log("SomCoffe POS - System Initialized.");
});

function formatCurrency(amount) {
    // This can fetch currency from meta or data attributes if needed.
    return '$' + parseFloat(amount).toFixed(2);
}
