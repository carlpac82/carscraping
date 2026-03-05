// CÓDIGO PARA TESTAR NA CONSOLA DA HOMEPAGE
// Copiar e colar na consola do browser (F12) quando estiveres na homepage

console.log('🧪 Testing vans pricing in homepage...');

// 1. Verificar se os cards C3, C4, C5 existem
const cards = document.querySelectorAll('.price-card');
const grupos = [];
cards.forEach(card => {
    const h3 = card.querySelector('h3');
    if (h3) {
        const grupo = h3.textContent.replace('Grupo ', '').trim();
        grupos.push(grupo);
    }
});

console.log('📋 Grupos encontrados nos cards:', grupos);
console.log('📋 C3 existe?', grupos.includes('C3'));
console.log('📋 C4 existe?', grupos.includes('C4'));
console.log('📋 C5 existe?', grupos.includes('C5'));

// 2. Verificar se pricesByGroup tem C3, C4, C5
if (typeof pricesByGroup !== 'undefined') {
    console.log('📊 pricesByGroup keys:', Object.keys(pricesByGroup));
    console.log('📊 C3 in pricesByGroup?', 'C3' in pricesByGroup);
    console.log('📊 C4 in pricesByGroup?', 'C4' in pricesByGroup);
    console.log('📊 C5 in pricesByGroup?', 'C5' in pricesByGroup);
    
    if ('C3' in pricesByGroup) {
        console.log('📊 C3 prices:', pricesByGroup.C3);
    }
    if ('C4' in pricesByGroup) {
        console.log('📊 C4 prices:', pricesByGroup.C4);
    }
    if ('C5' in pricesByGroup) {
        console.log('📊 C5 prices:', pricesByGroup.C5);
    }
} else {
    console.log('❌ pricesByGroup não está definido');
}

// 3. Testar collectPriceData para ver o que vai para o CSV
if (typeof collectPriceData === 'function') {
    console.log('🧪 Testing collectPriceData...');
    const brokersData = collectPriceData('brokers');
    console.log('📋 Brokers CSV data:', brokersData);
    
    // Verificar se C3, C4, C5 estão no header
    const header = brokersData[0];
    console.log('📋 CSV Header:', header);
    console.log('📋 C3 in header?', header.includes('C3'));
    console.log('📋 C4 in header?', header.includes('C4'));
    console.log('📋 C5 in header?', header.includes('C5'));
    
    // Verificar índices de C3, C4, C5 no header
    const c3_idx = header.indexOf('C3');
    const c4_idx = header.indexOf('C4');
    const c5_idx = header.indexOf('C5');
    
    console.log('📋 C3 index:', c3_idx);
    console.log('📋 C4 index:', c4_idx);
    console.log('📋 C5 index:', c5_idx);
    
    // Verificar valores na primeira linha de dados (1 dia)
    if (brokersData.length > 1) {
        const firstDataRow = brokersData[1];
        console.log('📋 First data row (1 day):', firstDataRow);
        if (c3_idx >= 0) console.log('📋 C3 value for 1 day:', firstDataRow[c3_idx]);
        if (c4_idx >= 0) console.log('📋 C4 value for 1 day:', firstDataRow[c4_idx]);
        if (c5_idx >= 0) console.log('📋 C5 value for 1 day:', firstDataRow[c5_idx]);
    }
} else {
    console.log('❌ collectPriceData não está definido');
}

console.log('✅ Teste completo!');
