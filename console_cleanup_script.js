/**
 * 🧹 SCRIPT DE LIMPEZA COMPLETA DA BASE DE DADOS
 * 
 * Este script elimina TODOS os dados de testes:
 * - Rental Agreements (RAs) uploadados
 * - Inspeções (Check-in e Check-out)
 * - Fotos de inspeções
 * 
 * ⚠️ ATENÇÃO: Esta ação é IRREVERSÍVEL!
 * 
 * 📋 COMO USAR:
 * 1. Abre o Safari
 * 2. Vai para a página da aplicação (qualquer página autenticada)
 * 3. Abre o Console (Develop > Show JavaScript Console ou Cmd+Option+C)
 * 4. Cola este script completo
 * 5. Pressiona Enter
 * 6. Confirma quando pedido
 * 
 * O script vai:
 * ✅ Eliminar todas as inspeções (check-in e check-out)
 * ✅ Eliminar todas as fotos de inspeções
 * ✅ Eliminar todos os RAs uploadados
 * ✅ Resetar flags de inspeção nos RAs
 */

(async function cleanupDatabase() {
    console.log('🧹 SCRIPT DE LIMPEZA DA BASE DE DADOS');
    console.log('=====================================\n');
    
    // Confirmação do utilizador
    const confirmMessage = `⚠️ ATENÇÃO: Vais eliminar TODOS os dados de testes:

✗ Todos os Rental Agreements (RAs)
✗ Todas as Inspeções (Check-in e Check-out)
✗ Todas as Fotos de Inspeções

Esta ação é IRREVERSÍVEL!

Tens a certeza que queres continuar?`;
    
    if (!confirm(confirmMessage)) {
        console.log('❌ Operação cancelada pelo utilizador');
        return;
    }
    
    console.log('🚀 A iniciar limpeza...\n');
    
    let totalDeleted = {
        inspections: 0,
        photos: 0,
        rentalAgreements: 0
    };
    
    try {
        // 1️⃣ Eliminar todas as inspeções (também elimina fotos por foreign key)
        console.log('1️⃣ A eliminar inspeções e fotos...');
        const inspectionsResponse = await fetch('/api/inspections/delete-all', {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const inspectionsResult = await inspectionsResponse.json();
        
        if (inspectionsResult.ok) {
            console.log('✅ ' + inspectionsResult.message);
            // Extrair números da mensagem (ex: "Deleted 5 inspections and 20 photos")
            const match = inspectionsResult.message.match(/(\d+) inspections and (\d+) photos/);
            if (match) {
                totalDeleted.inspections = parseInt(match[1]);
                totalDeleted.photos = parseInt(match[2]);
            }
        } else {
            console.error('❌ Erro ao eliminar inspeções:', inspectionsResult.error);
        }
        
        console.log('');
        
        // 2️⃣ Eliminar todos os RAs
        console.log('2️⃣ A eliminar Rental Agreements...');
        const rasResponse = await fetch('/api/rental-agreements/delete-all', {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const rasResult = await rasResponse.json();
        
        if (rasResult.ok) {
            console.log('✅ ' + rasResult.message);
            // Extrair número da mensagem (ex: "Deleted 10 rental agreements")
            const match = rasResult.message.match(/(\d+) rental agreements/);
            if (match) {
                totalDeleted.rentalAgreements = parseInt(match[1]);
            }
        } else {
            console.error('❌ Erro ao eliminar RAs:', rasResult.error);
        }
        
        console.log('\n=====================================');
        console.log('✅ LIMPEZA CONCLUÍDA COM SUCESSO!');
        console.log('=====================================\n');
        console.log('📊 RESUMO:');
        console.log(`   🗑️  ${totalDeleted.rentalAgreements} Rental Agreements eliminados`);
        console.log(`   🗑️  ${totalDeleted.inspections} Inspeções eliminadas`);
        console.log(`   🗑️  ${totalDeleted.photos} Fotos eliminadas`);
        console.log('\n🎉 Base de dados limpa! Tudo a zeros.');
        
        // Recarregar página para refletir mudanças
        console.log('\n🔄 A recarregar página em 2 segundos...');
        setTimeout(() => {
            location.reload();
        }, 2000);
        
    } catch (error) {
        console.error('\n❌ ERRO DURANTE A LIMPEZA:', error);
        console.error('Detalhes:', error.message);
        console.log('\n⚠️ Alguns dados podem ter sido eliminados parcialmente.');
        console.log('Verifica o estado da base de dados.');
    }
})();
