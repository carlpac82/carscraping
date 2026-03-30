// COPIAR E COLAR ESTE CÓDIGO NO CONSOLE DO BROWSER

function verificarSeguro() {
    console.log('🔍 VERIFICANDO SEGURO');
    console.log('========================');
    
    // Obter dados atuais
    const pickupDate = document.getElementById('pickupDate').value;
    const dropoffDate = document.getElementById('dropoffDate').value;
    const selectedVehicle = document.getElementById('selectedVehicleGroup').value;
    
    console.log('📅 Data Entrega:', pickupDate);
    console.log('📅 Data Devolução:', dropoffDate);
    console.log('🚗 Veículo:', selectedVehicle);
    
    if (!pickupDate || !dropoffDate || !selectedVehicle) {
        console.log('❌ Preencha datas e selecione veículo primeiro!');
        return;
    }
    
    // Calcular dias
    const pickup = new Date(pickupDate);
    const dropoff = new Date(dropoffDate);
    const diffTime = Math.abs(dropoff - pickup);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    console.log('⏰ Dias:', diffDays);
    
    // Época
    function getSeasonForDate(date) {
        const year = date.getFullYear();
        const month = date.getMonth() + 1;
        const day = date.getDate();
        
        if (year === 2026) {
            if ((month === 1 || month === 2) || (month === 3 && day <= 25)) return 'low';
            if (month === 11 && day >= 16) return 'low';
            if (month === 12) return 'low';
            if ((month === 3 && day >= 26) || month === 4 || month === 5 || month === 6 || (month === 7 && day <= 14)) return 'mid';
            if ((month === 7 && day >= 15) || month === 8 || month === 9 || (month === 10 && day <= 15)) return 'high';
        }
        return 'mid';
    }
    
    const season = getSeasonForDate(pickup);
    console.log('🌤️ Época:', season);
    
    // Verificar dados do seguro
    console.log('🛡️ DADOS DO SEGURO:');
    console.log('  commissionerPricing:', commissionerPricing);
    
    if (commissionerPricing && commissionerPricing.extras && commissionerPricing.extras.insurance) {
        console.log('  ✅ Dados de seguro encontrados');
        console.log('  Seasons:', commissionerPricing.extras.insurance.seasons);
        
        if (commissionerPricing.extras.insurance.seasons[selectedVehicle]) {
            console.log('  ✅ Preços para veículo', selectedVehicle);
            console.log('  Preços na época', season + ':', commissionerPricing.extras.insurance.seasons[selectedVehicle][season]);
        } else {
            console.log('  ❌ Sem preços para veículo', selectedVehicle);
        }
    } else {
        console.log('  ❌ Dados de seguro NÃO encontrados');
    }
    
    // Verificar valor atual mostrado
    const priceElement = document.getElementById('summaryTotalPrice');
    if (priceElement) {
        console.log('💰 Preço atual mostrado:', priceElement.textContent);
    } else {
        console.log('❌ Elemento de preço não encontrado');
    }
    
    // Verificar ícone do seguro
    const insuranceIcon = document.querySelector('.insurance-icon');
    if (insuranceIcon) {
        console.log('🛡️ Ícone do seguro encontrado:', insuranceIcon);
    } else {
        console.log('❌ Ícone do seguro NÃO encontrado');
    }
    
    // Recalcular preço manualmente
    let insurancePrice = 0;
    
    if (selectedVehicle && commissionerPricing && commissionerPricing.extras && 
        commissionerPricing.extras.insurance && commissionerPricing.extras.insurance.seasons &&
        commissionerPricing.extras.insurance.seasons[selectedVehicle] &&
        commissionerPricing.extras.insurance.seasons[selectedVehicle][season]) {
        
        const seasonPrices = commissionerPricing.extras.insurance.seasons[selectedVehicle][season];
        
        let priceRange = null;
        if (diffDays >= 1 && diffDays <= 2) priceRange = "1_2";
        else if (diffDays >= 3 && diffDays <= 7) priceRange = "3_7";
        else if (diffDays >= 8 && diffDays <= 14) priceRange = "8_14";
        else if (diffDays >= 15 && diffDays <= 21) priceRange = "15_21";
        
        if (priceRange && seasonPrices[priceRange]) {
            insurancePrice = seasonPrices[priceRange];
            console.log('💰 Preço do seguro calculado:', insurancePrice + '€ (faixa:', priceRange + ')');
        } else {
            console.log('❌ Faixa de preço não encontrada:', priceRange);
        }
    } else {
        console.log('❌ Não foi possível calcular preço do seguro');
    }
    
    console.log('========================');
    console.log('✅ Verificação concluída!');
    console.log('📋 Resumo:');
    console.log('  - Seguro calculado:', insurancePrice + '€');
    console.log('  - Preço na UI:', priceElement ? priceElement.textContent : 'N/A');
}

// Executar função
verificarSeguro();
