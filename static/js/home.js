let balanceVisible = true;
let originalBalance = "";
let originalCnpj = "";

// Função para formatar CNPJ: 11111111000191 -> 11.111.111/0001-91
function formatCNPJ(cnpj) {
  if (!cnpj) return cnpj;

  // Remove caracteres não numéricos
  const cleaned = cnpj.toString().replace(/\D/g, '');

  // Se não tem 14 dígitos, retorna como está
  if (cleaned.length !== 14) return cnpj;

  // Aplica a formatação
  return cleaned.replace(/(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})/, '$1.$2.$3/$4-$5');
}

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
  // Formatar CNPJ quando página carregar
  const cnpjEl = document.getElementById("empresaCnpj");
  if (cnpjEl) {
    const text = cnpjEl.textContent;
    // Extrai apenas os números do CNPJ
    const cnpjNumbers = text.replace(/\D/g, '');
    if (cnpjNumbers.length === 14) {
      const formatted = formatCNPJ(cnpjNumbers);
      cnpjEl.textContent = "CNPJ " + formatted;
      originalCnpj = cnpjEl.textContent.trim();
    }
  }

  const btn = document.getElementById("eyeBtn");
  if (btn) {
    btn.addEventListener("click", toggleBalance);
  }
});