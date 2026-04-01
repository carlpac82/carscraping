// Verificar se a página de comissões está a carregar corretamente
console.log('🔍 Verificação da página de comissões');

// Verificar URL atual
console.log('URL atual:', window.location.href);

// Verificar se estamos na página de comissões
if (window.location.href.includes('/admin/commissions')) {
    console.log('✅ Estamos na página de comissões');
    
    // Verificar se o conteúdo da página está visível
    const mainContent = document.querySelector('main') || document.body;
    if (mainContent) {
        console.log('✅ Conteúdo principal encontrado');
        console.log('Título da página:', document.title);
        
        // Procurar elementos específicos da página de comissões
        const headers = document.querySelectorAll('h1, h2, h3');
        console.log('Headers encontrados:', Array.from(headers).map(h => h.textContent));
        
        // Procurar tabelas ou cards
        const tables = document.querySelectorAll('table');
        const cards = document.querySelectorAll('[class*="card"], [class*="summary"]');
        console.log('Tabelas:', tables.length);
        console.log('Cards:', cards.length);
        
        // Verificar se há algum erro visível
        const errorElements = document.querySelectorAll('[class*="error"], [class*="alert"]');
        console.log('Elementos de erro:', errorElements.length);
    } else {
        console.log('❌ Conteúdo principal não encontrado');
    }
} else {
    console.log('❌ Não estamos na página de comissões');
}

// Verificar se há algum JavaScript error
console.log('Erros JavaScript:', window.errorCount || 0);

// Verificar se há chamadas API em progresso
if (window.fetch) {
    const originalFetch = window.fetch;
    window.fetch = function(...args) {
        console.log('📡 Chamada API:', args[0]);
        return originalFetch.apply(this, args).then(response => {
            console.log('📡 Resposta API:', args[0], response.status);
            return response;
        }).catch(error => {
            console.log('❌ Erro API:', args[0], error);
            throw error;
        });
    };
}
