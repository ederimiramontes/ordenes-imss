/**
 * Service Worker — Sistema de Gestión de Órdenes BC
 * Estrategia: cache-first para el shell de la app (HTML/CSS/JS).
 * Network-first para todo lo que vaya a Supabase (datos en vivo).
 * Resultado: la interfaz carga aunque haya red lenta o intermitente.
 * Los datos siguen requiriendo conexión — es un sistema transaccional.
 */

const CACHE   = 'so-bc-v1';
const SHELL   = ['./'];          // index.html principal

// ── INSTALL: pre-cachear el shell ──────────────────────────────
self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(CACHE)
      .then(c => c.addAll(SHELL))
      .then(() => self.skipWaiting())
  );
});

// ── ACTIVATE: limpiar cachés viejas ───────────────────────────
self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys()
      .then(keys => Promise.all(
        keys.filter(k => k !== CACHE).map(k => caches.delete(k))
      ))
      .then(() => self.clients.claim())
  );
});

// ── FETCH: decidir estrategia por destino ─────────────────────
self.addEventListener('fetch', e => {
  const url = e.request.url;

  // Supabase, Google Fonts, CDNs → siempre red (datos en vivo)
  if (url.includes('supabase.co') ||
      url.includes('googleapis.com') ||
      url.includes('cdnjs.cloudflare.com') ||
      url.includes('jsdelivr.net')) {
    return; // deja que el browser maneje con su propio caché HTTP
  }

  // Solo same-origin (GitHub Pages)
  if (!url.startsWith(self.location.origin)) return;

  // Shell de la app → cache-first con fallback a red
  e.respondWith(
    caches.match(e.request).then(cached => {
      if (cached) return cached;
      return fetch(e.request).then(response => {
        // solo cachear respuestas válidas
        if (response && response.status === 200 && response.type === 'basic') {
          const clone = response.clone();
          caches.open(CACHE).then(c => c.put(e.request, clone));
        }
        return response;
      }).catch(() => caches.match('./'));  // fallback al index si todo falla
    })
  );
});
