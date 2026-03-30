// Função para verificar preços discriminados no console
// Copiar e colar esta função no console do browser

function debugPrecos() {
    console.log('🔍 ANÁLISE DETALHADA DE PREÇOS');
    console.log('================================');
    
    // Obter dados do formulário
    const pickupDate = document.getElementById('pickupDate').value;
    const dropoffDate = document.getElementById('dropoffDate').value;
    const pickupTime = document.getElementById('pickupTime').value;
    const dropoffTime = document.getElementById('dropoffTime').value;
    const selectedVehicle = document.getElementById('selectedVehicleGroup').value;
    
    console.log('📅 DATAS:');
    console.log('  Data Entrega:', pickupDate, pickupTime);
    console.log('  Data Devolução:', dropoffDate, dropoffTime);
    
    if (!pickupDate || !dropoffDate) {
        console.log('❌ Preencha as datas primeiro!');
        return;
    }
    
    // Calcular dias
    const pickup = new Date(pickupDate + ' ' + pickupTime);
    const dropoff = new Date(dropoffDate + ' ' + dropoffTime);
    const diffTime = Math.abs(dropoff - pickup);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    console.log('⏰ CÁLCULO DE DIAS:');
    console.log('  Diferença em ms:', diffTime);
    console.log('  Dias calculados:', diffDays);
    
    // Época
    function getSeasonForDate(date) {
        const year = date.getFullYear();
        const month = date.getMonth() + 1;
        const day = date.getDate();
        
        if (year === 2026) {
            if ((month === 1 || month === 2) || (month === 3 && day <= 25)) {
                return 'low';
            }
            if (month === 11 && day >= 16) {
                return 'low';
            }
            if (month === 12) {
                return 'low';
            }
            if ((month === 3 && day >= 26) || month === 4 || month === 5 || month === 6 || (month === 7 && day <= 14)) {
                return 'mid';
            }
            if ((month === 7 && day >= 15) || month === 8 || month === 9 || (month === 10 && day <= 15)) {
                return 'high';
            }
        } else if (year === 2027) {
            if (month === 1 || month === 2 || (month === 3 && day <= 25)) {
                return 'low';
            }
            if ((month === 3 && day >= 26) || month === 4 || month === 5 || month === 6 || (month === 7 && day <= 14)) {
                return 'mid';
            }
        }
        
        return 'mid';
    }
    
    const season = getSeasonForDate(pickup);
    console.log('🌤️ ÉPOCA:', season);
    
    // Veículo selecionado
    console.log('🚗 VEÍCULO:');
    console.log('  Código:', selectedVehicle);
    
    if (!selectedVehicle) {
        console.log('❌ Selecione um veículo primeiro!');
        return;
    }
    
    // Dados do veículo
    const vehicleData = vehicleGroups.find(v => v.code === selectedVehicle);
    if (vehicleData) {
        console.log('  Nome:', vehicleData.name);
        console.log('  Preço base diário:', vehicleData.price + '€');
    }
    
    // Preços do comissionista
    console.log('💰 PREÇOS DO COMISSIONISTA:');
    console.log('  Dados:', commissionerPricing);
    
    if (commissionerPricing && commissionerPricing.seasons && commissionerPricing.seasons[selectedVehicle]) {
        const seasonPrices = commissionerPricing.seasons[selectedVehicle][season];
        console.log('  Preços para', selectedVehicle, 'na época', season + ':', seasonPrices);
        
        // Calcular preço base
        let basePrice = 0;
        if (diffDays <= 7) {
            const dayKey = `day${diffDays}`;
            basePrice = seasonPrices[dayKey] || 0;
            console.log('  Preço base (' + dayKey + '):', basePrice + '€');
        } else {
            // Para mais de 7 dias
            if (seasonPrices.day7) {
                basePrice = seasonPrices.day7;
                for (let i = 8; i <= diffDays; i++) {
                    const extraDayPrice = seasonPrices[`day${i}`] || seasonPrices.day8 || seasonPrices.day7;
                    basePrice += extraDayPrice;
                }
            }
            console.log('  Preço base (calculado):', basePrice + '€');
        }
    }
    
    // Seguro
    console.log('🛡️ SEGURO:');
    let insurancePrice = 0;
    
    if (selectedVehicle && commissionerPricing && commissionerPricing.extras && 
        commissionerPricing.extras.insurance && commissionerPricing.extras.insurance.seasons &&
        commissionerPricing.extras.insurance.seasons[selectedVehicle] &&
        commissionerPricing.extras.insurance.seasons[selectedVehicle][season]) {
        
        const seasonPrices = commissionerPricing.extras.insurance.seasons[selectedVehicle][season];
        
        let priceRange = null;
        if (diffDays >= 1 && diffDays <= 2) {
            priceRange = "1_2";
        } else if (diffDays >= 3 && diffDays <= 7) {
            priceRange = "3_7";
        } else if (diffDays >= 8 && diffDays <= 14) {
            priceRange = "8_14";
        } else if (diffDays >= 15 && diffDays <= 21) {
            priceRange = "15_21";
        }
        
        if (priceRange && seasonPrices[priceRange]) {
            insurancePrice = seasonPrices[priceRange];
            console.log('  Faixa de dias:', priceRange);
            console.log('  Preço seguro:', insurancePrice + '€');
        }
    }
    
    // Extras
    console.log('🎁 EXTRAS:');
    let extrasTotal = 0;
    
    // GPS
    const gpsCheckbox = document.getElementById('extraGPS');
    if (gpsCheckbox && gpsCheckbox.checked) {
        const gpsPrice = 5 * diffDays;
        extrasTotal += gpsPrice;
        console.log('  GPS: 5€ ×', diffDays, 'dias =', gpsPrice + '€');
    }
    
    // Cadeira de Criança
    const childSeatInput = document.getElementById('extraChildSeat');
    if (childSeatInput && childSeatInput.value > 0) {
        const childSeatPrice = 5 * diffDays * parseInt(childSeatInput.value);
        extrasTotal += childSeatPrice;
        console.log('  Cadeira Criança: 5€ ×', diffDays, 'dias ×', childSeatInput.value, 'unid =', childSeatPrice + '€');
    }
    
    // Booster Seat
    const boosterSeatInput = document.getElementById('extraBoosterSeat');
    if (boosterSeatInput && boosterSeatInput.value > 0) {
        const boosterSeatPrice = 3 * diffDays * parseInt(boosterSeatInput.value);
        extrasTotal += boosterSeatPrice;
        console.log('  Booster Seat: 3€ ×', diffDays, 'dias ×', boosterSeatInput.value, 'unid =', boosterSeatPrice + '€');
    }
    
    // Condutor Adicional
    const additionalDriverInput = document.getElementById('extraAdditionalDriver');
    if (additionalDriverInput && additionalDriverInput.value > 0) {
        const additionalDriverPrice = 5 * diffDays * parseInt(additionalDriverInput.value);
        extrasTotal += additionalDriverPrice;
        console.log('  Condutor Adicional: 5€ ×', diffDays, 'dias ×', additionalDriverInput.value, 'unid =', additionalDriverPrice + '€');
    }
    
    // Young Driver
    const youngDriverCheckbox = document.getElementById('extraYoungDriver');
    if (youngDriverCheckbox && youngDriverCheckbox.checked) {
        const youngDriverPrice = 10 * diffDays;
        extrasTotal += youngDriverPrice;
        console.log('  Young Driver: 10€ ×', diffDays, 'dias =', youngDriverPrice + '€');
    }
    
    // Senior Driver
    const seniorDriverCheckbox = document.getElementById('extraSeniorDriver');
    if (seniorDriverCheckbox && seniorDriverCheckbox.checked) {
        const seniorDriverPrice = 8 * diffDays;
        extrasTotal += seniorDriverPrice;
        console.log('  Senior Driver: 8€ ×', diffDays, 'dias =', seniorDriverPrice + '€');
    }
    
    // Road Tax
    const roadTaxCheckbox = document.getElementById('extraRoadTax');
    if (roadTaxCheckbox && roadTaxCheckbox.checked) {
        const roadTaxDays = Math.min(diffDays, 10);
        const roadTaxPrice = 2.23 * roadTaxDays;
        extrasTotal += roadTaxPrice;
        console.log('  Road Tax: 2.23€ ×', roadTaxDays, 'dias (máx 10) =', roadTaxPrice.toFixed(2) + '€');
    }
    
    // Taxa Aeroporto
    const airportCheckbox = document.getElementById('extraAirport');
    if (airportCheckbox && airportCheckbox.checked) {
        const airportPrice = 20;
        extrasTotal += airportPrice;
        console.log('  Taxa Aeroporto: 20€ (taxa única)');
    }
    
    console.log('  Total Extras:', extrasTotal.toFixed(2) + '€');
    
    // RESUMO FINAL
    console.log('📊 RESUMO FINAL:');
    console.log('================================');
    
    // Calcular preço base (se tiver dados)
    let basePrice = 0;
    if (commissionerPricing && commissionerPricing.seasons && commissionerPricing.seasons[selectedVehicle]) {
        const seasonPrices = commissionerPricing.seasons[selectedVehicle][season];
        if (diffDays <= 7) {
            const dayKey = `day${diffDays}`;
            basePrice = seasonPrices[dayKey] || 0;
        }
    }
    
    const totalPrice = basePrice + insurancePrice + extrasTotal;
    
    console.log('  Preço Base:', basePrice.toFixed(2) + '€');
    console.log('  Seguro:', insurancePrice.toFixed(2) + '€');
    console.log('  Extras:', extrasTotal.toFixed(2) + '€');
    console.log('  ──────────────────────────');
    console.log('  TOTAL:', totalPrice.toFixed(2) + '€');
    
    // Comparar com o valor mostrado na UI
    const uiPrice = document.getElementById('summaryTotalPrice');
    if (uiPrice) {
        console.log('  Valor na UI:', uiPrice.textContent);
        console.log('  Diferença:', (totalPrice - parseFloat(uiPrice.textContent.replace('€', '').replace(',', '.'))).toFixed(2) + '€');
    }
    
    console.log('================================');
    console.log('✅ Análise concluída!');
}

// Executar a função
debugPrecos();
