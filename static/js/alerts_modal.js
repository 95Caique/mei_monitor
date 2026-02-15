(function(){
  const dataEl = document.getElementById('alertsAllData');
  if(!dataEl) return;
  let alerts = [];
  try { alerts = JSON.parse(dataEl.textContent || '[]'); } catch(e){ alerts = []; }

  const modalEl = document.getElementById('alertsModal');
  const openBtn = document.getElementById('openAlertsModalBtn');
  const closeBtn = document.getElementById('alertsModalClose');
  const listEl = document.getElementById('alertsModalList');
  const filterSelect = document.getElementById('alertsFilter');
  const filterSelectModal = document.getElementById('alertsFilterModal');
  const perPage = 20;
  let currentPage = 1;
  let currentFilter = 'ALL';

  function formatDate(s){
    try { return new Date(s).toLocaleString('pt-BR'); } catch(e){ return s; }
  }

  function getFiltered(){
    if(currentFilter === 'ALL') return alerts;
    return alerts.filter(a => (a.level||'').toUpperCase() === currentFilter);
  }

  function renderPage(page){
    currentPage = page;
    const filtered = getFiltered();
    const total = filtered.length;
    const start = (page-1)*perPage;
    const pageItems = filtered.slice(start, start+perPage);
    listEl.innerHTML = pageItems.map((a, idx) => `<tr><td>${start+idx+1}</td><td>${formatDate(a.created_at)}</td><td>${a.level}</td><td>${a.message}</td></tr>`).join('\n') || '<tr><td colspan="4" class="text-muted text-center">Sem alertas</td></tr>';
    renderPagination(Math.ceil(total/perPage));
  }

  function renderPagination(pages){
    const pagEl = document.getElementById('alertsModalPagination');
    if(!pagEl) return;
    if(pages <= 1){ pagEl.innerHTML = ''; return; }
    let html = '';
    for(let i=1;i<=pages;i++){
      html += `<li class="page-item ${i===currentPage?'active':''}"><a class="page-link" href="#" data-page="${i}">${i}</a></li>`;
    }
    pagEl.innerHTML = html;
    pagEl.querySelectorAll('a[data-page]').forEach(el=>el.addEventListener('click', function(e){ e.preventDefault(); renderPage(parseInt(this.dataset.page)); }));
  }

  if(openBtn && modalEl){
    openBtn.addEventListener('click', function(e){
      e.preventDefault();
      // show bootstrap modal
      const bs = new bootstrap.Modal(modalEl);
      bs.show();
      renderPage(1);
    });
  }
  if(filterSelect){
    filterSelect.addEventListener('change', function(){
      currentFilter = this.value;
      // update modal select if present
      if(filterSelectModal) filterSelectModal.value = currentFilter;
      renderPage(1);
    });
  }
  if(filterSelectModal){
    filterSelectModal.addEventListener('change', function(){
      currentFilter = this.value;
      if(filterSelect) filterSelect.value = currentFilter;
      renderPage(1);
    });
  }

})();
