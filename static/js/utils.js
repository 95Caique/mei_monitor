/**
 * Utilitários globais para todo o projeto
 */

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

// Aplicar formatação de CNPJ em todos os elementos com classe cnpj-format
document.addEventListener("DOMContentLoaded", function () {
  // Formatar todos os CNPJs na página
  document.querySelectorAll('[data-cnpj]').forEach(function(el) {
    const cnpj = el.getAttribute('data-cnpj');
    const formatted = formatCNPJ(cnpj);
    el.textContent = formatted;
  });

  // Também tentar formatar elementos com id empresaCnpj
  const cnpjEl = document.getElementById("empresaCnpj");
  if (cnpjEl) {
    const text = cnpjEl.textContent;
    const cnpjNumbers = text.replace(/\D/g, '');
    if (cnpjNumbers.length === 14) {
      const formatted = formatCNPJ(cnpjNumbers);
      cnpjEl.textContent = "CNPJ " + formatted;
    }
  }
});

