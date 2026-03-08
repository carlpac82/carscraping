// TESTE: Colar isto na consola da homepage para ver o localStorage

console.log('=== TESTE LOCALSTORAGE ===');
const savedVansPricing = localStorage.getItem('vansPricing');
console.log('localStorage.getItem("vansPricing"):', savedVansPricing);

if (savedVansPricing) {
    const parsed = JSON.parse(savedVansPricing);
    console.log('Valores guardados:', parsed);
} else {
    console.log('❌ localStorage VAZIO - usando valores default');
    console.log('Valores default:', {
        c3_1day: 112, c3_2days: 144, c3_3days: 180,
        c4_1day: 152, c4_2days: 170, c4_3days: 210,
        c5_1day: 175, c5_2days: 190, c5_3days: 240
    });
}

console.log('=== FIM TESTE ===');
