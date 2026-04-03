// Debug detalhado para o problema do gráfico em branco
// Copiar e colar no console

console.log('🔍 Debug detalhado do gráfico em branco...');

// 1. Verificar dados atuais
async function debugChartData() {
    try {
        const yearSelect = document.getElementById('brokerYearSelect');
        const selectedYear = yearSelect?.value || '2026';
        
        console.log('📅 Ano selecionado:', selectedYear);
        
        // Buscar dados da API
        const response = await fetch(`/api/admin/brokers/yearly-distribution?year=${selectedYear}`);
        const data = await response.json();
        
        console.log('📡 Resposta completa da API:', data);
        
        if (!data.ok) {
            console.error('❌ Erro na API:', data.error);
            return;
        }
        
        const brokers = data.data.brokers;
        console.log('📊 Dados dos brokers:');
        
        brokers.forEach((broker, index) => {
            console.log(`[${index}] ${broker.broker_name}:`);
            console.log(`  - Reservations: ${broker.reservation_count}`);
            console.log(`  - Total Value: ${broker.total_value}`);
            console.log(`  - Value é zero?: ${broker.total_value === 0}`);
            console.log(`  - Value é null?: ${broker.total_value === null}`);
            console.log(`  - Value é undefined?: ${broker.total_value === undefined}`);
            console.log(`  - Type of value: ${typeof broker.total_value}`);
        });
        
        // Verificar somas
        const totalReservations = brokers.reduce((sum, b) => sum + (b.reservation_count || 0), 0);
        const totalValue = brokers.reduce((sum, b) => sum + (b.total_value || 0), 0);
        
        console.log('\n💰 Totais:');
        console.log('- Total Reservations:', totalReservations);
        console.log('- Total Value:', totalValue);
        console.log('- Total Value é zero?:', totalValue === 0);
        
        // Testar criação manual do gráfico com valores
        console.log('\n🧪 Testando criação manual com valores...');
        
        const canvas = document.getElementById('brokerYearlyChart');
        if (!canvas) {
            console.error('❌ Canvas não encontrado');
            return;
        }
        
        // Destruir gráfico anterior se existir
        if (window.brokerYearlyChart && typeof window.brokerYearlyChart.destroy === 'function') {
            window.brokerYearlyChart.destroy();
        }
        
        // Preparar dados para modo valores
        const labels = brokers.map(b => b.broker_name);
        const values = brokers.map(b => b.total_value || 0);
        const colors = ['#009cb6', '#ff9800', '#4caf50', '#f44336', '#9c27b0', '#795548', '#607d8b', '#e91e63', '#ff5722', '#3f51b5'];
        
        console.log('📈 Dados para o gráfico de valores:');
        console.log('- Labels:', labels);
        console.log('- Values:', values);
        console.log('- Values array length:', values.length);
        console.log('- All values are zero?:', values.every(v => v === 0));
        
        // Criar gráfico de teste
        window.brokerYearlyChart = new Chart(canvas, {
            type: 'pie',
            data: {
                labels: labels,
                datasets: [{
                    data: values,
                    backgroundColor: colors.slice(0, labels.length),
                    borderColor: '#ffffff',
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right',
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.parsed;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = total > 0 ? ((value / total) * 100).toFixed(1) : '0.0';
                                return `${label}: €${value.toFixed(2)} (${percentage}%)`;
                            }
                        }
                    }
                }
            }
        });
        
        console.log('✅ Gráfico de teste criado');
        
        // Verificar se o gráfico foi realmente criado
        setTimeout(() => {
            const chartInstance = window.brokerYearlyChart;
            if (chartInstance) {
                console.log('📊 Chart instance exists:', true);
                console.log('📊 Chart type:', chartInstance.config.type);
                console.log('📊 Chart data:', chartInstance.data);
                console.log('📊 Canvas visible:', canvas.offsetWidth > 0 && canvas.offsetHeight > 0);
            } else {
                console.error('❌ Chart instance is null after creation');
            }
        }, 1000);
        
    } catch (error) {
        console.error('❌ Erro no debug:', error);
    }
}

// 2. Função para testar com dados mock
function testWithMockData() {
    console.log('\n🎭 Testando com dados mock...');
    
    const canvas = document.getElementById('brokerYearlyChart');
    if (!canvas) {
        console.error('❌ Canvas não encontrado');
        return;
    }
    
    // Destruir gráfico anterior
    if (window.brokerYearlyChart && typeof window.brokerYearlyChart.destroy === 'function') {
        window.brokerYearlyChart.destroy();
    }
    
    // Dados mock com valores conhecidos
    const mockLabels = ['Broker A', 'Broker B', 'Broker C'];
    const mockValues = [1000, 2000, 1500];
    const colors = ['#009cb6', '#ff9800', '#4caf50'];
    
    console.log('📊 Dados mock:');
    console.log('- Labels:', mockLabels);
    console.log('- Values:', mockValues);
    
    window.brokerYearlyChart = new Chart(canvas, {
        type: 'pie',
        data: {
            labels: mockLabels,
            datasets: [{
                data: mockValues,
                backgroundColor: colors,
                borderColor: '#ffffff',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.parsed;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((value / total) * 100).toFixed(1);
                            return `${label}: €${value.toFixed(2)} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
    
    console.log('✅ Gráfico mock criado - deve visível agora');
}

// Adicionar funções ao escopo global
window.debugChartData = debugChartData;
window.testWithMockData = testWithMockData;

console.log('\n🚀 Funções disponíveis:');
console.log('- debugChartData() - Analisa dados reais da API');
console.log('- testWithMockData() - Testa com dados mock');
console.log('\n🔥 Execute debugChartData() primeiro para ver o problema');
