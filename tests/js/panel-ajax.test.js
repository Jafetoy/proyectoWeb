const { readFileSync } = require('node:fs');
const { resolve } = require('node:path');
const { test } = require('node:test');
const assert = require('node:assert/strict');
const { JSDOM } = require('jsdom');

const panelAjaxSource = readFileSync(
  resolve(__dirname, '../../canaco/static/js/panel-ajax.js'),
  'utf8'
);

function createPanelDom(content = '') {
  const dom = new JSDOM(
    `<!doctype html>
    <html>
      <head><title>Panel actual</title></head>
      <body>
        <div class="site-navigation-actions"><a class="text-white">Usuario actual</a></div>
        <aside class="panel-sidebar">Menú actual</aside>
        <main class="panel-content">${content}</main>
      </body>
    </html>`,
    {
      url: 'https://canaco.test/perfil/',
      runScripts: 'outside-only'
    }
  );

  return dom;
}

function nextPanelHtml({ content = 'Contenido nuevo', title = 'Panel nuevo' } = {}) {
  return `<!doctype html>
    <html>
      <head><title>${title}</title></head>
      <body>
        <div class="site-navigation-actions"><a class="text-white">Usuario actualizado</a></div>
        <aside class="panel-sidebar">Menú nuevo</aside>
        <main class="panel-content"><section data-panel-ajax>${content}</section></main>
      </body>
    </html>`;
}

function successfulResponse(url, html = nextPanelHtml()) {
  return {
    ok: true,
    status: 200,
    url,
    text: async () => html
  };
}

async function flushAsyncEvents() {
  await new Promise((resolvePromise) => setTimeout(resolvePromise, 0));
  await new Promise((resolvePromise) => setTimeout(resolvePromise, 0));
}

test('la navegación AJAX reemplaza el panel y actualiza el historial', async () => {
  const dom = createPanelDom(
    '<a data-panel-ajax-link href="/crud-usuarios/">Usuarios</a>'
  );
  const { window } = dom;
  const requests = [];
  const historyEntries = [];
  const originalPushState = window.history.pushState.bind(window.history);

  window.fetch = async (url, options) => {
    requests.push({ url: url.toString(), options });
    return successfulResponse('https://canaco.test/crud-usuarios/');
  };
  window.history.pushState = (state, title, url) => {
    historyEntries.push(url.toString());
    originalPushState(state, title, url);
  };
  window.eval(panelAjaxSource);

  const link = window.document.querySelector('[data-panel-ajax-link]');
  link.dispatchEvent(new window.MouseEvent('click', {
    bubbles: true,
    cancelable: true,
    button: 0
  }));
  await flushAsyncEvents();

  assert.equal(requests.length, 1);
  assert.equal(requests[0].url, 'https://canaco.test/crud-usuarios/');
  assert.equal(requests[0].options.method, 'GET');
  assert.equal(requests[0].options.credentials, 'same-origin');
  assert.equal(requests[0].options.headers['X-Requested-With'], 'XMLHttpRequest');
  assert.equal(requests[0].options.headers.Accept, 'text/html');
  assert.match(window.document.querySelector('.panel-content').textContent, /Contenido nuevo/);
  assert.match(window.document.querySelector('.panel-sidebar').textContent, /Menú nuevo/);
  assert.equal(window.document.querySelector('.site-navigation-actions a').textContent, 'Usuario actualizado');
  assert.equal(window.document.title, 'Panel nuevo');
  assert.deepEqual(historyEntries, ['https://canaco.test/crud-usuarios/']);
  assert.equal(window.location.pathname, '/crud-usuarios/');

  dom.window.close();
});

test('una respuesta anterior no altera la navegación más reciente', async () => {
  const dom = createPanelDom('<a data-panel-ajax-link href="/crud-usuarios/">Usuarios</a><a data-panel-ajax-link href="/crud-categorias/">Categorías</a>');
  const { window } = dom;
  const pendingRequests = new Map();
  const historyEntries = [];
  const originalPushState = window.history.pushState.bind(window.history);

  window.fetch = (url) => new Promise((resolvePromise) => pendingRequests.set(new URL(url.toString()).pathname, resolvePromise));
  window.history.pushState = (state, title, url) => { historyEntries.push(url.toString()); originalPushState(state, title, url); };
  window.eval(panelAjaxSource);

  const click = (link) => link.dispatchEvent(new window.MouseEvent('click',
    { bubbles: true, cancelable: true, button: 0 }));
  let [usersLink, categoriesLink] = window.document.querySelectorAll('[data-panel-ajax-link]');
  click(usersLink);
  click(categoriesLink);

  pendingRequests.get('/crud-categorias/')(successfulResponse('https://canaco.test/crud-categorias/',
    nextPanelHtml({ content: `Categorías recientes
      <a data-panel-ajax-link href="/crud-usuarios/">Usuarios</a>
      <a data-panel-ajax-link href="/crud-categorias/">Categorías</a>`, title: 'Categorías' })
  ));
  await flushAsyncEvents();
  pendingRequests.get('/crud-usuarios/')(successfulResponse('https://canaco.test/crud-usuarios/',
    nextPanelHtml({ content: 'Usuarios antiguos', title: 'Usuarios' })));
  await flushAsyncEvents();

  assert.match(window.document.querySelector('.panel-content').textContent, /Categorías recientes/);
  assert.equal(window.document.title, 'Categorías');
  assert.equal(window.location.pathname, '/crud-categorias/');
  assert.deepEqual(historyEntries, ['https://canaco.test/crud-categorias/']);

  [usersLink, categoriesLink] = window.document.querySelectorAll('[data-panel-ajax-link]');
  click(usersLink);
  let rejectOldBody;
  pendingRequests.get('/crud-usuarios/')({
    ok: true, status: 200, url: 'https://canaco.test/crud-usuarios/',
    text: () => new Promise((resolvePromise, rejectPromise) => { rejectOldBody = rejectPromise; })
  });
  await flushAsyncEvents();
  click(categoriesLink);
  pendingRequests.get('/crud-categorias/')(successfulResponse(
    'https://canaco.test/crud-categorias/', nextPanelHtml({ content: 'Categorías finales' })
  ));
  await flushAsyncEvents();
  rejectOldBody(new Error('stale response body failed')); await flushAsyncEvents();

  assert.match(window.document.querySelector('.panel-content').textContent, /Categorías finales/);
  assert.equal(window.document.querySelector('[data-panel-ajax-error]'), null);

  dom.window.close();
});

test('el envío POST conserva el token CSRF y evita envíos duplicados', async () => {
  const dom = createPanelDom(`
    <section data-panel-ajax>
      <form action="/guardar/" method="post">
        <input name="csrfmiddlewaretoken" value="csrf-token">
        <input name="nombre" value="Canaco">
        <button type="submit">Guardar</button>
      </form>
    </section>
  `);
  const { window } = dom;
  const requests = [];
  let resolveFetch;

  window.fetch = (url, options) => {
    requests.push({ url: url.toString(), options });
    return new Promise((resolvePromise) => {
      resolveFetch = resolvePromise;
    });
  };
  window.eval(panelAjaxSource);

  const form = window.document.querySelector('form');
  form.dispatchEvent(new window.SubmitEvent('submit', { bubbles: true, cancelable: true }));
  form.dispatchEvent(new window.SubmitEvent('submit', { bubbles: true, cancelable: true }));

  assert.equal(requests.length, 1);
  assert.equal(requests[0].options.method, 'POST');
  assert.equal(requests[0].options.body.get('csrfmiddlewaretoken'), 'csrf-token');
  assert.equal(requests[0].options.body.get('nombre'), 'Canaco');
  assert.equal(form.dataset.ajaxPending, 'true');
  assert.equal(form.getAttribute('aria-busy'), 'true');

  resolveFetch(successfulResponse('https://canaco.test/guardar/'));
  await flushAsyncEvents();

  assert.equal(form.dataset.ajaxPending, undefined);
  assert.equal(form.hasAttribute('aria-busy'), false);

  dom.window.close();
});

test('el envío GET convierte los campos del formulario en parámetros', async () => {
  const dom = createPanelDom(`
    <section data-panel-ajax>
      <form action="/buscar/" method="get">
        <input name="q" value="cámara empresarial">
      </form>
    </section>
  `);
  const { window } = dom;
  let requestedUrl;

  window.fetch = async (url) => {
    requestedUrl = new URL(url.toString());
    return successfulResponse(requestedUrl.toString());
  };
  window.eval(panelAjaxSource);

  window.document.querySelector('form').dispatchEvent(
    new window.SubmitEvent('submit', { bubbles: true, cancelable: true })
  );
  await flushAsyncEvents();

  assert.equal(requestedUrl.pathname, '/buscar/');
  assert.equal(requestedUrl.searchParams.get('q'), 'cámara empresarial');

  dom.window.close();
});

test('popstate recarga el panel sin crear otra entrada de historial', async () => {
  const dom = createPanelDom('<section data-panel-ajax>Contenido actual</section>');
  const { window } = dom;
  const historyEntries = [];

  window.fetch = async () => successfulResponse(
    'https://canaco.test/perfil/',
    nextPanelHtml({ content: 'Contenido restaurado' })
  );
  window.history.pushState = (state, title, url) => {
    historyEntries.push(url.toString());
  };
  window.eval(panelAjaxSource);

  window.dispatchEvent(new window.PopStateEvent('popstate'));
  await flushAsyncEvents();

  assert.match(window.document.querySelector('.panel-content').textContent, /Contenido restaurado/);
  assert.deepEqual(historyEntries, []);

  dom.window.close();
});

test('un fallo de red muestra un error accesible y libera el formulario', async () => {
  const dom = createPanelDom(`
    <section data-panel-ajax>
      <form action="/guardar/" method="post">
        <input name="csrfmiddlewaretoken" value="csrf-token">
      </form>
    </section>
  `);
  const { window } = dom;

  window.fetch = async () => {
    throw new Error('network unavailable');
  };
  window.eval(panelAjaxSource);

  const form = window.document.querySelector('form');
  form.dispatchEvent(new window.SubmitEvent('submit', { bubbles: true, cancelable: true }));
  await flushAsyncEvents();

  const alert = window.document.querySelector('[data-panel-ajax-error]');
  assert.ok(alert);
  assert.equal(alert.getAttribute('role'), 'alert');
  assert.equal(alert.getAttribute('aria-live'), 'assertive');
  assert.equal(
    alert.textContent,
    'No se pudo completar la solicitud. Verifica tu conexión e inténtalo de nuevo.'
  );
  assert.equal(form.dataset.ajaxPending, undefined);
  assert.equal(form.hasAttribute('aria-busy'), false);

  dom.window.close();
});
