(function () {
  'use strict';

  const content = document.querySelector('.panel-content');
  if (!content) return;

  const ajaxHeaders = {
    'X-Requested-With': 'XMLHttpRequest',
    'Accept': 'text/html'
  };
  let latestPanelRequest = 0;

  function showError(message) {
    const section = content.querySelector('[data-panel-ajax]') || content;
    let alert = section.querySelector('[data-panel-ajax-error]');

    if (!alert) {
      alert = document.createElement('div');
      alert.className = 'alert alert-danger';
      alert.setAttribute('role', 'alert');
      alert.setAttribute('aria-live', 'assertive');
      alert.dataset.panelAjaxError = '';
      section.prepend(alert);
    }

    alert.textContent = message;
  }

  async function loadPanel(url, options, addHistory) {
    const requestId = ++latestPanelRequest;
    let response;

    try {
      response = await fetch(url, {
        credentials: 'same-origin',
        ...options,
        headers: { ...ajaxHeaders, ...(options && options.headers) }
      });
    } catch (error) {
      if (requestId !== latestPanelRequest) return;
      throw error;
    }

    if (requestId !== latestPanelRequest) return;

    if (!response.ok) {
      throw new Error(`La solicitud falló (HTTP ${response.status}).`);
    }

    const html = await response.text().catch((error) => {
      if (requestId === latestPanelRequest) throw error;
    });
    if (requestId !== latestPanelRequest) return;

    const nextDocument = new DOMParser().parseFromString(html, 'text/html');
    const nextContent = nextDocument.querySelector('.panel-content');

    if (!nextContent) {
      window.location.assign(response.url);
      return;
    }

    content.innerHTML = nextContent.innerHTML;

    const nextSidebar = nextDocument.querySelector('.panel-sidebar');
    const sidebar = document.querySelector('.panel-sidebar');
    if (nextSidebar && sidebar) sidebar.replaceWith(nextSidebar);

    const nextUserLink = nextDocument.querySelector('.site-navigation-actions a.text-white');
    const userLink = document.querySelector('.site-navigation-actions a.text-white');
    if (nextUserLink && userLink) userLink.textContent = nextUserLink.textContent;

    if (nextDocument.title) document.title = nextDocument.title;

    if (addHistory && response.url !== window.location.href) {
      window.history.pushState({}, '', response.url);
    }
  }

  function isSameOrigin(url) {
    return url.origin === window.location.origin;
  }

  document.addEventListener('click', function (event) {
    const link = event.target.closest('a');
    if (
      !link ||
      event.defaultPrevented ||
      event.button !== 0 ||
      event.metaKey ||
      event.ctrlKey ||
      event.shiftKey ||
      event.altKey ||
      link.target ||
      link.hasAttribute('download') ||
      (!link.closest('[data-panel-ajax]') && !link.hasAttribute('data-panel-ajax-link'))
    ) {
      return;
    }

    const url = new URL(link.href, window.location.href);
    if (!isSameOrigin(url) || (url.pathname === window.location.pathname && url.hash)) return;

    event.preventDefault();
    loadPanel(url, { method: 'GET' }, true).catch(() => {
      showError('No se pudo cargar esta sección. Inténtalo de nuevo.');
    });
  });

  document.addEventListener('submit', function (event) {
    const form = event.target;
    if (!form.closest('[data-panel-ajax]')) return;

    event.preventDefault();
    if (form.dataset.ajaxPending) return;
    form.dataset.ajaxPending = 'true';
    form.setAttribute('aria-busy', 'true');

    const method = (form.method || 'GET').toUpperCase();
    const url = new URL(form.action || window.location.href, window.location.href);
    const formData = new FormData(form);
    const options = { method };

    if (method === 'GET') {
      formData.forEach((value, key) => url.searchParams.set(key, value.toString()));
    } else {
      options.body = formData;
    }

    if (!isSameOrigin(url)) {
      delete form.dataset.ajaxPending;
      form.removeAttribute('aria-busy');
      return;
    }

    loadPanel(url, options, true)
      .catch(() => {
        showError('No se pudo completar la solicitud. Verifica tu conexión e inténtalo de nuevo.');
      })
      .finally(() => {
        delete form.dataset.ajaxPending;
        form.removeAttribute('aria-busy');
      });
  });

  window.addEventListener('popstate', function () {
    loadPanel(window.location.href, { method: 'GET' }, false).catch(() => {
      showError('No se pudo cargar esta sección. Inténtalo de nuevo.');
    });
  });
})();
