// Código para debug do toggle do gráfico anual de brokers
// Copiar e colar este código no console do navegador (F12)

console.log('🔍 Iniciando debug do toggle do gráfico anual...');

// 1. Verificar se elementos existem
const toggleBtn = document.getElementById('brokerYearlyToggle');
const toggleIcon = document.getElementById('brokerYearlyToggleIcon');
const yearSelect = document.getElementById('brokerYearSelect');
const canvas = document.getElementById('brokerYearlyChart');

console.log('📋 Elementos encontrados:');
console.log('- Botão toggle:', toggleBtn ? '✅' : '❌');
console.log('- Ícone toggle:', toggleIcon ? '✅' : '❌');
console.log('- Select ano:', yearSelect ? '✅' : '❌');
console.log('- Canvas:', canvas ? '✅' : '❌');

// 2. Verificar estado atual
console.log('\n📊 Estado atual:');
console.log('- Ano selecionado:', yearSelect?.value);
console.log('- brokerYearlyShowValues:', typeof window.brokerYearlyShowValues !== 'undefined' ? window.brokerYearlyShowValues : '❌ Variável não definida');
console.log('- brokerYearlyChart:', typeof window.brokerYearlyChart !== 'undefined' ? (window.brokerYearlyChart ? '✅ Instância existe' : '❌ Null') : '❌ Variável não definida');

// 3. Testar toggle manualmente
async function testToggle() {
    console.log('\n🔄 Testando toggle manualmente...');
    
    try {
        // Alternar estado
        if (typeof window.brokerYearlyShowValues === 'undefined') {
            window.brokerYearlyShowValues = false;
        }
        window.brokerYearlyShowValues = !window.brokerYearlyShowValues;
        
        console.log('🔢 Novo estado showValues:', window.brokerYearlyShowValues);
        
        // Atualizar ícone
        if (toggleIcon) {
            if (window.brokerYearlyShowValues) {
                toggleIcon.textContent = '📊';
                toggleIcon.style.color = '#ff9800';
            } else {
                toggleIcon.textContent = '🔢';
                toggleIcon.style.color = '#009cb6';
            }
            console.log('🎨 Ícone atualizado:', toggleIcon.textContent, toggleIcon.style.color);
        }
        
        // Carregar dados
        const selectedYear = yearSelect?.value || '2025';
        console.log('📅 Carregando dados para o ano:', selectedYear);
        
        const response = await fetch(`/api/admin/brokers/yearly-distribution?year=${selectedYear}`);
        const data = await response.json();
        
        console.log('📡 Resposta da API:', data);
        
        if (!data.ok) {
            console.error('❌ Erro na API:', data.error);
            return;
        }
        
        // Destruir gráfico anterior
        if (window.brokerYearlyChart) {
            window.brokerYearlyChart.destroy();
            console.log('🗑️ Gráfico anterior destruído');
        }
        
        // Preparar dados
        const labels = data.data.brokers.map(b => b.broker_name);
        const counts = data.data.brokers.map(b => b.reservation_count);
        const values = data.data.brokers.map(b => b.total_value);
        const chartData = window.brokerYearlyShowValues ? values : counts;
        const dataType = window.brokerYearlyShowValues ? 'valor' : 'reservas';
        
        console.log('📊 Dados processados:');
        console.log('- Labels:', labels);
        console.log('- Counts:', counts);
        console.log('- Values:', values);
        console.log('- Tipo de dados:', dataType);
        console.log('- Dados do gráfico:', chartData);
        
        // Verificar se há dados válidos
        if (!labels.length || labels.every(l => !l)) {
            console.error('❌ Não há dados válidos para exibir');
            return;
        }
        
        // Criar gráfico
        const colors = ['#009cb6', '#ff9800', '#4caf50', '#f44336', '#9c27b0', '#795548', '#607d8b', '#e91e63', '#ff5722', '#3f51b5'];
        
        window.brokerYearlyChart = new Chart(canvas, {
            type: 'pie',
            data: {
                labels: labels,
                datasets: [{
                    data: chartData,
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
                                const percentage = ((value / total) * 100).toFixed(1);
                                let formattedValue;
                                if (window.brokerYearlyShowValues) {
                                    formattedValue = '€' + value.toFixed(2);
                                } else {
                                    formattedValue = value.toString();
                                }
                                return `${label}: ${formattedValue} ${dataType} (${percentage}%)`;
                            }
                        }
                    }
                }
            }
        });
        
        console.log('✅ Gráfico criado com sucesso!');
        
    } catch (error) {
        console.error('❌ Erro no teste:', error);
    }
}

// 4. Adicionar função ao escopo global para fácil acesso
window.testToggle = testToggle;

console.log('\n🚀 Para testar, digite: testToggle()');
console.log('💡 Ou clique no botão toggle normalmente e observe os logs');

// 5. Testar automaticamente após 2 segundos
setTimeout(() => {
    console.log('\n⏰ Executando teste automático...');
    testToggle();
}, 2000);
