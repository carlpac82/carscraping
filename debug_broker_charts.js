// DEBUG CODE - Colar no console do Safari
console.log('=== DEBUG BROKER CHARTS ===');

// 1. Verificar se Chart.js está carregado
console.log('Chart.js disponível:', typeof Chart !== 'undefined');

// 2. Verificar se as funções existem
console.log('Funções disponíveis:');
console.log('- loadBrokerMonthlyComparison:', typeof loadBrokerMonthlyComparison);
console.log('- loadBrokerYearlyDistribution:', typeof loadBrokerYearlyDistribution);
console.log('- loadBrokerTopByValue:', typeof loadBrokerTopByValue);
console.log('- populateBrokerChartSelectors:', typeof populateBrokerChartSelectors);

// 3. Verificar se os elementos existem
console.log('Elementos DOM:');
console.log('- brokerMonthlyChart canvas:', document.getElementById('brokerMonthlyChart'));
console.log('- brokerYearlyChart canvas:', document.getElementById('brokerYearlyChart'));
console.log('- brokerTopChart canvas:', document.getElementById('brokerTopChart'));
console.log('- brokerMonthSelect:', document.getElementById('brokerMonthSelect'));
console.log('- brokerYearSelect:', document.getElementById('brokerYearSelect'));
console.log('- brokerTopYearSelect:', document.getElementById('brokerTopYearSelect'));

// 4. Verificar valores dos seletores
console.log('Valores dos seletores:');
console.log('- brokerMonthSelect value:', document.getElementById('brokerMonthSelect')?.value);
console.log('- brokerYearSelect value:', document.getElementById('brokerYearSelect')?.value);
console.log('- brokerTopYearSelect value:', document.getElementById('brokerTopYearSelect')?.value);

// 5. Testar endpoints manualmente
async function testEndpoints() {
    console.log('\n=== TESTAR ENDPOINTS ===');
    
    try {
        // Testar monthly comparison
        const monthValue = document.getElementById('brokerMonthSelect')?.value;
        if (monthValue) {
            console.log('Testando monthly comparison com mês:', monthValue);
            const monthlyResponse = await fetch(`/api/admin/brokers/monthly-comparison?month=${monthValue}`);
            const monthlyData = await monthlyResponse.json();
            console.log('Monthly comparison response:', monthlyData);
        }
        
        // Testar yearly distribution
        const yearValue = document.getElementById('brokerYearSelect')?.value;
        if (yearValue) {
            console.log('Testando yearly distribution com ano:', yearValue);
            const yearlyResponse = await fetch(`/api/admin/brokers/yearly-distribution?year=${yearValue}`);
            const yearlyData = await yearlyResponse.json();
            console.log('Yearly distribution response:', yearlyData);
        }
        
        // Testar top by value
        const topYearValue = document.getElementById('brokerTopYearSelect')?.value;
        if (topYearValue) {
            console.log('Testando top by value com ano:', topYearValue);
            const topResponse = await fetch(`/api/admin/brokers/top-by-value?year=${topYearValue}`);
            const topData = await topResponse.json();
            console.log('Top by value response:', topData);
        }
        
    } catch (error) {
        console.error('Erro ao testar endpoints:', error);
    }
}

// 6. Testar criação de gráficos manualmente
async function testChartsManually() {
    console.log('\n=== TESTAR GRÁFICOS MANUALMENTE ===');
    
    try {
        // Testar populate selectors
        if (typeof populateBrokerChartSelectors === 'function') {
            console.log('Executando populateBrokerChartSelectors...');
            populateBrokerChartSelectors();
            console.log('populateBrokerChartSelectors executado');
        }
        
        // Testar cada gráfico
        if (typeof loadBrokerMonthlyComparison === 'function') {
            console.log('Executando loadBrokerMonthlyComparison...');
            await loadBrokerMonthlyComparison();
            console.log('loadBrokerMonthlyComparison executado');
        }
        
        if (typeof loadBrokerYearlyDistribution === 'function') {
            console.log('Executando loadBrokerYearlyDistribution...');
            await loadBrokerYearlyDistribution();
            console.log('loadBrokerYearlyDistribution executado');
        }
        
        if (typeof loadBrokerTopByValue === 'function') {
            console.log('Executando loadBrokerTopByValue...');
            await loadBrokerTopByValue();
            console.log('loadBrokerTopByValue executado');
        }
        
    } catch (error) {
        console.error('Erro ao testar gráficos:', error);
    }
}

// 7. Verificar estado dos gráficos
function checkChartInstances() {
    console.log('\n=== VERIFICAR INSTÂNCIAS DOS GRÁFICOS ===');
    console.log('brokerMonthlyChart:', window.brokerMonthlyChart);
    console.log('brokerYearlyChart:', window.brokerYearlyChart);
    console.log('brokerTopChart:', window.brokerTopChart);
}

// Executar testes
console.log('\nA executar testes...');
testEndpoints().then(() => {
    testChartsManually().then(() => {
        checkChartInstances();
        console.log('\n=== DEBUG CONCLUÍDO ===');
    });
});

// Função para resetar gráficos (se necessário)
window.resetBrokerCharts = function() {
    if (window.brokerMonthlyChart) window.brokerMonthlyChart.destroy();
    if (window.brokerYearlyChart) window.brokerYearlyChart.destroy();
    if (window.brokerTopChart) window.brokerTopChart.destroy();
    window.brokerMonthlyChart = null;
    window.brokerYearlyChart = null;
    window.brokerTopChart = null;
    console.log('Gráficos resetados');
};

console.log('\nComandos disponíveis:');
console.log('- testEndpoints() para testar endpoints');
console.log('- testChartsManually() para testar gráficos');
console.log('- checkChartInstances() para verificar instâncias');
console.log('- resetBrokerCharts() para resetar gráficos');
