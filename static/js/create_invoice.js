(function(){
  const form = document.getElementById('invoiceForm');
  if (!form) return;

  form.addEventListener('input', function() {
    const data = new FormData(form);
    let html = '';
    let hasData = false;

    for (const [key, value] of data.entries()) {
      if (key === 'csrfmiddlewaretoken') continue;
      if (value && value.toString().trim()) {
        hasData = true;
        const label = key.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
        const isTotal = key.toLowerCase().includes('total') || key.toLowerCase().includes('valor');
        html += '<div class="preview-line">';
        html += '  <span class="preview-label">' + label + '</span>';
        html += '  <span class="preview-value' + (isTotal ? ' total' : '') + '">' + value + '</span>';
        html += '</div>';
      }
    }

    const container = document.getElementById('previewContent');
    if (hasData) {
      html += '<div style="text-align:center; margin-top:0.75rem;">';
      html += '  <span class="preview-status">⏳ Rascunho</span>';
      html += '</div>';
      container.innerHTML = html;
    } else {
      container.innerHTML = '<div class="preview-empty"><span class="icon">📋</span>Preencha o formulário para<br>visualizar a nota aqui.</div>';
    }
  });
})();
