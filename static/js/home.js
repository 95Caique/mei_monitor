let balanceVisible = true;
let originalBalance = "";
let originalCnpj = "";

function toggleBalance() {
  const balanceEl = document.getElementById("balanceAmount");
  const cnpjEl = document.getElementById("empresaCnpj");
  const eyeBtn = document.getElementById("eyeBtn");

  if (!balanceEl || !cnpjEl || !eyeBtn) return;

  if (!originalBalance) {
    originalBalance = balanceEl.textContent.trim();
  }

  if (!originalCnpj) {
    originalCnpj = cnpjEl.textContent.trim();
  }

  balanceVisible = !balanceVisible;

  if (balanceVisible) {
    balanceEl.textContent = originalBalance;
    cnpjEl.textContent = originalCnpj;
    eyeBtn.innerHTML = '<i class="fa-regular fa-eye"></i>';
  } else {
    balanceEl.textContent = "********";
    cnpjEl.textContent = "CNPJ ********";
    eyeBtn.innerHTML = '<i class="fa-solid fa-eye-slash"></i>';
  }
}

document.addEventListener("DOMContentLoaded", function () {
  const btn = document.getElementById("eyeBtn");
  if (btn) {
    btn.addEventListener("click", toggleBalance);
  }
});