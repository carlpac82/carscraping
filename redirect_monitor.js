// Monitorar redirecionamentos em tempo real
console.log('🔍 Monitor de redirecionamentos ativado');

// Guardar URL atual
let currentUrl = window.location.href;
console.log('URL inicial:', currentUrl);

// Interceptar mudanças de URL
const originalPushState = history.pushState;
const originalReplaceState = history.replaceState;

history.pushState = function(...args) {
    console.log('🔄 pushState:', args[2]);
    return originalPushState.apply(this, args);
};

history.replaceState = function(...args) {
    console.log('🔄 replaceState:', args[2]);
    return originalReplaceState.apply(this, args);
};

// Monitorar mudanças de hash
window.addEventListener('hashchange', () => {
    console.log('🔄 hashchange:', window.location.href);
});

// Interceptar todos os cliques
document.addEventListener('click', (e) => {
    const target = e.target.closest('a');
    if (target) {
        console.log('🖱️ Clique detectado:', target.href);
        console.log('🖱️ Texto do link:', target.textContent);
        console.log('🖱️ Tem title?', target.title);
    }
});

// Verificar se o ícone de comissões existe
const commissionsIcon = document.querySelector('a[href="/admin/commissions"]');
if (commissionsIcon) {
    console.log('✅ Ícone de comissões encontrado');
    console.log('🖱️ href:', commissionsIcon.href);
    console.log('🖱️ visível:', commissionsIcon.offsetParent !== null);
    
    // Adicionar listener específico para este ícone
    commissionsIcon.addEventListener('click', (e) => {
        console.log('🎯 CLIQUE NO ÍCONE DE COMISSÕES!');
        console.log('🎯 URL antes do clique:', window.location.href);
        console.log('🎯 href do ícone:', commissionsIcon.href);
        
        // Impedir o comportamento padrão para ver o que acontece
        e.preventDefault();
        console.log('🎯 Comportamento padrão impedido');
        
        // Tentar navegar manualmente
        setTimeout(() => {
            console.log('🎯 Tentando navegar manualmente...');
            window.location.href = '/admin/commissions';
        }, 100);
    });
} else {
    console.log('❌ Ícone de comissões NÃO encontrado');
    console.log('Todos os links:', Array.from(document.querySelectorAll('a')).map(a => a.href));
}

// Verificar mudanças de URL a cada 100ms
setInterval(() => {
    if (window.location.href !== currentUrl) {
        console.log('🔄 URL mudou de:', currentUrl);
        console.log('🔄 URL mudou para:', window.location.href);
        currentUrl = window.location.href;
    }
}, 100);
