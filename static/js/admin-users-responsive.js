
function setupResponsiveLayout() {
  const desktopTable = document.querySelector('.desktop-table');
  const mobileCards = document.querySelector('.mei-table-mobile');

  function updateLayout() {
    const width = window.innerWidth;

    if (width >= 768) {
      if (desktopTable) desktopTable.style.display = 'block';
      if (mobileCards) mobileCards.style.display = 'none';
    } else {
      if (desktopTable) desktopTable.style.display = 'none';
      if (mobileCards) mobileCards.style.display = 'block';
    }
  }

  updateLayout();

  window.addEventListener('resize', updateLayout);
  window.addEventListener('orientationchange', updateLayout);
}

document.addEventListener('DOMContentLoaded', setupResponsiveLayout);

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', setupResponsiveLayout);
} else {
  setupResponsiveLayout();
}

