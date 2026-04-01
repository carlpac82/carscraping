// Verificar estado da sessão e autenticação
console.log('🔍 Verificação de autenticação');

// Verificar se há cookies de sessão
console.log('Cookies:', document.cookie);

// Verificar se estamos na página de login
if (window.location.href.includes('/login')) {
    console.log('❌ Fomos redirecionados para o login');
    console.log('URL original que tentámos aceder:', document.referrer);
    
    // Verificar se há mensagem de erro
    const errorElements = document.querySelectorAll('[class*="error"], [class*="alert"]');
    console.log('Mensagens de erro:', Array.from(errorElements).map(e => e.textContent));
    
    // Tentar fazer login automaticamente se já tivermos credenciais guardadas
    const usernameInput = document.querySelector('input[name="username"], input[type="text"]');
    const passwordInput = document.querySelector('input[name="password"], input[type="password"]');
    const submitButton = document.querySelector('button[type="submit"], input[type="submit"]');
    
    console.log('Formulário de login encontrado:', {
        username: !!usernameInput,
        password: !!passwordInput,
        submit: !!submitButton
    });
    
    // Se tivermos localStorage com credenciais, tentar preencher
    const savedUsername = localStorage.getItem('saved_username');
    const savedPassword = localStorage.getItem('saved_password');
    
    if (savedUsername && savedPassword && usernameInput && passwordInput) {
        console.log('🔑 Tentando login automático...');
        usernameInput.value = savedUsername;
        passwordInput.value = savedPassword;
        setTimeout(() => {
            submitButton?.click();
        }, 100);
    }
} else {
    console.log('✅ Não estamos na página de login');
    console.log('URL atual:', window.location.href);
    
    // Verificar se há algum indicador de sessão expirada
    const sessionWarnings = document.querySelectorAll('[class*="session"], [class*="expired"]');
    console.log('Avisos de sessão:', Array.from(sessionWarnings).map(e => e.textContent));
}

// Verificar timestamp da página
console.log('Timestamp atual:', new Date().toISOString());
console.log('Tempo desde último acesso:', performance.now());
