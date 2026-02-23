(function(){
  const dataEl = document.getElementById('alertsAllData');
  if(!dataEl) return;
  let alerts = [];
  try { alerts = JSON.parse(dataEl.textContent || '[]'); } catch(e){ alerts = []; }

  const modalEl = document.getElementById('alertsModal');
  const openBtn = document.getElementById('openAlertsModalBtn');
  const closeBtn = document.getElementById('alertsModalClose');
  const listEl = document.getElementById('alertsModalList');
  const cardListEl = document.getElementById('alertsCardList');
  const cardPagEl = document.getElementById('alertsCardPagination');
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

  // compact list util
  function compactPageList(current, total, maxBlocks){
    if(total <= maxBlocks) return Array.from({length: total}, (_,i)=>i+1);
    const pages = [];
    pages.push(1);
    const inner = maxBlocks - 2;
    let start = current - Math.floor(inner/2);
    let end = start + inner - 1;
    if(start < 2){ start = 2; end = start + inner - 1; }
    if(end > total - 1){ end = total - 1; start = end - (inner - 1); if(start < 2) start = 2; }
    if(start > 2) pages.push('...');
    for(let i=start;i<=end;i++) pages.push(i);
    if(end < total - 1) pages.push('...');
    pages.push(total);
    return pages;
  }

  // RENDER MODAL
  function renderModalPage(page){
    currentPage = page;
    const filtered = getFiltered();
    const total = filtered.length;
    const start = (page-1)*perPage;
    const pageItems = filtered.slice(start, start+perPage);
    if(listEl) {
      listEl.innerHTML = pageItems.map((a, idx) => `<tr><td>${start+idx+1}</td><td>${formatDate(a.created_at)}</td><td>${(a.level||'').replace(/_/g,' ')}</td><td>${a.message}</td></tr>`).join('\n') || '<tr><td colspan="4" class="text-muted text-center">Sem alertas</td></tr>';
    }
    renderModalPagination(Math.ceil(total/perPage));
  }

  function renderModalPagination(pages){
    const pagEl = document.getElementById('alertsModalPagination');
    if(!pagEl) return;
    if(pages <= 1){ pagEl.innerHTML = ''; return; }
    const maxBlocks = 4;
    const list = compactPageList(currentPage, pages, maxBlocks);
    let html = '';
    html += `<li class="page-item ${currentPage===1? 'disabled':''}"><a class="page-link" href="#" data-page="${Math.max(1,currentPage-1)}">&laquo;</a></li>`;
    list.forEach(p => { if(p === '...') html += `<li class="page-item disabled"><span class="page-link">…</span></li>`; else html += `<li class="page-item ${p===currentPage? 'active':''}"><a class="page-link" href="#" data-page="${p}">${p}</a></li>`; });
    html += `<li class="page-item ${currentPage===pages? 'disabled':''}"><a class="page-link" href="#" data-page="${Math.min(pages,currentPage+1)}">&raquo;</a></li>`;
    pagEl.innerHTML = html;
    pagEl.querySelectorAll('a[data-page]').forEach(el=>el.addEventListener('click', function(e){ e.preventDefault(); renderModalPage(parseInt(this.dataset.page)); }));
    try{ pagEl.scrollLeft = 0; }catch(e){}
  }

  // RENDER CARD (alertas recentes)
  function renderCardPage(page){
    const filtered = getFiltered();
    const total = filtered.length;
    if(!cardListEl) return;
    const start = (page-1)*perPage;
    const pageItems = filtered.slice(start, start+perPage);
    cardListEl.innerHTML = pageItems.map((a, idx) => `<li class="list-group-item alert-item"><strong>[${(a.level||'').replace(/_/g,' ')}]</strong> ${a.message} <small class="text-muted">(${formatDate(a.created_at)})</small></li>`).join('\n') || '<li class="list-group-item text-muted text-center">Sem alertas</li>';
    renderCardPagination(Math.ceil(total/perPage), page);
  }

  function renderCardPagination(pages, current){
    if(!cardPagEl) return;
    if(pages <= 1){ cardPagEl.innerHTML = ''; return; }
    const maxBlocks = 4;
    const list = compactPageList(current, pages, maxBlocks);
    let html = '';
    html += `<li class="page-item ${current===1? 'disabled':''}"><a class="page-link" href="#" data-page="${Math.max(1,current-1)}">&laquo;</a></li>`;
    list.forEach(p => { if(p === '...') html += `<li class="page-item disabled"><span class="page-link">…</span></li>`; else html += `<li class="page-item ${p===current? 'active':''}"><a class="page-link" href="#" data-page="${p}">${p}</a></li>`; });
    html += `<li class="page-item ${current===pages? 'disabled':''}"><a class="page-link" href="#" data-page="${Math.min(pages,current+1)}">&raquo;</a></li>`;
    cardPagEl.innerHTML = html;
    cardPagEl.querySelectorAll('a[data-page]').forEach(el=>el.addEventListener('click', function(e){ e.preventDefault(); const p = parseInt(this.dataset.page); renderCardPage(p); }));
    try{ cardPagEl.scrollLeft = 0; }catch(e){}
  }

  // initialize card on load
  function initCard(){
    try{ renderCardPage(1); }catch(e){}
  }

  if(openBtn && modalEl){
    openBtn.addEventListener('click', function(e){
      e.preventDefault();
      const bs = new bootstrap.Modal(modalEl);
      bs.show();
      try{
        modalEl.addEventListener('shown.bs.modal', function onShown(){
          modalEl.removeEventListener('shown.bs.modal', onShown);
          renderModalPage(1);
          const pagEl = document.getElementById('alertsModalPagination'); try{ if(pagEl) pagEl.scrollLeft = 0; } catch(e){}
        });
        setTimeout(()=>{ try{ renderModalPage(1); const pagEl=document.getElementById('alertsModalPagination'); if(pagEl) pagEl.scrollLeft=0; }catch(e){} }, 150);
      }catch(e){ renderModalPage(1); }
    });
  }

  if(filterSelect){
    filterSelect.addEventListener('change', function(){
      currentFilter = this.value;
      if(filterSelectModal) filterSelectModal.value = currentFilter;
      initCard();
    });
  }
  if(filterSelectModal){
    filterSelectModal.addEventListener('change', function(){
      currentFilter = this.value;
      if(filterSelect) filterSelect.value = currentFilter;
      renderModalPage(1);
      initCard();
    });
  }

  if(document.readyState === 'loading') document.addEventListener('DOMContentLoaded', initCard);
  else initCard();

})();
