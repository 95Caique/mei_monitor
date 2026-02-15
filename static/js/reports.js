(function(){
  // expects a global element with id 'invoicesData' containing JSON
  const dataEl = document.getElementById('invoicesData');
  if (!dataEl) return;
  let invoices = [];
  try { invoices = JSON.parse(dataEl.textContent || '[]'); } catch(e){ invoices = []; }

  const toggleBtn = document.getElementById('toggleInvoicesBtn');
  const panel = document.getElementById('invoicesPanel');
  const searchInput = document.getElementById('invoiceSearch');
  const listEl = document.getElementById('invoicesList');

  function formatCurrency(v){
    try { return new Intl.NumberFormat('pt-BR', {style:'currency', currency:'BRL'}).format(Number(v)); } catch(e){ return 'R$ ' + v; }
  }

  function renderList(items){
    if(!listEl) return;
    if (!items.length){ listEl.innerHTML = '<tr><td colspan="4" class="text-center text-muted">Nenhuma nota encontrada.</td></tr>'; return; }
    const rows = items.map((inv, idx) => {
      const d = new Date(inv.created_at).toISOString().slice(0,10);
      return `<tr><td>${idx+1}</td><td>${d}</td><td>${inv.invoice_id}</td><td>${formatCurrency(inv.total)}</td></tr>`;
    });
    listEl.innerHTML = rows.join('\n');
  }

  function filterInvoices(q){
    if (!q) return invoices;
    q = q.toLowerCase();
    return invoices.filter(inv => {
      if ((inv.invoice_id||'').toLowerCase().includes(q)) return true;
      if ((inv.total||'').toString().toLowerCase().includes(q)) return true;
      // name not available; fallback to invoice_id match
      return false;
    });
  }

  if (toggleBtn && panel){
    toggleBtn.addEventListener('click', function(e){
      e.preventDefault();
      if (panel.style.display === 'block'){
        panel.style.display = 'none';
        toggleBtn.textContent = 'Ver todas';
      } else {
        panel.style.display = 'block';
        toggleBtn.textContent = 'Ocultar';
        renderList(invoices);
      }
    });
  }

  if (searchInput){
    searchInput.addEventListener('input', function(e){
      const q = e.target.value.trim();
      const filtered = filterInvoices(q);
      renderList(filtered);
    });
  }

  // initial render hidden
  if(panel) panel.style.display = 'none';
})();
