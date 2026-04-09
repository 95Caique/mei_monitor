
function toggleSidebar() {
  const sidebar = document.getElementById('sidebar');
  const main = document.getElementById('main');
  sidebar.classList.toggle('collapsed');
  main.classList.toggle('shifted');
}

function openMobileMenu() {
  const sidebar = document.getElementById('sidebar');
  const overlay = document.getElementById('mobile-overlay');
  sidebar.classList.add('mobile-open');
  overlay.classList.add('show');
}

function closeMobileMenu() {
  const sidebar = document.getElementById('sidebar');
  const overlay = document.getElementById('mobile-overlay');
  sidebar.classList.remove('mobile-open');
  overlay.classList.remove('show');
}

function navigate(pageId, navElement) {
  const pages = document.querySelectorAll('.page');
  pages.forEach(page => page.classList.remove('active'));

  const targetPage = document.getElementById('page-' + pageId);
  if (targetPage) {
    targetPage.classList.add('active');
  }

  const navItems = document.querySelectorAll('.nav-item');
  navItems.forEach(item => item.classList.remove('active'));
  if (navElement) {
    navElement.classList.add('active');
  }

  const breadcrumb = document.getElementById('topbar-breadcrumb');
  if (breadcrumb) {
    const label = navElement?.textContent?.trim() || 'Dashboard';
    breadcrumb.innerHTML = `
      Sistema
      <svg class="chevron" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <polyline points="9 18 15 12 9 6"/>
      </svg>
      <strong>${label}</strong>
    `;
  }

  if (window.innerWidth <= 768) {
    closeMobileMenu();
  }
}

function animateCounter(element, start, end, duration = 1000) {
  if (start === end) {
    element.textContent = formatNumber(end);
    return;
  }

  const range = end - start;
  const increment = range / (duration / 16);
  let current = start;

  const timer = setInterval(() => {
    current += increment;
    if ((increment > 0 && current >= end) || (increment < 0 && current <= end)) {
      current = end;
      clearInterval(timer);
    }
    element.textContent = formatNumber(Math.round(current * 100) / 100);
  }, 16);
}

function formatNumber(num) {
  return new Intl.NumberFormat('pt-BR', {
    minimumFractionDigits: 0,
    maximumFractionDigits: 2,
  }).format(num);
}

document.addEventListener('DOMContentLoaded', function() {
  // Menu mobile close ao clicar no overlay
  const overlay = document.getElementById('mobile-overlay');
  if (overlay) {
    overlay.addEventListener('click', closeMobileMenu);
  }

  const mobileToggle = document.querySelector('.mobile-toggle');
  if (mobileToggle) {
    mobileToggle.addEventListener('click', openMobileMenu);
  }

  const navItems = document.querySelectorAll('.nav-item');
  navItems.forEach(item => {
    item.addEventListener('click', function() {
      if (window.innerWidth <= 768) {
        closeMobileMenu();
      }
    });
  });

  const activePage = document.querySelector('.page.active');
  if (activePage) {
    activePage.style.animation = 'fadeUp .28s ease both';
  }
});

function formatCurrency(value) {
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value);
}

function formatPercent(value) {
  return (Math.round(value * 100) / 100).toFixed(2) + '%';
}

