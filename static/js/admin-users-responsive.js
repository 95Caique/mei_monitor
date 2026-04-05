/**
 * Admin Users - Responsive Layout Switcher
 * A responsividade agora e feita via CSS media queries (@see admin-users-responsive.css)
 * Este script mantem-se para garantir compatibilidade com orientation change.
 */

(function() {
  function setupResponsiveLayout() {
    var desktopTable = document.querySelector('.table-responsive');
    var mobileCards = document.querySelector('.mei-table-mobile');

    if (!desktopTable || !mobileCards) return;

    function updateLayout() {
      if (window.innerWidth < 768) {
        desktopTable.style.display = 'none';
        mobileCards.style.display = 'grid';
      } else {
        desktopTable.style.display = 'block';
        mobileCards.style.display = 'none';
      }
    }

    updateLayout();
    window.addEventListener('resize', updateLayout);
    window.addEventListener('orientationchange', updateLayout);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', setupResponsiveLayout);
  } else {
    setupResponsiveLayout();
  }
})();
