// COPIAR E COLAR DIRETAMENTE NO CONSOLE DO SAFARI
function checkSeguro(){
    const pickup=document.getElementById('pickupDate').value;
    const dropoff=document.getElementById('dropoffDate').value;
    const vehicle=document.getElementById('selectedVehicleGroup').value;
    console.log('🔍 SEGURO CHECK');
    console.log('Datas:',pickup,'→',dropoff);
    console.log('Veículo:',vehicle);
    
    if(!pickup||!dropoff||!vehicle){console.log('❌ Preencha tudo!');return;}
    
    const pickupDate=new Date(pickup);
    const dropoffDate=new Date(dropoff);
    const days=Math.ceil(Math.abs(dropoffDate-pickupDate)/(1000*60*60*24));
    console.log('Dias:',days);
    
    function getSeason(d){
        const y=d.getFullYear(),m=d.getMonth()+1,day=d.getDate();
        if(y===2026){
            if((m===1||m===2)||(m===3&&day<=25))return'low';
            if((m===3&&day>=26)||m===4||m===5||m===6||(m===7&&day<=14))return'mid';
            if((m===7&&day>=15)||m===8||m===9||(m===10&&day<=15))return'high';
        }
        return'mid';
    }
    
    const season=getSeason(pickupDate);
    console.log('Época:',season);
    
    console.log('Dados seguro:',window.commissionerPricing?.extras?.insurance);
    
    let seguro=0;
    const data=window.commissionerPricing;
    if(data?.extras?.insurance?.seasons?.[vehicle]?.[season]){
        const prices=data.extras.insurance.seasons[vehicle][season];
        let range=null;
        if(days<=2)range='1_2';
        else if(days<=7)range='3_7';
        else if(days<=14)range='8_14';
        else if(days<=21)range='15_21';
        
        if(range&&prices[range]){
            seguro=prices[range];
            console.log('💰 Seguro calculado:',seguro+'€');
        }
    }
    
    const precoUI=document.getElementById('summaryTotalPrice')?.textContent;
    console.log('Preço na UI:',precoUI);
    console.log('Ícone seguro:',document.querySelector('.insurance-icon')?'✅':'❌');
    console.log('✅ Fim!');
}
checkSeguro();
