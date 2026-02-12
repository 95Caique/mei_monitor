let balanceVisible = true;
const balanceEl = document.getElementById('balanceAmount');
const eyeBtn = document.getElementById('eyeBtn');
const originalBalance = balanceEl ? balanceEl.textContent : '';

function toggleBalance() {
  balanceVisible = !balanceVisible;
  if (!balanceEl || !eyeBtn) return;
  balanceEl.textContent = balanceVisible ? originalBalance : 'R$ ••••••';
  eyeBtn.textContent = balanceVisible ? '👁' : '🙈';
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', function() {
    const btn = document.getElementById('eyeBtn');
    if (btn) btn.addEventListener('click', toggleBalance);
  });
} else {
  const btn = document.getElementById('eyeBtn');
  if (btn) btn.addEventListener('click', toggleBalance);
}
