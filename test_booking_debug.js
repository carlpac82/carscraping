// ========================================
// 🔍 DEBUG SCRIPT - Booking Creation
// ========================================
// Copia e cola no Console do Safari
// ========================================

console.log('🔍 ===== BOOKING DEBUG SCRIPT =====');

// 1. Verificar bookingConfirmationData
console.log('\n📦 bookingConfirmationData:', bookingConfirmationData);

// 2. Verificar dados do formulário
const formData = {
    // Cliente
    client_name: document.getElementById('clientName')?.value,
    client_email: document.getElementById('clientEmail')?.value,
    client_phone: document.getElementById('clientPhone')?.value,
    
    // Hotel
    hotel: document.getElementById('hotel')?.value,
    room_number: document.getElementById('roomNumber')?.value,
    
    // Datas e Horas
    pickup_date: document.getElementById('pickupDate')?.value,
    pickup_time: document.getElementById('pickupTime')?.value,
    dropoff_date: document.getElementById('dropoffDate')?.value,
    dropoff_time: document.getElementById('dropoffTime')?.value,
    
    // Locais
    pickup_location: document.getElementById('pickupLocation')?.value,
    dropoff_location: document.getElementById('dropoffLocation')?.value,
    
    // Voo
    flight_number: document.getElementById('flightNumber')?.value,
    
    // Seguro
    insurance_type: document.querySelector('input[name="insuranceType"]:checked')?.value,
    
    // Veículo
    vehicle_group: selectedVehicle,
    
    // Extras
    extraGPS: document.getElementById('extraGPS')?.checked,
    extraAirport: document.getElementById('extraAirport')?.checked,
    extraChildSeat: parseInt(document.getElementById('extraChildSeat')?.value) || 0,
    extraBoosterSeat: parseInt(document.getElementById('extraBoosterSeat')?.value) || 0,
    extraAdditionalDriver: parseInt(document.getElementById('extraAdditionalDriver')?.value) || 0,
    extraYoungDriver: document.getElementById('extraYoungDriver')?.checked,
    extraSeniorDriver: document.getElementById('extraSeniorDriver')?.checked,
    extraTripToSpain: document.getElementById('extraTripToSpain')?.checked,
};

console.log('\n📝 Dados do Formulário:', formData);

// 3. Verificar campos vazios
console.log('\n⚠️ Campos VAZIOS ou NULL:');
Object.entries(formData).forEach(([key, value]) => {
    if (!value || value === '' || value === null) {
        console.log(`   ❌ ${key}: "${value}"`);
    }
});

// 4. Verificar botões de confirmação
const valueYesBtn = document.querySelectorAll('.confirmation-btn-yes')[0];
const valueNoBtn = document.querySelectorAll('.confirmation-btn-no')[0];
const depositYesBtn = document.querySelectorAll('.confirmation-btn-yes')[1];
const depositNoBtn = document.querySelectorAll('.confirmation-btn-no')[1];

console.log('\n🔘 Estado dos Botões:');
console.log('   Valor Sim:', valueYesBtn?.classList.contains('selected'));
console.log('   Valor Não:', valueNoBtn?.classList.contains('selected'));
console.log('   Depósito Sim:', depositYesBtn?.classList.contains('selected'));
console.log('   Depósito Não:', depositNoBtn?.classList.contains('selected'));

// 5. Verificar campos de ajuste
const valueAdjustmentInput = document.getElementById('valueAdjustment');
const depositInput = document.getElementById('depositAmount');

console.log('\n💰 Campos de Ajuste:');
console.log('   Valor Ajustado:', valueAdjustmentInput?.value);
console.log('   Valor Depósito:', depositInput?.value);

// 6. Calcular preços
console.log('\n💶 Cálculo de Preços:');
try {
    const totalAmount = calculateTotalAmount();
    console.log('   Total Calculado:', totalAmount);
} catch (e) {
    console.error('   ❌ Erro ao calcular total:', e.message);
}

// 7. Simular dados que seriam enviados
console.log('\n📤 Dados que SERIAM enviados ao backend:');
const simulatedBookingData = {
    vehicle_group: selectedVehicle,
    client_name: document.getElementById('clientName')?.value,
    client_email: document.getElementById('clientEmail')?.value,
    client_phone: document.getElementById('clientPhone')?.value,
    hotel: document.getElementById('hotel')?.value || null,
    room_number: document.getElementById('roomNumber')?.value || null,
    pickup_date: document.getElementById('pickupDate')?.value,
    pickup_time: document.getElementById('pickupTime')?.value,
    dropoff_date: document.getElementById('dropoffDate')?.value,
    dropoff_time: document.getElementById('dropoffTime')?.value,
    pickup_location: document.getElementById('pickupLocation')?.value,
    dropoff_location: document.getElementById('dropoffLocation')?.value,
    flight_number: document.getElementById('flightNumber')?.value || null,
    insurance_type: document.querySelector('input[name="insuranceType"]:checked')?.value,
    total_amount: bookingConfirmationData?.totalAmount || 0,
};

console.log(JSON.stringify(simulatedBookingData, null, 2));

// 8. Verificar campos OBRIGATÓRIOS do backend
const requiredFields = [
    "vehicle_group", "client_name", "client_email", "client_phone",
    "pickup_date", "pickup_time", "dropoff_date", "dropoff_time",
    "pickup_location", "dropoff_location", "insurance_type", "total_amount"
];

console.log('\n✅ Validação de Campos OBRIGATÓRIOS:');
requiredFields.forEach(field => {
    const value = simulatedBookingData[field];
    const isValid = value && value !== '' && value !== null && value !== 0;
    console.log(`   ${isValid ? '✅' : '❌'} ${field}: "${value}"`);
});

console.log('\n🔍 ===== FIM DO DEBUG =====');
