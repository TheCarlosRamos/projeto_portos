/**
 * Configuração da API
 * Detecta automaticamente se está em localhost ou produção
 */
(function() {
    const isLocal = /localhost|127\.0\.0\.1/.test(window.location.hostname);
    
    // Em localhost usa a API local, em produção usa a URL do backend no Vercel
    window.API_BASE = isLocal 
        ? 'http://localhost:8000' 
        : 'https://projeto-portos-backend.vercel.app';  // URL do backend no Vercel
    
    console.log('API Base URL:', window.API_BASE);
})();
