// Cole este código no console do browser (F12) quando estiver na página de comissões

// 1. Verificar se os dados estão sendo enviados ao marcar como pago
console.log('=== DEBUG: Interceptar chamada de mark-paid ===');

// Sobrescrever a função submitPaymentStatus para ver o que está sendo enviado
const originalFetch = window.fetch;
window.fetch = async function(...args) {
    const [url, options] = args;
    
    if (url.includes('mark-paid')) {
        console.log('🔍 Chamada para mark-paid detectada!');
        console.log('URL:', url);
        console.log('Body enviado:', options.body);
        
        try {
            const bodyData = JSON.parse(options.body);
            console.log('📦 Dados parseados:');
            console.log('  - commission_ids:', bodyData.commission_ids);
            console.log('  - receiver_name:', bodyData.receiver_name);
            console.log('  - signature (primeiros 100 chars):', bodyData.signature ? bodyData.signature.substring(0, 100) : 'VAZIO');
        } catch (e) {
            console.error('Erro ao parsear body:', e);
        }
    }
    
    const response = await originalFetch.apply(this, args);
    
    if (url.includes('mark-paid')) {
        const clonedResponse = response.clone();
        const responseData = await clonedResponse.json();
        console.log('📥 Resposta do servidor:', responseData);
    }
    
    return response;
};

console.log('✅ Debug ativado! Agora marque uma comissão como paga e veja os logs aqui.');
