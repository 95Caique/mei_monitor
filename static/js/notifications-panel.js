
let lastNotificationCheck = null;

function toggleNotifications() {
  const panel = document.getElementById('notificationsPanel');
  if (panel) {
    const isOpen = panel.classList.contains('show');
    if (!isOpen) {
      openNotifications();
    } else {
      closeNotifications();
    }
  }
}

function openNotifications() {
  const panel = document.getElementById('notificationsPanel');
  if (panel) {
    panel.classList.add('show');
    loadNotifications();
  }
}

function closeNotifications() {
  const panel = document.getElementById('notificationsPanel');
  if (panel) {
    panel.classList.remove('show');
  }
}

function loadNotifications() {
  const body = document.getElementById('notificationsBody');
  if (!body) return;

  body.innerHTML = `
    <div style="padding: 48px 20px; text-align: center; color: var(--text-muted);">
      <div style="font-size: 24px; margin-bottom: 12px;">⏳</div>
      <p>Carregando alertas...</p>
    </div>
  `;

  const since = new Date();
  since.setDate(since.getDate() - 30); // Últimos 30 dias
  const sinceISO = since.toISOString();

  fetch(`/api/notifications/?since=${encodeURIComponent(sinceISO)}`)
    .then(response => {
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      return response.json();
    })
    .then(data => {
      if (!data || !data.alerts || data.alerts.length === 0) {
        body.innerHTML = `
          <div style="padding: 48px 20px; text-align: center; color: var(--text-muted);">
            <div style="font-size: 48px; margin-bottom: 16px; opacity: .3;">🔔</div>
            <p>Sem alertas recentes.</p>
          </div>
        `;
        return;
      }

      let html = '';
      data.alerts.forEach(alert => {
        html += renderNotificationItem(alert);
      });

      body.innerHTML = html;
      lastNotificationCheck = new Date();
    })
    .catch(err => {
      console.error('Erro ao carregar notificações:', err);
      body.innerHTML = `
        <div style="padding: 48px 20px; text-align: center; color: var(--red);">
          <div style="font-size: 48px; margin-bottom: 16px; opacity: .3;">⚠️</div>
          <p>Erro ao carregar alertas.</p>
          <small style="color: var(--text-muted); margin-top: 8px; display: block;">${err.message}</small>
        </div>
      `;
    });
}

function renderNotificationItem(alert) {
  const level = (alert.level || 'INFO').toUpperCase();
  const message = alert.message || 'Sem mensagem';
  const createdAt = formatDate(alert.created_at);

  let iconClass = 'info';
  let iconEmoji = 'ℹ️';

  if (level === 'CRITICAL' || level === 'ERROR') {
    iconClass = 'critical';
    iconEmoji = '❌';
  } else if (level === 'WARNING') {
    iconClass = 'warning';
    iconEmoji = '⚠️';
  }

  return `
    <div class="notification-item">
      <div class="notification-item-icon ${iconClass}">
        ${iconEmoji}
      </div>
      <div class="notification-item-content">
        <div class="notification-item-title">${level}</div>
        <div class="notification-item-message">${message}</div>
        <div class="notification-item-time">${createdAt}</div>
      </div>
    </div>
  `;
}

function formatDate(dateStr) {
  try {
    const date = new Date(dateStr);
    return date.toLocaleString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  } catch (e) {
    return dateStr;
  }
}

// Fechar painel ao clicar fora
document.addEventListener('click', function(e) {
  const panel = document.getElementById('notificationsPanel');
  const btn = document.getElementById('notificationsBtn');

  if (panel && btn && !panel.contains(e.target) && !btn.contains(e.target)) {
    closeNotifications();
  }
});

// Fechar painel ao pressionar ESC
document.addEventListener('keydown', function(e) {
  if (e.key === 'Escape') {
    closeNotifications();
  }
});

// Recarregar notificações periodicamente (a cada 20 segundos)
setInterval(function() {
  const panel = document.getElementById('notificationsPanel');
  if (panel && panel.classList.contains('show')) {
    loadNotifications();
  }
}, 20000);


