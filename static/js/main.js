/**
 * main.js - Core JavaScript utilities for Audit Koding 2025 App
 */

// ---- Number Formatting ----
function fmtNum(n) {
  if (n === null || n === undefined || n === '' || n !== n) return '0';
  return Math.round(Number(n)).toLocaleString('id-ID');
}

function fmtCurrency(n) {
  if (n === null || n === undefined || isNaN(n)) return '0';
  return Math.abs(Number(n)).toLocaleString('id-ID', { maximumFractionDigits: 0 });
}

function fmtCurrencyShort(n) {
  if (!n || isNaN(n)) return '0';
  n = Number(n);
  const isNeg = n < 0;
  n = Math.abs(n);
  let result;
  if (n >= 1e12) result = (n / 1e12).toFixed(2) + ' T';
  else if (n >= 1e9) result = (n / 1e9).toFixed(2) + ' M';
  else if (n >= 1e6) result = (n / 1e6).toFixed(1) + ' Jt';
  else result = n.toLocaleString('id-ID');
  return (isNeg ? '-' : '') + result;
}

// ---- Toast Notifications ----
function showToast(message, type = 'info') {
  const container = document.getElementById('toastContainer');
  if (!container) return;
  
  const iconMap = { success: '✅', error: '❌', info: 'ℹ️', warning: '⚠️' };
  
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.innerHTML = `
    <span class="toast-icon">${iconMap[type] || 'ℹ️'}</span>
    <span style="flex:1;">${message}</span>
    <button onclick="this.parentElement.remove()" style="background:none; border:none; color:var(--text-muted); cursor:pointer; font-size:16px;">×</button>
  `;
  
  container.appendChild(toast);
  
  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(100%)';
    toast.style.transition = 'all 0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}

// ---- Info Modal ----
function showInfo() {
  const modal = document.getElementById('infoModal');
  if (modal) modal.style.display = 'flex';
}

// ---- Active nav item ----
document.addEventListener('DOMContentLoaded', () => {
  const path = window.location.pathname;
  document.querySelectorAll('.nav-item').forEach(item => {
    const href = item.getAttribute('href');
    if (href && href !== '#') {
      if (path === href || (href !== '/' && path.startsWith(href))) {
        item.classList.add('active');
      } else {
        item.classList.remove('active');
      }
    }
  });
});
