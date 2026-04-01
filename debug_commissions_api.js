// Verificar APIs de comissões
console.log('🔍 Verificando APIs de comissões');

// Verificar API de resumo
fetch('/api/admin/commissions/summary')
    .then(response => {
        console.log('📊 Summary API Status:', response.status);
        return response.json();
    })
    .then(data => {
        console.log('📊 Summary API Response:', data);
        if (data.ok) {
            console.log('✅ Summary API OK - Dados:', data.summary);
        } else {
            console.log('❌ Summary API Error:', data.error);
        }
    })
    .catch(error => {
        console.log('❌ Summary API Error:', error);
    });

// Verificar API de lista
fetch('/api/admin/commissions/list')
    .then(response => {
        console.log('📋 List API Status:', response.status);
        return response.json();
    })
    .then(data => {
        console.log('📋 List API Response:', data);
        if (data.ok) {
            console.log('✅ List API OK - Comissões:', data.commissions?.length || 0);
            if (data.commissions && data.commissions.length > 0) {
                console.log('📋 Primeira comissão:', data.commissions[0]);
            } else {
                console.log('⚠️ Nenhuma comissão encontrada');
            }
        } else {
            console.log('❌ List API Error:', data.error);
        }
    })
    .catch(error => {
        console.log('❌ List API Error:', error);
    });

// Verificar se há erros no console da página
console.log('🔍 Verificando console da página...');
setTimeout(() => {
    const errorElements = document.querySelectorAll('[class*="error"]');
    console.log('📨 Elementos de erro na página:', errorElements.length);
    if (errorElements.length > 0) {
        errorElements.forEach((el, i) => {
            console.log(`  ${i + 1}: ${el.textContent}`);
        });
    }
    
    // Verificar conteúdo da tabela
    const tbody = document.getElementById('commissionsTableBody');
    if (tbody) {
        console.log('📋 Conteúdo da tabela:', tbody.innerHTML);
    }
}, 1000);
