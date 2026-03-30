// COPIAR E COLAR NO CONSOLE DO SAFARI
function checkAPIData(){
    console.log('🔍 API DATA CHECK');
    console.log('commissionerPricing completo:', window.commissionerPricing);
    console.log('Tem extras?', window.commissionerPricing?.extras);
    console.log('Tem insurance?', window.commissionerPricing?.extras?.insurance);
    console.log('Tem seasons?', window.commissionerPricing?.extras?.insurance?.seasons);
    
    // Verificar estrutura completa
    const data = window.commissionerPricing;
    if(data){
        console.log('Estrutura completa:');
        console.log('- seasons:', data.seasons);
        console.log('- extras:', data.extras);
        console.log('- insurance:', data.extras?.insurance);
        console.log('- insurance seasons:', data.extras?.insurance?.seasons);
        
        // Verificar para veículo B
        if(data.extras?.insurance?.seasons?.B){
            console.log('Preços seguro para B:', data.extras.insurance.seasons.B);
            console.log('Preços para B em mid:', data.extras.insurance.seasons.B.mid);
        } else {
            console.log('❌ Sem preços de seguro para veículo B');
        }
    } else {
        console.log('❌ commissionerPricing não está definido');
    }
}
checkAPIData();
