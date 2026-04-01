// Verificar permissões específicas para gestão de comissões
console.log('🔍 Verificação de permissões de comissões');

// Verificar se estamos na página de login
if (window.location.href.includes('/login')) {
    console.log('❌ Estamos no login - verificar porquê');
    
    // Fazer uma chamada API para verificar a sessão
    fetch('/api/user-session')
        .then(response => response.json())
        .then(data => {
            console.log('📋 Dados da sessão:', data);
            console.log('🔑 can_manage_commissions:', data.can_manage_commissions);
            console.log('🔑 is_admin:', data.is_admin);
            console.log('🔑 username:', data.username);
            
            if (!data.can_manage_commissions) {
                console.log('❌ PROBLEMA: can_manage_commissions é FALSE!');
                console.log('🔧 É preciso atualizar esta permissão na base de dados');
            } else {
                console.log('✅ can_manage_commissions está OK');
            }
        })
        .catch(error => {
            console.log('❌ Erro ao verificar sessão:', error);
        });
} else {
    console.log('✅ Não estamos no login');
    console.log('URL atual:', window.location.href);
    
    // Verificar se conseguimos aceder à API de sessão
    fetch('/api/user-session')
        .then(response => {
            console.log('📡 Resposta da API de sessão:', response.status);
            return response.json();
        })
        .then(data => {
            console.log('📋 Dados da sessão:', data);
        })
        .catch(error => {
            console.log('❌ Erro na API de sessão:', error);
        });
}

// Verificar se o ícone de comissões está visível
const commissionsIcon = document.querySelector('a[href="/admin/commissions"]');
if (commissionsIcon) {
    console.log('✅ Ícone de comissões encontrado no HTML');
    console.log('👁️ Está visível?', commissionsIcon.offsetParent !== null);
    console.log('🎨 Tem estilo display:none?', getComputedStyle(commissionsIcon).display === 'none');
} else {
    console.log('❌ Ícone de comissões NÃO encontrado');
    console.log('🔍 Todos os links admin:', Array.from(document.querySelectorAll('a[href*="admin"]')).map(a => a.href));
}
