(function () {
  const storageKey = 'canaco_welcome_modal_seen';

  function hasBeenShown() {
    try {
      return window.sessionStorage.getItem(storageKey) === 'true';
    } catch (error) {
      return false;
    }
  }

  function markAsShown() {
    try {
      window.sessionStorage.setItem(storageKey, 'true');
    } catch (error) {
      // The modal can still be shown when browser storage is unavailable.
    }
  }

  function initializeWelcomeModal() {
    const modalElement = document.querySelector('[data-welcome-modal]');

    if (!modalElement || !window.bootstrap?.Modal || hasBeenShown()) {
      return;
    }

    const showModal = function () {
      if (hasBeenShown()) {
        return;
      }

      markAsShown();
      window.bootstrap.Modal.getOrCreateInstance(modalElement).show();
    };

    const cookieBanner = document.getElementById('canaco-cookie-banner');

    if (!cookieBanner || cookieBanner.hidden) {
      showModal();
      return;
    }

    const observer = new MutationObserver(function () {
      if (cookieBanner.hidden) {
        observer.disconnect();
        showModal();
      }
    });

    observer.observe(cookieBanner, {
      attributes: true,
      attributeFilter: ['hidden'],
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeWelcomeModal, { once: true });
  } else {
    initializeWelcomeModal();
  }
})();
