/**
 * Base URL da API.
 * Local (localhost): mesmo origin, usa ''.
 * Produção (Vercel etc.): Railway.
 */
(function() {
  var isLocal = /localhost|127\.0\.0\.1/.test(window.location.hostname);
  window.API_BASE = isLocal ? '' : 'https://projetoportos-production.up.railway.app';
})();
