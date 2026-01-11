// Função corrigida para deletePeriod com persistência na base de dados
async function deletePeriod() {
    if (allPeriods.length <= 1) {
        alert('Não é possível eliminar o último período!');
        return;
    }
    
    const periodToDelete = allPeriods[currentPeriodIndex];
    const location = document.getElementById('locationSelect').value;
    const month = parseInt(document.getElementById('monthSelect').value);
    const year = parseInt(document.getElementById('yearSelect').value);
    const lastDayOfMonth = new Date(year, month, 0).getDate();
    
    if (!confirm(`Eliminar período ${periodToDelete.day_start}-${periodToDelete.day_end}?`)) {
        return;
    }
    
    console.log(`Eliminando período ${periodToDelete.day_start}-${periodToDelete.day_end}`);
    
    // Remover período do array local
    allPeriods.splice(currentPeriodIndex, 1);
    
    // Expandir períodos adjacentes para preencher o espaço
    allPeriods.forEach(period => {
        if (period.day_end === periodToDelete.day_start - 1) {
            const nextPeriod = allPeriods.find(p => p.day_start === periodToDelete.day_end + 1);
            if (nextPeriod) {
                period.day_end = nextPeriod.day_start - 1;
            } else {
                period.day_end = lastDayOfMonth;
            }
            console.log(`Expandindo período para ${period.day_start}-${period.day_end}`);
        }
        if (period.day_start === periodToDelete.day_end + 1) {
            const prevPeriod = allPeriods.find(p => p.day_end === periodToDelete.day_start - 1);
            if (prevPeriod) {
                period.day_start = prevPeriod.day_end + 1;
            } else {
                period.day_start = 1;
            }
            console.log(`Expandindo período para ${period.day_start}-${period.day_end}`);
        }
    });
    
    // Se não há períodos, criar um período completo vazio
    if (allPeriods.length === 0) {
        allPeriods.push({
            prices: {},
            updated_at: new Date().toISOString(),
            day_start: 1,
            day_end: lastDayOfMonth
        });
    }
    
    // Ordenar períodos
    allPeriods.sort((a, b) => a.day_start - b.day_start);
    
    console.log('Períodos após eliminação:', allPeriods.map(p => `${p.day_start}-${p.day_end}`));
    
    // PERSISTIR NA BASE DE DADOS
    try {
        // Eliminar todos os períodos deste mês
        const deleteResponse = await fetch('/api/current-prices/delete-month', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ location, month, year })
        });
        
        const deleteResult = await deleteResponse.json();
        if (deleteResult.ok) {
            console.log('Períodos antigos eliminados da base de dados');
        }
        
        // Guardar todos os períodos restantes
        for (const period of allPeriods) {
            if (Object.keys(period.prices).length > 0) {
                console.log(`Guardando período ${period.day_start}-${period.day_end}`);
                
                const response = await fetch('/api/current-prices/save', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        location,
                        month,
                        year,
                        prices: period.prices,
                        day_start: period.day_start,
                        day_end: period.day_end
                    })
                });
                
                const result = await response.json();
                if (!result.ok) {
                    console.error(`Erro ao guardar período ${period.day_start}-${period.day_end}:`, result.error);
                }
            }
        }
        
        console.log('Eliminação persistida na base de dados com sucesso');
        
        // Atualizar UI
        currentPeriodIndex = Math.max(0, currentPeriodIndex - 1);
        updatePeriodSelector();
        loadPeriodByIndex(currentPeriodIndex);
        
    } catch (error) {
        console.error('Erro ao persistir eliminação:', error);
        alert('Erro ao eliminar período: ' + error.message);
    }
}
