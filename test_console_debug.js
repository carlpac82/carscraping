// Código para testar no console do Safari - Debug Booking Creation
// Execute isto no console (F12 → Console) quando estiver no Passo 5 da criação de reserva

// 1. Verificar estado do bookingConfirmationData
console.log("=== Estado do bookingConfirmationData ===");
console.log("bookingConfirmationData:", bookingConfirmationData);

// 2. Verificar valores dos campos do formulário
console.log("\n=== Valores dos campos do formulário ===");
console.log("clientEmail:", document.getElementById('clientEmail')?.value);
console.log("clientPhone:", document.getElementById('clientPhone')?.value);
console.log("pickupDate:", document.getElementById('pickupDate')?.value);
console.log("dropoffDate:", document.getElementById('dropoffDate')?.value);
console.log("pickupTime:", document.getElementById('pickupTime')?.value);
console.log("dropoffTime:", document.getElementById('dropoffTime')?.value);
console.log("pickupLocation:", document.getElementById('pickupLocation')?.value);
console.log("dropoffLocation:", document.getElementById('dropoffLocation')?.value);
console.log("valueAdjustment:", document.getElementById('valueAdjustment')?.value);
console.log("depositAmount:", document.getElementById('depositAmount')?.value);

// 3. Verificar estado dos botões (selecionados)
console.log("\n=== Estado dos botões Sim/Não ===");
const valueYes = document.querySelector('.confirmation-btn-yes.selected');
const valueNo = document.querySelector('.confirmation-btn-no.selected');
const depositButtons = document.querySelectorAll('.confirmation-btn-yes');
console.log("Valor - Sim selecionado:", !!valueYes);
console.log("Valor - Não selecionado:", !!valueNo);
console.log("Depósito - Botões disponíveis:", depositButtons.length);

// 4. Testar chamada à API manualmente
console.log("\n=== Teste manual da API ===");
const testData = {
    vehicle_group: "B",
    client_name: "Teste Cliente",
    client_email: "teste@teste.pt",
    client_phone: "912345678",
    pickup_date: "2026-04-02",
    pickup_time: "12:00",
    dropoff_date: "2026-04-05",
    dropoff_time: "12:00",
    pickup_location: "Faro Aeroporto",
    dropoff_location: "Faro Aeroporto",
    insurance_type: "premium",
    total_amount: 100.00
};

fetch('/api/commissioners/bookings', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(testData)
})
.then(r => r.json())
.then(data => console.log("Resposta teste:", data))
.catch(e => console.error("Erro teste:", e));
