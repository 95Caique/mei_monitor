/**
 * Formatação de CNPJ para relatórios e outras páginas
 */

document.addEventListener("DOMContentLoaded", function () {
  // Formatar CNPJs em tabelas e cards
  document.querySelectorAll('table td, .card, [class*="company"], [class*="empresa"]').forEach(function(el) {
    // Procura por padrões de CNPJ em texto
    const text = el.textContent;
    const cnpjMatch = text.match(/\d{14}/);

    if (cnpjMatch && cnpjMatch[0].length === 14) {
      const formatted = formatCNPJ(cnpjMatch[0]);
      el.textContent = el.textContent.replace(cnpjMatch[0], formatted);
    }
  });
});

