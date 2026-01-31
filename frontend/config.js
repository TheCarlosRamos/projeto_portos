/**
 * Configuração da API
 * Detecta automaticamente se está em localhost ou produção
 */
(function() {
    const isLocal = /localhost|127\.0\.0\.1/.test(window.location.hostname);
    
    // Em localhost usa a API local, em produção usa a URL do Railway
    window.API_BASE = isLocal 
        ? 'http://localhost:8000' 
        : 'https://seu-backend.up.railway.app';  // SUBSTITUIR pela URL real do Railway
    
    console.log('API Base URL:', window.API_BASE);
})();
