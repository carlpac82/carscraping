// Código para colar no console do Safari - Debug de Seguros e Franquias
// Copie e cole este código inteiro no console do Safari

console.log('=== DEBUG DE SEGUROS E FRANQUIAS ===');

// 1. Verificar dados do veículo selecionado
console.log('1. DADOS DO VEÍCULO SELECIONADO:');
console.log('selectedVehicle:', window.selectedVehicle);
console.log('selectedVehicleData:', window.selectedVehicleData);

if (window.selectedVehicleData) {
    console.log('Grupo do veículo:', window.selectedVehicleData.group);
    console.log('Nome do veículo:', window.selectedVehicleData.name);
    console.log('Código do veículo:', window.selectedVehicleData.code);
} else {
    console.log('❌ Nenhum veículo selecionado');
}

// 2. Verificar franquias disponíveis
console.log('\n2. FRANQUIAS POR GRUPO:');
console.log('franchisesByGroup:', window.franchisesByGroup);

// 3. Verificar preços do comissionista
console.log('\n3. PREÇOS DO COMISSIONISTA:');
console.log('commissionerPricing:', window.commissionerPricing);

if (window.commissionerPricing && window.commissionerPricing.extras && window.commissionerPricing.extras.insurance) {
    console.log('Dados de seguro disponíveis:', window.commissionerPricing.extras.insurance);
    
    if (window.commissionerPricing.extras.insurance.seasons) {
        console.log('Preços por época:', window.commissionerPricing.extras.insurance.seasons);
    }
} else {
    console.log('❌ Dados de preços não encontrados');
}

// 4. Verificar elementos HTML
console.log('\n4. ELEMENTOS HTML:');
const baseFranchisePrice = document.getElementById('baseFranchisePrice');
const premiumInsurancePrice = document.getElementById('premiumInsurancePrice');
const modalFranchise = document.getElementById('modalFranchise');

console.log('baseFranchisePrice element:', baseFranchisePrice);
console.log('premiumInsurancePrice element:', premiumInsurancePrice);
console.log('modalFranchise element:', modalFranchise);

if (baseFranchisePrice) {
    console.log('Texto atual da franquia base:', baseFranchisePrice.textContent);
}
if (premiumInsurancePrice) {
    console.log('Texto atual do preço premium:', premiumInsurancePrice.textContent);
}
if (modalFranchise) {
    console.log('Texto atual da franquia no modal:', modalFranchise.textContent);
}

// 5. Verificar data de pickup
console.log('\n5. DATA DE PICKUP:');
const pickupInput = document.getElementById('pickupDate');
if (pickupInput && pickupInput.value) {
    console.log('Data de pickup:', pickupInput.value);
    
    // Verificar época
    const pickup = new Date(pickupInput.value);
    const month = pickup.getMonth() + 1; // 0-11 para 1-12
    let season = '';
    
    if (month >= 4 && month <= 6) {
        season = 'alta';
    } else if (month >= 7 && month <= 9) {
        season = 'media';
    } else {
        season = 'baixa';
    }
    
    console.log('Mês:', month);
    console.log('Época calculada:', season);
} else {
    console.log('❌ Data de pickup não definida');
}

// 6. Função para testar atualização manual
console.log('\n6. FUNÇÃO DE TESTE MANUAL:');
window.testarFranquias = function() {
    console.log('=== TESTE MANUAL DE ATUALIZAÇÃO ===');
    
    // Testar updateBaseFranchiseText
    if (typeof window.updateBaseFranchiseText === 'function') {
        console.log('Executando updateBaseFranchiseText()...');
        window.updateBaseFranchiseText();
        console.log('✅ updateBaseFranchiseText executado');
    } else {
        console.log('❌ updateBaseFranchiseText não encontrada');
    }
    
    // Testar updatePremiumInsurancePrice
    if (typeof window.updatePremiumInsurancePrice === 'function') {
        console.log('Executando updatePremiumInsurancePrice()...');
        window.updatePremiumInsurancePrice();
        console.log('✅ updatePremiumInsurancePrice executado');
    } else {
        console.log('❌ updatePremiumInsurancePrice não encontrada');
    }
    
    // Verificar resultados
    setTimeout(() => {
        console.log('Resultados após atualização:');
        if (baseFranchisePrice) {
            console.log('Franquia base:', baseFranchisePrice.textContent);
        }
        if (premiumInsurancePrice) {
            console.log('Preço premium:', premiumInsurancePrice.textContent);
        }
        if (modalFranchise) {
            console.log('Franquia modal:', modalFranchise.textContent);
        }
    }, 100);
};

// 7. Função para simular seleção de veículo
console.log('\n7. FUNÇÃO PARA SIMULAR SELEÇÃO:');
window.simularSelecao = function(groupCode) {
    console.log(`=== SIMULANDO SELEÇÃO DO GRUPO ${groupCode} ===`);
    
    // Encontrar veículo pelo grupo
    const vehicle = window.vehicleGroups ? window.vehicleGroups.find(v => v.code === groupCode) : null;
    
    if (vehicle) {
        console.log('Veículo encontrado:', vehicle);
        
        // Simular seleção
        window.selectedVehicle = groupCode;
        window.selectedVehicleData = vehicle;
        
        // Atualizar textos
        window.testarFranquias();
        
        console.log('✅ Simulação concluída');
    } else {
        console.log(`❌ Veículo do grupo ${groupCode} não encontrado`);
    }
};

console.log('\n=== COMANDOS DISPONÍVEIS ===');
console.log('testarFranquias() - Testa atualização das franquias');
console.log('simularSelecao("A") - Simula seleção do grupo A');
console.log('simularSelecao("E1") - Simula seleção do grupo E1');
console.log('simularSelecao("F") - Simula seleção do grupo F');

console.log('\n=== DEBUG CONCLUÍDO ===');
