/**
 * Vehicle Inspection System - Complete JavaScript
 * Real-time camera capture + AI damage detection
 */

// Global state
let currentStep = 1;
let inspectionData = {
    photos: {},
    aiResults: {},
    vehicleInfo: {}
};

// Make inspectionData globally accessible
window.inspectionData = inspectionData;

// Function to save photo data
function savePhotoData(photoType, dataURL, blob = null) {
    console.log(`📸 Saving photo: ${photoType}`);
    
    // Save to local inspectionData
    inspectionData.photos[photoType] = {
        dataURL: dataURL,
        blob: blob,
        timestamp: new Date().toISOString(),
        type: photoType
    };
    
    // Update global window reference
    window.inspectionData = inspectionData;
    
    // Also save to localStorage as backup
    try {
        const photosForStorage = {};
        Object.keys(inspectionData.photos).forEach(key => {
            photosForStorage[key] = {
                dataURL: inspectionData.photos[key].dataURL,
                timestamp: inspectionData.photos[key].timestamp,
                type: inspectionData.photos[key].type
            };
        });
        localStorage.setItem('inspectionPhotos', JSON.stringify(photosForStorage));
        console.log(`💾 Photo saved to localStorage: ${photoType}`);
    } catch(e) {
        console.warn('Failed to save to localStorage:', e);
    }
    
    console.log(`✅ Photo saved successfully: ${photoType}. Total photos: ${Object.keys(inspectionData.photos).length}`);
}

// Function to load photos from localStorage on page load
function loadPhotosFromStorage() {
    try {
        const storedPhotos = localStorage.getItem('inspectionPhotos');
        if (storedPhotos) {
            const photos = JSON.parse(storedPhotos);
            Object.keys(photos).forEach(key => {
                inspectionData.photos[key] = photos[key];
            });
            window.inspectionData = inspectionData;
            console.log(`📂 Loaded ${Object.keys(photos).length} photos from localStorage`);
        }
    } catch(e) {
        console.warn('Failed to load photos from localStorage:', e);
    }
}

// Load photos when script loads
loadPhotosFromStorage();

// Debug function to check photo status
function debugPhotoStatus() {
    console.log('📊 Photo Status Debug:');
    console.log('- inspectionData.photos:', inspectionData.photos);
    console.log('- window.inspectionData.photos:', window.inspectionData?.photos);
    console.log('- localStorage photos:', localStorage.getItem('inspectionPhotos'));
    console.log('- Total photos in memory:', Object.keys(inspectionData.photos).length);
    
    // Also check if there are any photo elements in the DOM
    const photoSlots = document.querySelectorAll('.photo-slot, [id*="photo"], [class*="photo"]');
    console.log('- Photo elements in DOM:', photoSlots.length);
    
    return {
        memoryPhotos: Object.keys(inspectionData.photos).length,
        windowPhotos: Object.keys(window.inspectionData?.photos || {}).length,
        domElements: photoSlots.length
    };
}

// Make debug function globally available
window.debugPhotoStatus = debugPhotoStatus;

let cameraStream = null;
let currentPhotoType = null;
let autoSequenceMode = false;
let currentPhotoIndex = 0;

// Notification helper
function showNotification(message, type = 'info') {
    console.log(`[${type.toUpperCase()}] ${message}`);
    
    // Only show visual notifications for errors and warnings
    if (type !== 'error' && type !== 'warning') {
        return;
    }
    
    // Create toast notification
    const toast = document.createElement('div');
    toast.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : '#009cb6'};
        color: white;
        padding: 16px 24px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        z-index: 10001;
        font-weight: 500;
        max-width: 300px;
        animation: slideIn 0.3s ease-out;
    `;
    toast.textContent = message;
    
    document.body.appendChild(toast);
    
    // Remove after 3 seconds
    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => {
            if (toast.parentNode) {
                document.body.removeChild(toast);
            }
        }, 300);
    }, 3000);
}

// Photo types and instructions - 9 photos total
// Each photo has a specific image from the Inspecção folder
const photoTypes = [
    {type: 'front', label: 'Vista Frontal', instruction: 'Centre a frente do veículo, inclua a matrícula', position: 1, image: 'Vista Frontal.png'},
    {type: 'front_left', label: 'Vista Frontal Lateral Esquerda', instruction: 'Mostre a frente e o lado esquerdo do veículo', position: 2, image: 'Vista Frontal Esquerda.png'},
    {type: 'front_right', label: 'Vista Frontal Lateral Direita', instruction: 'Mostre a frente e o lado direito do veículo', position: 3, image: 'Vista Frontal Direita.png'},
    {type: 'right', label: 'Vista Lateral Direita', instruction: 'Mostre todo o lado direito, inclua todas as portas e rodas', position: 4, image: 'Vista Lateral Direita.png'},
    {type: 'back_right', label: 'Vista Traseira Lateral Direita', instruction: 'Mostre a traseira e o lado direito do veículo', position: 5, image: 'Vista Traseira direita.png'},
    {type: 'back', label: 'Vista Traseira', instruction: 'Centre a traseira do veículo, inclua a matrícula', position: 6, image: 'Vista Traseira.png'},
    {type: 'back_left', label: 'Vista Traseira Lateral Esquerda', instruction: 'Mostre a traseira e o lado esquerdo do veículo', position: 7, image: 'Vista Traseira Esquerda.png'},
    {type: 'left', label: 'Vista Lateral Esquerda', instruction: 'Mostre todo o lado esquerdo, inclua todas as portas e rodas', position: 8, image: 'Vista Lateral Esquerda.png'},
    {type: 'odometer', label: 'Odómetro / Painel de Instrumentos', instruction: 'Foto clara do conta-quilómetros/display da quilometragem', position: 9, image: 'Odometro.png'}
];

// Update pickup button state based on delivery status
function updatePickupButtonState() {
    const pickupButton = document.getElementById('pickupButton');
    const pickupIcon = document.getElementById('pickupIcon');
    const pickupAnimation = document.getElementById('pickupAnimation');
    const pickupText = document.getElementById('pickupText');
    
    if (!pickupButton) return;
    
    // Check if there's a completed delivery
    // Priority 1: Check window.inspectionCompleted (from RA database)
    // Priority 2: Check localStorage contracts
    const plate = document.getElementById('inputPlate')?.value.trim();
    const ra = document.getElementById('inputRA')?.value.trim();
    
    let hasCompletedDelivery = false;
    
    // Check if inspection was completed (from database)
    if (window.inspectionCompleted === true) {
        hasCompletedDelivery = true;
        console.log('✅ Check-in enabled: inspection_completed from database');
    } 
    // Fallback: Check localStorage contracts
    else if (plate && ra) {
        const contractKey = `${plate}_${ra}`;
        const contracts = getActiveContracts();
        
        // Check if this specific contract has completed delivery
        if (contracts[contractKey] && contracts[contractKey].deliveryComplete) {
            hasCompletedDelivery = true;
            console.log('✅ Check-in enabled: deliveryComplete from localStorage');
        }
    }
    
    if (!hasCompletedDelivery) {
        // Disable button
        pickupButton.disabled = true;
        pickupButton.classList.add('opacity-50', 'cursor-not-allowed');
        
        // Change icon to gray
        if (pickupIcon) {
            pickupIcon.setAttribute('fill', '#6c757d'); // gray color
        }
        
        // Hide animation
        if (pickupAnimation) {
            pickupAnimation.classList.add('hidden');
        }
        
        // Change text color to gray
        if (pickupText) {
            pickupText.classList.remove('group-hover:text-green-500');
            pickupText.classList.add('text-gray-400');
        }
        
        console.log('❌ Check-in disabled: no completed delivery found');
    } else {
        // Enable button
        pickupButton.disabled = false;
        pickupButton.classList.remove('opacity-50', 'cursor-not-allowed');
        
        // Change icon to GREEN
        if (pickupIcon) {
            pickupIcon.setAttribute('fill', '#28a745'); // Green color
        }
        
        // Show animation
        if (pickupAnimation) {
            pickupAnimation.classList.remove('hidden');
        }
        
        // Restore text color
        if (pickupText) {
            pickupText.classList.add('group-hover:text-green-500');
            pickupText.classList.remove('text-gray-400');
        }
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    // Update pickup button state
    updatePickupButtonState();
    
    // Add listeners to update pickup button when plate or RA changes
    const plateInput = document.getElementById('inputPlate');
    const raInput = document.getElementById('inputRA');
    
    if (plateInput) {
        plateInput.addEventListener('input', function() {
            setTimeout(updatePickupButtonState, 1000); // Delay to allow RA auto-fill
        });
    }
    
    if (raInput) {
        raInput.addEventListener('input', updatePickupButtonState);
    }
    // Auto-fill Rececionista from logged-in user
    let userName = 'Rececionista'; // fallback
    
    // Get user name from backend data
    if (window.currentUserData && window.currentUserData.name) {
        userName = window.currentUserData.name;
        console.log('✅ User name from backend:', userName);
    } else if (localStorage.getItem('userName')) {
        userName = localStorage.getItem('userName');
        console.log('✅ User name from localStorage:', userName);
    } else {
        console.log('⚠️ No user data found, using fallback:', userName);
    }
    
    const receptionistField = document.getElementById('inputReceptionist');
    if (receptionistField) {
        // Only override if current value is default
        if (!receptionistField.value || receptionistField.value === 'Admin' || receptionistField.value === 'Rececionista') {
            receptionistField.value = userName;
        }
        console.log('✅ Rececionista preenchido automaticamente:', receptionistField.value);
    }
    
    // Set user initials in avatar
    const userInitials = document.getElementById('userInitials');
    const userNameDisplay = document.getElementById('userNameDisplay');
    if (userInitials && userName) {
        const nameParts = userName.split(' ');
        const initials = nameParts.length > 1 
            ? nameParts[0][0] + nameParts[nameParts.length - 1][0]
            : userName.substring(0, 2);
        userInitials.textContent = initials.toUpperCase();
    }
    if (userNameDisplay) {
        userNameDisplay.textContent = userName;
    }
    
    // Auto-fill current Date
    const now = new Date();
    const dateStr = now.toLocaleDateString('pt-PT', { 
        year: 'numeric', 
        month: '2-digit', 
        day: '2-digit' 
    });
    const dateField = document.getElementById('inputDate');
    if (dateField) {
        dateField.value = dateStr;
    }
    
    // Auto-fill current Time
    const timeStr = now.toLocaleTimeString('pt-PT', { 
        hour: '2-digit', 
        minute: '2-digit'
    });
    const timeField = document.getElementById('inputTime');
    if (timeField) {
        timeField.value = timeStr;
    }
    
    // Auto-focus RA field when license plate is filled
    const plateField = document.getElementById('inputPlate');
    const raField = document.getElementById('inputRA');
    
    if (plateField && raField) {
        plateField.addEventListener('input', function() {
            // Count only alphanumeric characters (excluding dashes)
            const cleanValue = this.value.replace(/[^A-Za-z0-9]/g, '');
            
            // When plate reaches exactly 6 alphanumeric characters, focus RA field
            if (cleanValue.length === 6) {
                setTimeout(() => {
                    raField.focus();
                    console.log('✅ Auto-focused RA field after 6 alphanumeric characters in license plate');
                }, 100);
            }
        });
        
        plateField.addEventListener('keypress', function(e) {
            // On Enter key, focus RA field
            if (e.key === 'Enter') {
                e.preventDefault();
                raField.focus();
                console.log('✅ Focused RA field on Enter key');
            }
        });
    }
    
    // Auto-format license plate field: AA-03-AA (reuse existing plateField)
    if (plateField) {
        plateField.addEventListener('input', function(e) {
            let value = e.target.value.replace(/[^A-Za-z0-9]/g, '').toUpperCase(); // Only letters and numbers
            
            // Limit to 6 characters
            if (value.length > 6) {
                value = value.substring(0, 6);
            }
            
            // Auto-format with dashes: AA-03-AA (2-2-2 format)
            if (value.length >= 5) {
                value = value.substring(0, 2) + '-' + value.substring(2, 4) + '-' + value.substring(4);
            } else if (value.length >= 3) {
                value = value.substring(0, 2) + '-' + value.substring(2);
            }
            
            e.target.value = value;
        });
    }
    
    // Auto-format RA field: 5 digits + "-09" (reuse existing raField)
    if (raField) {
        raField.addEventListener('input', function(e) {
            let value = e.target.value.replace(/[^0-9-]/g, ''); // Only numbers and dash
            
            // Remove any existing dash
            value = value.replace(/-/g, '');
            
            // Limit to 5 digits
            if (value.length > 5) {
                value = value.substring(0, 5);
            }
            
            // Auto-add -09 after 5 digits
            if (value.length === 5) {
                value = value + '-09';
            }
            
            e.target.value = value;
        });
        
        // Also format on blur if user enters exactly 5 digits
        raField.addEventListener('blur', function(e) {
            let value = e.target.value.replace(/[^0-9-]/g, '');
            value = value.replace(/-/g, '');
            
            if (value.length === 5) {
                e.target.value = value + '-09';
            }
        });
    }
});

function initializePhotoGrid() {
    const grid = document.getElementById('photoGrid');
    grid.innerHTML = photoTypes.map((photo, index) => {
        // Number colors matching diagram
        let numberColor = '#10b981'; // green for 1-4
        if (photo.type === 'interior') numberColor = '#f59e0b'; // amber for 5
        if (photo.type === 'odometer') numberColor = '#8b5cf6'; // purple for 6
        
        return `
        <div class="photo-slot" id="slot-${photo.type}" onclick="openCamera('${photo.type}')">
            <div class="photo-slot-number" style="background: ${numberColor}; border-color: ${numberColor}; color: white;">
                ${index + 1}
            </div>
            <div class="absolute inset-0 flex flex-col items-center justify-center p-4 pt-12">
                <svg class="w-12 h-12 text-gray-400 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"/>
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z"/>
                </svg>
                <div class="text-center">
                    <div class="font-semibold text-gray-700 text-sm">${photo.label}</div>
                    <div class="text-xs text-gray-500 mt-1">Click to capture</div>
                </div>
            </div>
            <div class="absolute top-2 right-2 hidden" id="check-${photo.type}">
                <svg class="w-6 h-6 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
                </svg>
            </div>
        </div>
    `;
    }).join('');
}

function initializeDiagramInteraction() {
    // Make diagram indicators clickable
    const indicators = document.querySelectorAll('.photo-indicator');
    indicators.forEach(indicator => {
        indicator.addEventListener('click', function() {
            const photoType = this.getAttribute('data-type');
            openCamera(photoType);
        });
    });
}

function updateDiagramIndicator(photoType, captured) {
    // Diagram was removed, keeping function for compatibility
}

// Step navigation (4 steps: Photos -> Diagram -> Analysis -> Review)
function nextStep() {
    console.log('nextStep called, current step:', currentStep);
    
    if (currentStep === 1) {
        // Go to diagram after photos
        if (!validatePhotos()) return;
        currentStep = 2;
        updateStepDisplay();
        showDiagramStep();
    } else if (currentStep === 2) {
        // Go to analysis after diagram
        currentStep = 3;
        updateStepDisplay();
        startAIAnalysis();
    } else if (currentStep === 3) {
        // Go to review after analysis
        currentStep = 4;
        updateStepDisplay();
        generateReview();
    }
    
    console.log('nextStep finished, new step:', currentStep);
}

function showDiagramStep() {
    // Navigate to diagram from photos
    document.getElementById('stepPhotos').classList.add('hidden');
    document.getElementById('stepDiagram').classList.remove('hidden');
    window.scrollTo({ top: 0, behavior: 'smooth' });
    console.log('✅ Showing diagram step');
    
    // Initialize canvas after diagram is visible
    setTimeout(() => {
        console.log('🔵 Calling nextToDiagram to initialize canvas...');
        if (typeof nextToDiagram === 'function') {
            nextToDiagram(true); // Skip validation when called automatically
        } else {
            console.error('❌ nextToDiagram function not found');
        }
    }, 100);
}

function prevStep() {
    currentStep--;
    updateStepDisplay();
}

function updateStepDisplay() {
    // Hide all steps
    document.querySelectorAll('.step-content').forEach(el => el.classList.add('hidden'));
    
    // Show current step (now: stepPhotos, stepDiagram, stepAnalysis, stepReview)
    const steps = ['stepPhotos', 'stepDiagram', 'stepAnalysis', 'stepReview'];
    const currentStepElement = document.getElementById(steps[currentStep - 1]);
    if (currentStepElement) {
        currentStepElement.classList.remove('hidden');
    }
    
    // Update step indicators (3 steps only)
    const indicators = document.querySelectorAll('.step-indicator');
    indicators.forEach((indicator, index) => {
        const stepNum = index + 1;
        indicator.classList.remove('active', 'completed');
        if (stepNum < currentStep) {
            indicator.classList.add('completed'); // Blue
        } else if (stepNum === currentStep) {
            indicator.classList.add('active'); // Yellow
        }
    });
    
    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Validation
function validateInspectionInfo() {
    const plate = document.getElementById('inputPlate').value.trim();
    const ra = document.getElementById('inputRA').value.trim();
    
    if (!plate) {
        showNotification('Por favor insira a matrícula', 'error');
        document.getElementById('inputPlate').focus();
        return false;
    }
    
    if (!ra) {
        showNotification('Por favor insira o RA (Rental Agreement)', 'error');
        document.getElementById('inputRA').focus();
        return false;
    }
    
    return true;
}

function validatePhotos() {
    const capturedCount = Object.keys(inspectionData.photos).length;
    if (capturedCount < 9) {
        showNotification(`Por favor capture todas as 9 fotos (${capturedCount}/9 completas)`, 'warning');
        return false;
    }
    return true;
}

function saveVehicleInfo() {
    // Get diagram data if available (fuel level and odometer from diagram step)
    const diagramData = window.diagramData || {};
    
    inspectionData.vehicleInfo = {
        inspection_type: document.getElementById('inputInspectionType').value,
        vehicle_plate: document.getElementById('inputPlate').value.trim(),
        vehicle_brand: document.getElementById('inputBrand').value.trim(),
        vehicle_model: document.getElementById('inputModel').value.trim(),
        contract_number: document.getElementById('inputContract').value.trim(),
        customer_name: document.getElementById('inputCustomerName').value.trim(),
        customer_email: document.getElementById('inputCustomerEmail').value.trim(),
        customer_phone: document.getElementById('inputCustomerPhone').value.trim(),
        // Use diagram data if available, otherwise use form inputs
        odometer_reading: diagramData.odometerReading || document.getElementById('inputOdometer')?.value || '',
        fuel_level: diagramData.fuelLevel || document.getElementById('inputFuelLevel')?.value || '',
        inspector_name: document.getElementById('inputInspectorName').value.trim(),
        inspector_notes: document.getElementById('inputNotes').value.trim()
    };
    
    // Save inspector name
    localStorage.setItem('inspectorName', inspectionData.vehicleInfo.inspector_name);
    
    // Update header
    document.getElementById('inspectionType').textContent = 
        inspectionData.vehicleInfo.inspection_type === 'check_in' ? 'Check-in' : 'Check-out';
    
    console.log('Vehicle info saved:', inspectionData.vehicleInfo);
}

// Contract Management Functions
function getContractKey() {
    const plate = document.getElementById('inputPlate').value.trim();
    const ra = document.getElementById('inputRA').value.trim();
    return `${plate}_${ra}`;
}

function getActiveContracts() {
    const contracts = localStorage.getItem('activeContracts');
    return contracts ? JSON.parse(contracts) : {};
}

function saveActiveContracts(contracts) {
    localStorage.setItem('activeContracts', JSON.stringify(contracts));
}

function checkExistingContract() {
    const plate = document.getElementById('inputPlate').value.trim();
    const ra = document.getElementById('inputRA').value.trim();
    const contractKey = getContractKey();
    const contracts = getActiveContracts();
    
    // Check if there's an active contract for this vehicle with different RA
    for (const [key, contract] of Object.entries(contracts)) {
        const [contractPlate, contractRA] = key.split('_');
        
        // Same vehicle, different RA, and previous contract not completed (no pickup)
        if (contractPlate === plate && contractRA !== ra && !contract.pickupComplete) {
            return {
                exists: true,
                ra: contractRA,
                deliveryComplete: contract.deliveryComplete
            };
        }
    }
    
    return { exists: false };
}

// ENTREGA (Delivery/Check-out) - Start inspection process
function startDelivery() {
    // Validate inspection info first
    if (!validateInspectionInfo()) {
        return;
    }
    
    // Check if inspection was already completed for this RA
    if (window.inspectionCompleted) {
        const raNumber = document.getElementById('inputRA').value.trim();
        showMinimalistConfirm(
            `RA ${raNumber}`,
            'Inspeção realizada. Refazer inspeção?',
            (confirmed) => {
                if (confirmed) {
                    // User confirmed, proceed with delivery
                    proceedWithDelivery();
                } else {
                    // User cancelled, clear fields
                    document.getElementById('inputPlate').value = '';
                    document.getElementById('inputRA').value = '';
                    document.getElementById('reportEmail').value = '';
                    window.inspectionCompleted = false;
                }
            }
        );
        return;
    }
    
    // No previous inspection, proceed normally
    proceedWithDelivery();
}

// Helper function to proceed with delivery
function proceedWithDelivery() {
    // Check if there's an incomplete contract for this vehicle
    const existingContract = checkExistingContract();
    if (existingContract.exists) {
        showNotification(`❌ Existe um contrato ativo (RA: ${existingContract.ra}) para esta viatura que ainda não foi finalizado com check-in (recolha). Complete o check-in primeiro!`, 'error');
        return;
    }
    
    // Save contract as delivery started
    const contractKey = getContractKey();
    const contracts = getActiveContracts();
    contracts[contractKey] = {
        plate: document.getElementById('inputPlate').value.trim(),
        ra: document.getElementById('inputRA').value.trim(),
        deliveryComplete: false,
        pickupComplete: false,
        deliveryDate: new Date().toISOString()
    };
    saveActiveContracts(contracts);
    
    // Set process type to delivery
    localStorage.setItem('processType', 'delivery');
    localStorage.setItem('currentContractKey', contractKey);
    
    autoSequenceMode = true;
    currentPhotoIndex = 0;
    
    showNotification('Iniciando processo de ENTREGA! Siga as instruções', 'info');
    
    // Start with first photo
    setTimeout(() => {
        capturePhotoSequence(0);
    }, 1000);
}

// RECOLHA (Pickup/Check-in) - Load delivery data and update
function startPickup() {
    // Check if there's a completed delivery (either in localStorage or from backend)
    const hasLocalDelivery = localStorage.getItem('processType') === 'delivery' && localStorage.getItem('inspectionPhotos');
    const hasBackendDelivery = window.inspectionCompleted === true;
    
    if (!hasLocalDelivery && !hasBackendDelivery) {
        showNotification('❌ Não existe processo de ENTREGA! Faça a entrega primeiro.', 'error');
        return;
    }
    
    // Validate inspection info
    if (!validateInspectionInfo()) {
        return;
    }
    
    // Set process type to pickup
    localStorage.setItem('processType', 'pickup');
    
    // Go directly to croqui with delivery data
    showNotification('Carregando dados do check-out...', 'info');
    loadDeliveryDataAndShowCroqui();
}

// Show modal to update kms and fuel for pickup
function showPickupUpdateModal() {
    showNotification('Iniciando processo de RECOLHA! Carregando dados da entrega...', 'info');
    
    // Get delivery (check-out) fuel level from backend or current value
    let deliveryFuel = 100;
    if (window.currentRAData && window.currentRAData.fuel_level) {
        deliveryFuel = parseFloat(window.currentRAData.fuel_level);
    } else if (window.currentFuelLevel) {
        deliveryFuel = parseFloat(window.currentFuelLevel);
    }
    
    // Get delivery (check-out) km from backend
    let deliveryKm = '';
    if (window.currentRAData && window.currentRAData.odometer) {
        deliveryKm = window.currentRAData.odometer;
    }
    
    // Create modal HTML with clean design
    const modalHTML = `
        <div id="pickupUpdateModal" style="position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.85); z-index: 10000; display: flex; align-items: center; justify-content: center; backdrop-filter: blur(4px);">
            <div style="background: white; padding: 40px; border-radius: 12px; max-width: 600px; width: 90%; box-shadow: 0 10px 40px rgba(0,0,0,0.3);">
                <h2 style="color: #009cb6; font-size: 28px; font-weight: bold; margin-bottom: 10px; text-align: center;">
                    Iniciar Recolha de Viatura
                </h2>
                <p style="color: #666; margin-bottom: 30px; text-align: center; font-size: 14px;">
                    Insira os quilómetros e combustível finais da viatura
                </p>
                
                <!-- Quilómetros -->
                <div style="margin-bottom: 30px;">
                    <label style="display: block; color: #009cb6; font-weight: bold; font-size: 16px; margin-bottom: 12px;">
                        Km Entrada / Km In:
                    </label>
                    ${deliveryKm ? `<div style="background: #e3f2fd; padding: 10px; border-radius: 6px; margin-bottom: 10px; border-left: 4px solid #009cb6;">
                        <span style="font-size: 13px; color: #666;">Km Saída (Check-out): </span>
                        <span style="font-size: 14px; font-weight: bold; color: #009cb6;">${deliveryKm} km</span>
                    </div>` : ''}
                    <input type="number" id="pickupKm" value="${deliveryKm}" 
                           style="width: 100%; padding: 14px; border: 2px solid #009cb6; border-radius: 8px; font-size: 18px; font-weight: 600; color: #333;"
                           placeholder="Ex: 51500">
                </div>
                
                <!-- Combustível -->
                <div style="margin-bottom: 40px;">
                    <label style="display: block; color: #009cb6; font-weight: bold; font-size: 16px; margin-bottom: 12px;">
                        Combustível / Fuel:
                    </label>
                    <div style="background: #f8f9fa; border: 2px solid #009cb6; border-radius: 8px; padding: 20px;">
                        <div style="display: flex; align-items: center; justify-content: between; margin-bottom: 8px;">
                            <span style="font-size: 12px; font-weight: 600; color: #009cb6;">OUT</span>
                            <span style="font-size: 12px; font-weight: 600; color: #009cb6; margin-left: auto;">F</span>
                        </div>
                        
                        <!-- Fuel Level Bar -->
                        <div style="position: relative; background: white; border: 2px solid #009cb6; border-radius: 8px; height: 32px; margin-bottom: 12px;">
                            <div id="pickupFuelFill" style="height: 100%; background: #009cb6; border-radius: 6px; transition: width 0.3s; width: ${deliveryFuel}%;"></div>
                        </div>
                        
                        <!-- Fuel Level Slider -->
                        <input type="range" 
                               id="pickupFuelSlider" 
                               min="0" 
                               max="100" 
                               value="${deliveryFuel}" 
                               step="5"
                               style="width: 100%; height: 8px; border-radius: 5px; background: #ddd; outline: none; cursor: pointer;">
                        
                        <!-- Selected fuel level display -->
                        <div style="text-align: center; margin-top: 12px;">
                            <span style="font-size: 14px; font-weight: 600; color: #666;">Nível: </span>
                            <span id="pickupFuelText" style="font-size: 14px; font-weight: bold; color: #009cb6;"></span>
                        </div>
                    </div>
                </div>
                
                <div style="display: flex; gap: 12px;">
                    <button onclick="cancelPickupUpdate()" 
                            style="flex: 1; padding: 16px; background: #6c757d; color: white; border: none; border-radius: 8px; font-size: 16px; font-weight: bold; cursor: pointer; transition: background 0.2s;">
                        Cancelar
                    </button>
                    <button onclick="confirmPickupUpdate()" 
                            style="flex: 1; padding: 16px; background: #009cb6; color: white; border: none; border-radius: 8px; font-size: 16px; font-weight: bold; cursor: pointer; transition: background 0.2s;">
                        Iniciar Recolha
                    </button>
                </div>
            </div>
        </div>
    `;
    
    // Add modal to page
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    
    // Setup fuel slider
    const slider = document.getElementById('pickupFuelSlider');
    const fill = document.getElementById('pickupFuelFill');
    const text = document.getElementById('pickupFuelText');
    
    function updatePickupFuelDisplay(value) {
        const percentage = parseInt(value);
        fill.style.width = percentage + '%';
        
        // Simplified fractions like in check-out
        let levelText = '';
        if (percentage === 0) levelText = 'Vazio (E)';
        else if (percentage <= 12) levelText = '1/8';
        else if (percentage <= 25) levelText = '1/4';
        else if (percentage <= 37) levelText = '3/8';
        else if (percentage <= 50) levelText = '1/2';
        else if (percentage <= 62) levelText = '5/8';
        else if (percentage <= 75) levelText = '3/4';
        else if (percentage <= 87) levelText = '7/8';
        else if (percentage < 100) levelText = 'Quase Cheio';
        else levelText = 'Cheio (F)';
        
        text.textContent = `${percentage}% - ${levelText}`;
    }
    
    slider.addEventListener('input', (e) => {
        updatePickupFuelDisplay(e.target.value);
    });
    
    // Initialize display
    updatePickupFuelDisplay(deliveryFuel);
    
    // Focus on km input
    setTimeout(() => {
        document.getElementById('pickupKm')?.focus();
    }, 100);
}

// Cancel pickup update
function cancelPickupUpdate() {
    const modal = document.getElementById('pickupUpdateModal');
    if (modal) {
        modal.remove();
    }
    showNotification('Recolha cancelada', 'info');
}

// Confirm pickup update and load delivery data
function confirmPickupUpdate() {
    const km = document.getElementById('pickupKm')?.value;
    const fuel = document.getElementById('pickupFuelSlider')?.value;
    
    if (!km || km <= 0) {
        alert('Por favor, insira os quilómetros finais');
        document.getElementById('pickupKm')?.focus();
        return;
    }
    
    // Update form fields
    document.getElementById('odometerReading').value = km;
    
    // Update fuel slider on main form
    const mainFuelSlider = document.getElementById('fuelSlider');
    if (mainFuelSlider) {
        mainFuelSlider.value = fuel;
        // Trigger change event to update display
        mainFuelSlider.dispatchEvent(new Event('input'));
    }
    
    // Store fuel level
    window.currentFuelLevel = parseInt(fuel);
    
    // Close modal
    const modal = document.getElementById('pickupUpdateModal');
    if (modal) {
        modal.remove();
    }
    
    // Load delivery (check-out) data and show croqui with damages
    showNotification('Carregando dados do check-out...', 'info');
    loadDeliveryDataAndShowCroqui();
}

// Load delivery (check-out) data and show croqui with damages
async function loadDeliveryDataAndShowCroqui() {
    const plate = document.getElementById('inputPlate')?.value?.trim();
    const ra = document.getElementById('inputRA')?.value?.trim();
    
    if (!plate || !ra) {
        showNotification('Matrícula e RA são obrigatórios', 'error');
        return;
    }
    
    try {
        // Fetch delivery inspection data from backend
        const response = await fetch(`/api/get_inspection?plate=${encodeURIComponent(plate)}&ra=${encodeURIComponent(ra)}&type=checkout`);
        
        if (!response.ok) {
            throw new Error('Erro ao buscar dados do check-out');
        }
        
        const data = await response.json();
        
        if (!data.success || !data.inspection) {
            showNotification('Não foi encontrado check-out para esta viatura', 'error');
            return;
        }
        
        // Mark that we are in PICKUP mode
        window.isPickupMode = true;
        window.pickupNewDamages = []; // Store new damages added during pickup (in red)
        
        // Store delivery data
        window.deliveryInspection = data.inspection;
        window.deliveryPhotos = data.photos || [];
        window.deliveryDamages = data.damages || [];
        
        console.log('📦 Delivery inspection loaded:', data.inspection);
        console.log('📸 Delivery photos:', data.photos.length);
        
        // Store delivery photos in inspectionData for reference
        if (data.photos && data.photos.length > 0) {
            data.photos.forEach(photo => {
                if (photo.photo_type && photo.image_data) {
                    inspectionData.photos[photo.photo_type] = photo.image_data;
                }
            });
        }
        
        // Navigate to damage diagram step
        showNotification('Dados do check-out carregados! Mostrando croqui...', 'success');
        
        // Hide photo steps, show diagram step
        document.querySelectorAll('.step-content').forEach(step => step.classList.add('hidden'));
        const diagramStep = document.getElementById('stepDiagram');
        if (diagramStep) {
            diagramStep.classList.remove('hidden');
            
            // Update title for pickup mode
            const title = diagramStep.querySelector('h2');
            if (title) {
                title.textContent = 'Recolha de Viatura - Verificar Danos';
            }
            
            // Show pickup-specific UI
            showPickupDiagramUI();
        }
        
    } catch (error) {
        console.error('Error loading delivery data:', error);
        showNotification('Erro ao carregar dados do check-out: ' + error.message, 'error');
    }
}

// Show pickup-specific UI in diagram step
function showPickupDiagramUI() {
    console.log('🎨 Setting up pickup diagram UI...');
    
    // 1. Load delivery damages on croqui FIRST
    loadDeliveryDamagesOnCroqui();
    
    // 2. Modify croqui to allow adding new damages in red
    setupPickupCroquiMode();
    
    // 3. Add pickup action buttons
    addPickupActionButtons();
    
    // 4. Create and show delivery photos grid AFTER croqui
    showDeliveryPhotosGrid();
}

// Show grid of delivery photos (clickable to enlarge)
function showDeliveryPhotosGrid() {
    const diagramStep = document.getElementById('stepDiagram');
    if (!diagramStep) return;
    
    // Check if grid already exists
    let photosGrid = document.getElementById('deliveryPhotosGrid');
    if (photosGrid) {
        photosGrid.remove();
    }
    
    // Create photos grid container (clean design)
    photosGrid = document.createElement('div');
    photosGrid.id = 'deliveryPhotosGrid';
    photosGrid.style.cssText = `
        background: transparent;
        padding: 0;
        margin-bottom: 30px;
    `;
    
    // FIRST: Add damage photos section if exists (RECOLHA PRIMEIRO)
    if (window.pickupDamagePhotos && window.pickupDamagePhotos.length > 0) {
        // Title
        const damageTitle = document.createElement('h3');
        damageTitle.textContent = 'Fotos Recolha - Danos';
        damageTitle.style.cssText = `
            color: #333;
            font-size: 16px;
            font-weight: 600;
            margin-bottom: 15px;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        `;
        photosGrid.appendChild(damageTitle);
        
        // Grid
        const damageGrid = document.createElement('div');
        damageGrid.style.cssText = `
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        `;
        
        window.pickupDamagePhotos.forEach(photo => {
            const photoCard = document.createElement('div');
            photoCard.style.cssText = `cursor: pointer; transition: transform 0.2s;`;
            photoCard.addEventListener('mouseenter', () => photoCard.style.transform = 'scale(1.05)');
            photoCard.addEventListener('mouseleave', () => photoCard.style.transform = 'scale(1)');
            
            const img = document.createElement('img');
            img.src = photo.imageData;
            img.style.cssText = `width: 100%; height: 150px; object-fit: cover; border-radius: 8px;`;
            
            const label = document.createElement('div');
            label.textContent = formatPhotoType(photo.side);
            label.style.cssText = `color: #666; padding: 8px 0; text-align: center; font-size: 13px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;`;
            
            photoCard.appendChild(img);
            photoCard.appendChild(label);
            photoCard.addEventListener('click', () => enlargePhoto(photo.imageData, photo.side));
            damageGrid.appendChild(photoCard);
        });
        
        photosGrid.appendChild(damageGrid);
    }
    
    // SECOND: Add delivery photos section (ENTREGA DEPOIS)
    // Title
    const deliveryTitle = document.createElement('h3');
    deliveryTitle.textContent = 'Fotos da Entrega';
    deliveryTitle.style.cssText = `
        color: #333;
        font-size: 16px;
        font-weight: 600;
        margin-bottom: 15px;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    `;
    photosGrid.appendChild(deliveryTitle);
    
    // Grid of delivery photos
    const deliveryGrid = document.createElement('div');
    deliveryGrid.style.cssText = `
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
        gap: 20px;
    `;
    
    // Add each delivery photo
    if (window.deliveryPhotos && window.deliveryPhotos.length > 0) {
        window.deliveryPhotos.forEach(photo => {
            if (photo.photo_type !== 'damage_croqui') {
                const photoCard = document.createElement('div');
                photoCard.style.cssText = `cursor: pointer; transition: transform 0.2s;`;
                photoCard.addEventListener('mouseenter', () => photoCard.style.transform = 'scale(1.05)');
                photoCard.addEventListener('mouseleave', () => photoCard.style.transform = 'scale(1)');
                
                const img = document.createElement('img');
                img.src = photo.image_data;
                img.style.cssText = `width: 100%; height: 150px; object-fit: cover; border-radius: 8px;`;
                
                const label = document.createElement('div');
                label.textContent = formatPhotoType(photo.photo_type);
                label.style.cssText = `color: #666; padding: 8px 0; text-align: center; font-size: 13px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;`;
                
                photoCard.appendChild(img);
                photoCard.appendChild(label);
                photoCard.addEventListener('click', () => enlargePhoto(photo.image_data, photo.photo_type));
                deliveryGrid.appendChild(photoCard);
            }
        });
    } else {
        const noPhotos = document.createElement('p');
        noPhotos.textContent = 'Nenhuma foto encontrada';
        noPhotos.style.cssText = 'text-align: center; color: #999; padding: 20px; font-family: -apple-system, BlinkMacSystemFont, \'Segoe UI\', sans-serif;';
        deliveryGrid.appendChild(noPhotos);
    }
    
    photosGrid.appendChild(deliveryGrid);
    
    // Insert AFTER the croqui (at the end of diagram step)
    const diagramContainer = diagramStep.querySelector('.car-diagram-container');
    if (diagramContainer) {
        diagramContainer.appendChild(photosGrid);
    }
}

// Update delivery photos grid to include damage photos (RECOLHA PRIMEIRO)
function updateDeliveryPhotosGridWithDamages() {
    // Simply rebuild the entire grid with new order
    showDeliveryPhotosGrid();
}

// Format photo type for display
function formatPhotoType(type) {
    const labels = {
        'front': 'Frente',
        'front_left': 'Frente Esq.',
        'left': 'Esquerda',
        'back_left': 'Trás Esq.',
        'back': 'Trás',
        'back_right': 'Trás Dir.',
        'right': 'Direita',
        'front_right': 'Frente Dir.',
        'odometer': 'Odómetro'
    };
    return labels[type] || type;
}

// Enlarge photo in modal
function enlargePhoto(imageData, photoType) {
    // Create modal
    const modal = document.createElement('div');
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.9);
        z-index: 10000;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 20px;
    `;
    
    // Close on click
    modal.addEventListener('click', () => {
        modal.remove();
    });
    
    // Image container
    const container = document.createElement('div');
    container.style.cssText = `
        max-width: 90%;
        max-height: 90%;
        position: relative;
    `;
    container.addEventListener('click', (e) => {
        e.stopPropagation();
    });
    
    // Image
    const img = document.createElement('img');
    img.src = imageData;
    img.alt = photoType;
    img.style.cssText = `
        max-width: 100%;
        max-height: 80vh;
        border-radius: 8px;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
    `;
    
    // Label
    const label = document.createElement('div');
    label.textContent = formatPhotoType(photoType);
    label.style.cssText = `
        background: #009cb6;
        color: white;
        padding: 10px 20px;
        text-align: center;
        font-size: 18px;
        font-weight: bold;
        border-radius: 8px;
        margin-top: 10px;
    `;
    
    // Close button
    const closeBtn = document.createElement('button');
    closeBtn.textContent = '✕';
    closeBtn.style.cssText = `
        position: absolute;
        top: -10px;
        right: -10px;
        background: #dc3545;
        color: white;
        border: none;
        border-radius: 50%;
        width: 40px;
        height: 40px;
        font-size: 24px;
        cursor: pointer;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
    `;
    closeBtn.addEventListener('click', () => {
        modal.remove();
    });
    
    container.appendChild(img);
    container.appendChild(label);
    container.appendChild(closeBtn);
    modal.appendChild(container);
    document.body.appendChild(modal);
}

// Add pickup action buttons
function addPickupActionButtons() {
    const diagramStep = document.getElementById('stepDiagram');
    if (!diagramStep) return;
    
    // Check if buttons already exist
    let buttonsContainer = document.getElementById('pickupActionButtons');
    if (buttonsContainer) {
        buttonsContainer.remove();
    }
    
    // Create buttons container
    buttonsContainer = document.createElement('div');
    buttonsContainer.id = 'pickupActionButtons';
    buttonsContainer.style.cssText = `
        display: flex;
        gap: 15px;
        justify-content: center;
        margin-top: 30px;
        padding: 20px;
    `;
    
    // Button: Registar Novos Danos
    const btnNewDamages = document.createElement('button');
    btnNewDamages.textContent = 'Registar Novos Danos';
    btnNewDamages.style.cssText = `
        background: #ff9800;
        color: white;
        border: none;
        padding: 15px 30px;
        border-radius: 8px;
        font-size: 16px;
        font-weight: bold;
        cursor: pointer;
        transition: background 0.2s;
    `;
    btnNewDamages.addEventListener('mouseenter', () => {
        btnNewDamages.style.background = '#f57c00';
    });
    btnNewDamages.addEventListener('mouseleave', () => {
        btnNewDamages.style.background = '#ff9800';
    });
    btnNewDamages.addEventListener('click', startRegisterNewDamages);
    
    // Button: Terminar Recolha
    const btnFinishPickup = document.createElement('button');
    btnFinishPickup.textContent = 'Terminar Recolha';
    btnFinishPickup.style.cssText = `
        background: #28a745;
        color: white;
        border: none;
        padding: 15px 30px;
        border-radius: 8px;
        font-size: 16px;
        font-weight: bold;
        cursor: pointer;
        transition: background 0.2s;
    `;
    btnFinishPickup.addEventListener('mouseenter', () => {
        btnFinishPickup.style.background = '#218838';
    });
    btnFinishPickup.addEventListener('mouseleave', () => {
        btnFinishPickup.style.background = '#28a745';
    });
    btnFinishPickup.addEventListener('click', finishPickup);
    
    buttonsContainer.appendChild(btnNewDamages);
    buttonsContainer.appendChild(btnFinishPickup);
    
    // Add to diagram step
    const diagramContainer = diagramStep.querySelector('.car-diagram-container');
    if (diagramContainer) {
        diagramContainer.appendChild(buttonsContainer);
    }
}

// Load delivery damages on croqui
function loadDeliveryDamagesOnCroqui() {
    console.log('📍 Loading delivery damages on croqui...');
    
    if (!window.deliveryPhotos || window.deliveryPhotos.length === 0) {
        console.log('⚠️ No delivery photos to load damages from');
        return;
    }
    
    // Find the damage_croqui photo
    const croquiPhoto = window.deliveryPhotos.find(p => p.photo_type === 'damage_croqui');
    
    if (!croquiPhoto || !croquiPhoto.image_data) {
        console.log('⚠️ No damage croqui found in delivery photos');
        return;
    }
    
    // Load the croqui image with damages
    const croquiImg = document.getElementById('carCroqui');
    if (croquiImg) {
        croquiImg.src = croquiPhoto.image_data;
        console.log('✅ Loaded delivery damage croqui');
    }
}

// Setup pickup croqui mode - new damages will be red
function setupPickupCroquiMode() {
    console.log('🎨 Setting up pickup croqui mode - new damages will be RED');
    // The actual red color logic is in addPin() function in the HTML
    // which checks window.isPickupMode
}

// Start registering new damages
function startRegisterNewDamages() {
    console.log('📸 Starting new damage registration...');
    
    // Show modal to select which side to photograph
    showDamageSideSelectionModal();
}

// Show modal to select damage photo side
function showDamageSideSelectionModal() {
    const sides = [
        { id: 'front', label: 'Vista Frontal', image: 'Vista Frontal.png' },
        { id: 'front_left', label: 'Vista Frontal Esquerda', image: 'Vista Frontal Esquerda.png' },
        { id: 'left', label: 'Vista Lateral Esquerda', image: 'Vista Lateral Esquerda.png' },
        { id: 'back_left', label: 'Vista Traseira Esquerda', image: 'Vista Traseira Esquerda.png' },
        { id: 'back', label: 'Vista Traseira', image: 'Vista Traseira.png' },
        { id: 'back_right', label: 'Vista Traseira Direita', image: 'Vista Traseira direita.png' },
        { id: 'right', label: 'Vista Lateral Direita', image: 'Vista Lateral Direita.png' },
        { id: 'front_right', label: 'Vista Frontal Direita', image: 'Vista Frontal Direita.png' },
        { id: 'odometer', label: 'Odómetro', image: 'Odometro.png' }
    ];
    
    let sidesHTML = '';
    sides.forEach(side => {
        sidesHTML += `
            <div onclick="selectDamageSide('${side.id}')" 
                 style="background: rgba(255,255,255,0.05); border: 2px solid rgba(0,156,182,0.3); border-radius: 12px; padding: 12px; cursor: pointer; transition: all 0.3s; text-align: center;" 
                 onmouseover="this.style.background='rgba(0,156,182,0.15)'; this.style.borderColor='#009cb6'; this.style.transform='translateY(-3px)';" 
                 onmouseout="this.style.background='rgba(255,255,255,0.05)'; this.style.borderColor='rgba(0,156,182,0.3)'; this.style.transform='translateY(0)';">
                <div style="color: #009cb6; font-weight: 600; font-size: 11px; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.5px;">
                    ${side.label}
                </div>
                <img src="/static/Inspecçao/${side.image}" alt="${side.label}" style="width: 100%; height: 75px; object-fit: contain; display: block; margin: 0 auto; filter: brightness(1.1);">
            </div>
        `;
    });
    
    const modalHTML = `
        <div id="damageSideModal" style="position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: linear-gradient(135deg, rgba(0,0,0,0.95) 0%, rgba(0,30,40,0.95) 100%); z-index: 10000; display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 20px; overflow-y: auto; backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px);">
            <div style="max-width: 500px; width: 100%;">
                <h2 style="color: white; font-size: 24px; font-weight: 700; margin-bottom: 8px; text-align: center; letter-spacing: -0.5px;">
                    Recolha de Viatura
                </h2>
                <p style="color: rgba(255,255,255,0.7); font-size: 14px; margin-bottom: 25px; text-align: center;">
                    Verificar Danos - Selecione a vista para fotografar
                </p>
                
                <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 25px;">
                    ${sidesHTML}
                </div>
                
                <button onclick="closeDamageSideModal()" style="width: 100%; padding: 14px; background: rgba(220,53,69,0.9); color: white; border: none; border-radius: 12px; font-size: 15px; font-weight: 600; cursor: pointer; transition: all 0.3s; box-shadow: 0 4px 15px rgba(220,53,69,0.3);" 
                        onmouseover="this.style.background='rgba(220,53,69,1)'; this.style.transform='translateY(-2px)'; this.style.boxShadow='0 6px 20px rgba(220,53,69,0.4)';" 
                        onmouseout="this.style.background='rgba(220,53,69,0.9)'; this.style.transform='translateY(0)'; this.style.boxShadow='0 4px 15px rgba(220,53,69,0.3)';">
                    Cancelar
                </button>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', modalHTML);
}

// Close damage side selection modal
function closeDamageSideModal() {
    const modal = document.getElementById('damageSideModal');
    if (modal) {
        modal.remove();
    }
}

// Select damage side and open camera
function selectDamageSide(side) {
    console.log('📸 Selected damage side:', side);
    
    // Close modal
    closeDamageSideModal();
    
    // Store selected side
    window.currentDamageSide = side;
    
    // Open camera to capture damage photo
    captureDamagePhoto(side);
}

// Capture damage photo
function captureDamagePhoto(side) {
    showNotification(`Abrindo câmera para fotografar: ${formatPhotoType(side)}`, 'info');
    
    // Open camera for damage photo
    openCameraForDamage(side);
}

// Open camera for damage photo
async function openCameraForDamage(photoType) {
    window.currentDamageSide = photoType;
    
    // Set flag to indicate this is a pickup damage photo
    window.isPickupDamagePhoto = true;
    window.currentDamagePhotoType = photoType;
    
    // Use CHECKOUT camera function directly
    await openCamera(photoType);
}

// Show countdown - EXACTLY like checkout
function showDamageCountdown(photoType, photoLabel, photoInstruction) {
    return new Promise((resolve) => {
        // Get the reference image for this photo type
        const photo = photoTypes.find(p => p.type === photoType);
        const imageUrl = photo ? `/static/Inspecçao/${photo.image}` : '';
        
        // Show car miniature BEFORE countdown (EXACTLY like checkout)
        const miniature = document.getElementById('damageCarMiniature');
        if (miniature) {
            const miniatureImg = miniature.querySelector('img');
            if (miniatureImg) {
                miniatureImg.src = imageUrl;
                miniatureImg.alt = photoLabel;
            }
            miniature.style.display = 'block';
        }
        
        // Create countdown overlay - EXACTLY like checkout
        const countdownOverlay = document.createElement('div');
        countdownOverlay.id = 'damageCountdown';
        countdownOverlay.style.cssText = `
            position: fixed;
            inset: 0;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            z-index: 99999;
            pointer-events: none;
            background: rgba(0, 0, 0, 0.8);
        `;
        
        countdownOverlay.innerHTML = `
            <div style="position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0, 0, 0, 0.7); z-index: -1;"></div>
            
            <!-- Text at top -->
            <div style="position: absolute; top: 50px; left: 0; right: 0; text-align: center; z-index: 10;">
                <h3 style="font-size: 22px; font-weight: 600; color: white; margin-bottom: 8px; text-shadow: 0 2px 8px rgba(0,0,0,0.5);">${photoLabel}</h3>
                <p style="font-size: 14px; font-weight: 400; color: white; opacity: 0.8; text-shadow: 0 2px 8px rgba(0,0,0,0.5);">${photoInstruction}</p>
            </div>
            
            <!-- Countdown circle in center -->
            <div style="text-align: center; position: relative; z-index: 10;">
                <svg width="160" height="160" viewBox="0 0 160 160" style="transform: rotate(-90deg);">
                    <circle cx="80" cy="80" r="70" fill="none" stroke="rgba(255,255,255,0.15)" stroke-width="10"/>
                    <circle id="damageCountdownCircle" cx="80" cy="80" r="70" fill="none" stroke="#009cb6" stroke-width="10" 
                        stroke-dasharray="440" stroke-dashoffset="0" 
                        style="transition: stroke-dashoffset 1s linear;"/>
                </svg>
                <div id="damageCountdownNumber" style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); font-size: 72px; font-weight: 800; color: white; text-shadow: 0 4px 12px rgba(0,0,0,0.5);">3</div>
            </div>
            
            <!-- Space for buttons at bottom (they will be visible underneath) -->
        `;
        
        document.body.appendChild(countdownOverlay);
        
        // Countdown animation
        let count = 3;
        const circle = document.getElementById('damageCountdownCircle');
        const numberEl = document.getElementById('damageCountdownNumber');
        const circumference = 440; // 2 * PI * 70
        
        const interval = setInterval(() => {
            count--;
            const progress = count / 3;
            circle.style.strokeDashoffset = circumference * (1 - progress);
            
            if (count > 0) {
                numberEl.textContent = count;
            } else {
                clearInterval(interval);
                countdownOverlay.remove();
                resolve();
            }
        }, 1000);
    });
}

// Start camera for damage photo
async function startDamageCamera() {
    try {
        const video = document.getElementById('damageVideo');
        const stream = await navigator.mediaDevices.getUserMedia({
            video: { facingMode: 'environment' }
        });
        video.srcObject = stream;
        window.damageCameraStream = stream;
    } catch (error) {
        console.error('Error starting camera:', error);
        showNotification('Erro ao aceder à câmera: ' + error.message, 'error');
        closeDamagePhotoModal();
    }
}

// Capture damage photo now
function captureDamagePhotoNow() {
    const video = document.getElementById('damageVideo');
    const canvas = document.getElementById('damageCanvas');
    const ctx = canvas.getContext('2d');
    
    // Set canvas size to video size
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    
    // Draw video frame to canvas
    ctx.drawImage(video, 0, 0);
    
    // Get base64 image
    const imageData = canvas.toDataURL('image/jpeg', 0.9);
    
    // Stop camera
    if (window.damageCameraStream) {
        window.damageCameraStream.getTracks().forEach(track => track.stop());
    }
    
    // Close modal
    closeDamagePhotoModal();
    
    // Store damage photo
    if (!window.pickupDamagePhotos) {
        window.pickupDamagePhotos = [];
    }
    
    window.pickupDamagePhotos.push({
        side: window.currentDamageSide,
        imageData: imageData,
        timestamp: new Date().toISOString()
    });
    
    // Update the photos grid to show the new damage photo
    updateDeliveryPhotosGridWithDamages();
    
    showNotification('Foto capturada! Deseja adicionar mais fotos?', 'success');
    
    // Ask if wants to add more photos
    askAddMoreDamagePhotos();
}

// Close damage photo modal
function closeDamagePhotoModal() {
    // Stop camera
    if (window.damageCameraStream) {
        window.damageCameraStream.getTracks().forEach(track => track.stop());
    }
    
    const modal = document.getElementById('damagePhotoModal');
    if (modal) {
        modal.remove();
    }
}

// Ask if wants to add more damage photos
function askAddMoreDamagePhotos() {
    const modalHTML = `
        <div id="addMorePhotosModal" style="position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.85); z-index: 10000; display: flex; align-items: center; justify-content: center;">
            <div style="background: white; padding: 40px; border-radius: 12px; max-width: 500px; width: 90%; box-shadow: 0 10px 40px rgba(0,0,0,0.3);">
                <h2 style="color: #009cb6; font-size: 24px; font-weight: bold; margin-bottom: 20px; text-align: center;">
                    Adicionar Mais Fotos?
                </h2>
                <p style="color: #666; margin-bottom: 30px; text-align: center;">
                    Deseja adicionar mais fotos de danos ou terminar o registo?
                </p>
                
                <div style="display: flex; gap: 15px;">
                    <button onclick="addAnotherDamagePhoto()" style="flex: 1; padding: 15px; background: #ff9800; color: white; border: none; border-radius: 8px; font-size: 16px; font-weight: bold; cursor: pointer;">
                        Adicionar Mais
                    </button>
                    <button onclick="finishAddingDamagePhotos()" style="flex: 1; padding: 15px; background: #28a745; color: white; border: none; border-radius: 8px; font-size: 16px; font-weight: bold; cursor: pointer;">
                        Terminar
                    </button>
                </div>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', modalHTML);
}

// Add another damage photo
function addAnotherDamagePhoto() {
    const modal = document.getElementById('addMorePhotosModal');
    if (modal) {
        modal.remove();
    }
    
    // Show side selection again
    showDamageSideSelectionModal();
}

// Finish adding damage photos
function finishAddingDamagePhotos() {
    const modal = document.getElementById('addMorePhotosModal');
    if (modal) {
        modal.remove();
    }
    
    const photoCount = window.pickupDamagePhotos ? window.pickupDamagePhotos.length : 0;
    showNotification(`${photoCount} foto(s) de novos danos registada(s)!`, 'success');
}

// Finish pickup and show summary
function finishPickup() {
    console.log('✅ Finishing pickup...');
    
    // Validate that we have all required data
    if (!window.deliveryInspection) {
        showNotification('Erro: Dados do check-out não encontrados', 'error');
        return;
    }
    
    // Show pickup summary modal
    showPickupSummaryModal();
}

// Show pickup summary modal (like checkout summary)
function showPickupSummaryModal() {
    const plate = document.getElementById('inputPlate')?.value?.trim();
    const ra = document.getElementById('inputRA')?.value?.trim();
    const odometer = document.getElementById('odometerReading')?.value;
    const fuel = document.getElementById('fuelSlider')?.value;
    
    // Count new damage photos
    const newDamagePhotosCount = window.pickupDamagePhotos ? window.pickupDamagePhotos.length : 0;
    const newDamagesCount = window.pickupNewDamages ? window.pickupNewDamages.length : 0;
    
    const modalHTML = `
        <div id="pickupSummaryModal" style="position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.9); z-index: 10000; display: flex; align-items: center; justify-content: center; padding: 20px; overflow-y: auto;">
            <div style="background: white; padding: 40px; border-radius: 12px; max-width: 800px; width: 100%; box-shadow: 0 10px 40px rgba(0,0,0,0.5);">
                <h2 style="color: #28a745; font-size: 28px; font-weight: bold; margin-bottom: 10px; text-align: center;">
                    ✅ Recolha de Viatura Completa
                </h2>
                <p style="color: #666; margin-bottom: 30px; text-align: center; font-size: 14px;">
                    Todos os dados foram registados com sucesso
                </p>
                
                <!-- Summary Info -->
                <div style="background: #f8f9fa; border-radius: 8px; padding: 20px; margin-bottom: 30px;">
                    <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px;">
                        <div>
                            <div style="color: #666; font-size: 12px; margin-bottom: 5px;">Matrícula</div>
                            <div style="color: #009cb6; font-size: 18px; font-weight: bold;">${plate}</div>
                        </div>
                        <div>
                            <div style="color: #666; font-size: 12px; margin-bottom: 5px;">RA</div>
                            <div style="color: #009cb6; font-size: 18px; font-weight: bold;">${ra}</div>
                        </div>
                        <div>
                            <div style="color: #666; font-size: 12px; margin-bottom: 5px;">Km Entrada</div>
                            <div style="color: #009cb6; font-size: 18px; font-weight: bold;">${odometer} km</div>
                        </div>
                        <div>
                            <div style="color: #666; font-size: 12px; margin-bottom: 5px;">Combustível</div>
                            <div style="color: #009cb6; font-size: 18px; font-weight: bold;">${fuel}%</div>
                        </div>
                        <div>
                            <div style="color: #666; font-size: 12px; margin-bottom: 5px;">Fotos do Check-out</div>
                            <div style="color: #009cb6; font-size: 18px; font-weight: bold;">${window.deliveryPhotos ? window.deliveryPhotos.length : 0}</div>
                        </div>
                        <div>
                            <div style="color: #666; font-size: 12px; margin-bottom: 5px;">Novos Danos</div>
                            <div style="color: #dc3545; font-size: 18px; font-weight: bold;">${newDamagesCount} (${newDamagePhotosCount} fotos)</div>
                        </div>
                    </div>
                </div>
                
                <!-- Action Buttons -->
                <div style="display: flex; flex-direction: column; gap: 15px;">
                    <button onclick="saveAndEmailPickup()" style="width: 100%; padding: 20px; background: #009cb6; color: white; border: none; border-radius: 8px; font-size: 18px; font-weight: bold; cursor: pointer; transition: background 0.2s;">
                        💾 Guardar e Enviar Email
                    </button>
                    <button onclick="savePickupOnly()" style="width: 100%; padding: 20px; background: #28a745; color: white; border: none; border-radius: 8px; font-size: 18px; font-weight: bold; cursor: pointer; transition: background 0.2s;">
                        💾 Só Guardar
                    </button>
                    <button onclick="closePickupSummary()" style="width: 100%; padding: 15px; background: #6c757d; color: white; border: none; border-radius: 8px; font-size: 16px; font-weight: bold; cursor: pointer;">
                        Cancelar
                    </button>
                </div>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', modalHTML);
}

// Close pickup summary
function closePickupSummary() {
    const modal = document.getElementById('pickupSummaryModal');
    if (modal) {
        modal.remove();
    }
}

// Save and email pickup
async function saveAndEmailPickup() {
    showNotification('Guardando recolha e enviando email...', 'info');
    
    const success = await savePickupInspection();
    
    if (success) {
        // Close summary modal
        closePickupSummary();
        
        // TODO: Send email
        showNotification('Recolha guardada com sucesso! Email será enviado...', 'success');
        
        // Redirect after delay
        setTimeout(() => {
            window.location.href = '/vehicle-inspection';
        }, 2000);
    }
}

// Save pickup only
async function savePickupOnly() {
    showNotification('Guardando recolha...', 'info');
    
    const success = await savePickupInspection();
    
    if (success) {
        // Close summary modal
        closePickupSummary();
        
        showNotification('Recolha guardada com sucesso!', 'success');
        
        // Redirect after delay
        setTimeout(() => {
            window.location.href = '/vehicle-inspection';
        }, 2000);
    }
}

// Save pickup inspection to backend
async function savePickupInspection() {
    try {
        // Prepare inspection data
        const plate = document.getElementById('inputPlate')?.value?.trim();
        const ra = document.getElementById('inputRA')?.value?.trim();
        const odometer = document.getElementById('odometerReading')?.value;
        const fuel = document.getElementById('fuelSlider')?.value;
        const receptionist = document.getElementById('inputReceptionist')?.value?.trim();
        const observations = document.getElementById('inputObservations')?.value?.trim();
        
        // Get damage croqui (with new damages in red)
        const damageCroqui = await captureDamageCroqui();
        
        // Prepare photos object (delivery photos + new damage photos)
        const photos = {};
        
        // Add delivery photos
        if (window.deliveryPhotos) {
            window.deliveryPhotos.forEach(photo => {
                if (photo.photo_type !== 'damage_croqui') {
                    photos[photo.photo_type] = photo.image_data;
                }
            });
        }
        
        // Add new damage photos with unique keys
        if (window.pickupDamagePhotos) {
            window.pickupDamagePhotos.forEach((photo, index) => {
                photos[`new_damage_${index}`] = photo.imageData;
            });
        }
        
        // Prepare request data
        const requestData = {
            inspection_type: 'checkin',
            plate: plate,
            ra: ra,
            odometer_reading: parseInt(odometer),
            fuel_level: parseInt(fuel),
            receptionist: receptionist,
            observations: observations,
            has_damage: (window.pickupNewDamages && window.pickupNewDamages.length > 0),
            damage_count: window.pickupNewDamages ? window.pickupNewDamages.length : 0,
            photos: photos,
            damage_croqui: damageCroqui
        };
        
        console.log('📤 Saving pickup inspection...', requestData);
        
        // Send to backend
        const response = await fetch('/api/save-inspection', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        });
        
        if (!response.ok) {
            throw new Error('Erro ao guardar recolha');
        }
        
        const data = await response.json();
        
        if (data.ok) {
            console.log('✅ Pickup inspection saved successfully');
            return true;
        } else {
            throw new Error(data.error || 'Erro desconhecido');
        }
        
    } catch (error) {
        console.error('Error saving pickup inspection:', error);
        showNotification('Erro ao guardar recolha: ' + error.message, 'error');
        return false;
    }
}

// Capture damage croqui (helper function)
async function captureDamageCroqui() {
    try {
        const canvas = document.getElementById('drawingCanvas');
        const container = document.getElementById('carDiagram');
        
        if (!canvas || !container) {
            console.warn('Canvas or container not found');
            return '';
        }
        
        // Create temporary canvas
        const tempCanvas = document.createElement('canvas');
        const tempCtx = tempCanvas.getContext('2d');
        const croquiImg = container.querySelector('img');
        
        if (!croquiImg || !croquiImg.complete) {
            console.warn('Croqui image not loaded');
            return '';
        }
        
        // Set canvas size
        tempCanvas.width = croquiImg.naturalWidth;
        tempCanvas.height = croquiImg.naturalHeight;
        
        // Draw croqui image
        tempCtx.drawImage(croquiImg, 0, 0);
        
        // Draw canvas content (lines/drawings)
        if (canvas.width > 0 && canvas.height > 0) {
            tempCtx.drawImage(canvas, 0, 0, tempCanvas.width, tempCanvas.height);
        }
        
        // Draw pins
        const pins = container.querySelectorAll('.damage-pin');
        pins.forEach(pin => {
            const rect = container.getBoundingClientRect();
            const pinRect = pin.getBoundingClientRect();
            
            const x = (pinRect.left - rect.left) / rect.width * tempCanvas.width;
            const y = (pinRect.top - rect.top) / rect.height * tempCanvas.height;
            
            const size = pin.classList.contains('size-small') ? 8 : 
                        pin.classList.contains('size-large') ? 20 : 12;
            
            // Check if it's a new damage (red color)
            const isNewDamage = pin.style.background === 'rgb(220, 53, 69)' || pin.style.background === '#dc3545';
            
            tempCtx.fillStyle = isNewDamage ? '#dc3545' : '#000000';
            tempCtx.beginPath();
            tempCtx.arc(x, y, size, 0, Math.PI * 2);
            tempCtx.fill();
        });
        
        // Return base64
        return tempCanvas.toDataURL('image/png');
        
    } catch (error) {
        console.error('Error capturing damage croqui:', error);
        return '';
    }
}

// Auto Sequence Mode (legacy - now called by startDelivery)
function startAutoSequence() {
    startDelivery();
}

function capturePhotoSequence(index) {
    // Clear old photos when starting new inspection (index 0)
    if (index === 0) {
        console.log('🧹 Starting new inspection - clearing old photos');
        inspectionData.photos = {};
        window.inspectionData = inspectionData;
        localStorage.removeItem('inspectionPhotos');
    }
    
    if (index >= photoTypes.length) {
        console.log('All photos captured');
        return;
    }
    
    const photoType = photoTypes[index].type;
    
    // Show car diagram preview first, then open camera
    showCarDiagramPreview(photoType);
}

// Countdown removed - now happens in camera modal

// Show car diagram preview before opening camera
async function showCarDiagramPreview(photoType) {
    const photo = photoTypes.find(p => p.type === photoType);
    if (!photo) return;
    
    // Create preview modal
    const previewModal = document.createElement('div');
    previewModal.id = 'carDiagramPreview';
    previewModal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.95);
        z-index: 999999;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 20px;
    `;
    
    // Use specific image from Inspecção folder
    const imagePath = `/static/Inspecçao/${photo.image}`;
    console.log(`🖼️ Loading image for ${photo.label}: ${imagePath}`);
    
    previewModal.innerHTML = `
        <style>
            @keyframes spin {
                from { transform: translate(-50%, -50%) rotate(0deg); }
                to { transform: translate(-50%, -50%) rotate(360deg); }
            }
            .countdown-circle {
                animation: spin 2s linear infinite;
            }
        </style>
        
        <div style="position: absolute; top: 60px; left: 0; right: 0; text-align: center; z-index: 10;">
            <h2 style="color: white; font-size: 20px; margin: 0 0 8px 0; font-weight: 600; line-height: 1.2;">${photo.label}</h2>
            <p style="color: #ff4757; font-size: 14px; margin: 0; font-weight: 500; max-width: 300px; margin: 0 auto;">${photo.instruction}</p>
        </div>
        
        <div style="display: flex; flex-direction: column; justify-content: center; align-items: center; min-height: 100vh; padding: 140px 20px 20px 20px;">
            <img id="previewCarImage" src="${imagePath}" alt="${photo.label}" style="max-width: 180px; width: 100%; height: auto; display: block; margin: 0 auto;">
            
            <!-- Countdown - centered horizontally below image -->
            <div style="position: relative; width: 100%; text-align: center; margin-top: 60px;">
                <div id="previewCountdown" style="
                    display: inline-block;
                    font-size: 43px;
                    font-weight: bold;
                    color: #ff4757;
                    text-shadow: 0 0 20px rgba(0, 0, 0, 0.8), 0 4px 8px rgba(0, 0, 0, 0.5);
                    position: relative;
                    z-index: 10;
                ">3</div>
            
                <!-- Spinning circle around countdown -->
                <div id="countdownCircle" class="countdown-circle" style="
                    position: absolute;
                    top: 50%;
                    left: 50%;
                    transform: translate(-50%, -50%);
                    width: 67px;
                    height: 67px;
                    border: 3px solid transparent;
                    border-top-color: white;
                    border-right-color: white;
                    border-radius: 50%;
                    display: none;
                    z-index: 9;
                "></div>
            </div>
        </div>
        
        <!-- Loading message -->
        <div id="cameraPermissionMsg" style="
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            color: white;
            font-size: 16px;
            text-align: center;
            background: rgba(0, 0, 0, 0.8);
            padding: 15px 25px;
            border-radius: 8px;
            display: block;
            z-index: 11;
        ">A pedir permissão da câmera...</div>
    `;
    
    document.body.appendChild(previewModal);
    
    // Force image to load and display
    const carImage = document.getElementById('previewCarImage');
    if (carImage) {
        carImage.onload = () => {
            console.log('✅ Car image loaded successfully');
        };
        carImage.onerror = () => {
            console.error('❌ Failed to load car image:', imagePath);
        };
    }
    
    // Check if we already have camera permission/stream
    if (window.savedCameraStream || window.pendingCameraStream || cameraStream) {
        // Already have permission, hide message and start countdown immediately
        console.log('✅ Camera permission already granted');
        const permMsg = document.getElementById('cameraPermissionMsg');
        if (permMsg) permMsg.style.display = 'none';
        
        // Reuse existing stream if available
        if (window.savedCameraStream && window.savedCameraStream.active) {
            window.pendingCameraStream = window.savedCameraStream;
        }
        
        setTimeout(() => {
            startPreviewCountdown(photoType);
        }, 500);
    } else {
        // Request camera permission first time
        try {
            console.log('🎥 Requesting camera permission...');
            const stream = await navigator.mediaDevices.getUserMedia({
                video: {
                    facingMode: 'environment',
                    width: { ideal: 1920 },
                    height: { ideal: 1080 }
                }
            });
            
            // Store stream globally for reuse
            window.savedCameraStream = stream;
            window.pendingCameraStream = stream;
            
            // Hide permission message
            const permMsg = document.getElementById('cameraPermissionMsg');
            if (permMsg) permMsg.style.display = 'none';
            
            // Start countdown after permission granted
            setTimeout(() => {
                startPreviewCountdown(photoType);
            }, 500);
            
        } catch (error) {
            console.error('❌ Camera permission denied:', error);
            const modal = document.getElementById('carDiagramPreview');
            if (modal) modal.remove();
            showNotification('Permissão da câmera negada. Por favor, permita o acesso à câmera.', 'error');
        }
    }
}

// Countdown in preview modal before opening camera
function startPreviewCountdown(photoType) {
    const countdownEl = document.getElementById('previewCountdown');
    const circleEl = document.getElementById('countdownCircle');
    
    if (!countdownEl) {
        const modal = document.getElementById('carDiagramPreview');
        if (modal) modal.remove();
        openCameraWithStream(photoType);
        return;
    }
    
    // Show countdown and spinning circle
    countdownEl.style.display = 'block';
    if (circleEl) circleEl.style.display = 'block';
    
    let count = 3;
    countdownEl.textContent = count;
    
    const interval = setInterval(() => {
        count--;
        if (count > 0) {
            countdownEl.textContent = count;
        } else {
            clearInterval(interval);
            const modal = document.getElementById('carDiagramPreview');
            if (modal) modal.remove();
            openCameraWithStream(photoType);
        }
    }, 1000);
}

// Show car miniature with position marker
function showCarMiniature(photoType) {
    const photo = photoTypes.find(p => p.type === photoType);
    if (!photo) return;
    
    const miniature = document.getElementById('carMiniature');
    const miniatureImg = miniature ? miniature.querySelector('img') : null;
    
    if (!miniature || !miniatureImg) return;
    
    // Use specific image from Inspecção folder
    const imagePath = `/static/Inspecçao/${photo.image}`;
    miniatureImg.src = imagePath;
    miniatureImg.alt = photo.label;
    
    // Show miniature
    miniature.style.display = 'block';
}

// Open camera using already obtained stream (no additional countdown)
async function openCameraWithStream(photoType) {
    currentPhotoType = photoType;
    const photo = photoTypes.find(p => p.type === photoType);
    
    // Update modal content with simplified info
    const locationEl = document.getElementById('cameraLocation');
    const instructionEl = document.getElementById('cameraInstruction');
    
    if (locationEl) {
        locationEl.textContent = photo.label.toUpperCase();
        console.log(`📝 Updated title: ${photo.label.toUpperCase()}`);
    }
    if (instructionEl) {
        instructionEl.textContent = photo.instruction;
        console.log(`📝 Updated instruction: ${photo.instruction}`);
    }
    
    // Show modal
    const modal = document.getElementById('cameraModal');
    modal.classList.add('active');
    modal.style.opacity = '1';
    modal.style.pointerEvents = 'auto';
    
    // Request fullscreen with mobile support
    try {
        const elem = modal || document.documentElement;
        if (elem.requestFullscreen) {
            await elem.requestFullscreen();
        } else if (elem.webkitRequestFullscreen) {
            await elem.webkitRequestFullscreen();
        } else if (elem.webkitEnterFullscreen) {
            // iOS Safari
            await elem.webkitEnterFullscreen();
        } else if (elem.msRequestFullscreen) {
            await elem.msRequestFullscreen();
        } else if (elem.mozRequestFullScreen) {
            await elem.mozRequestFullScreen();
        }
        console.log('✅ Fullscreen activated for camera');
    } catch (error) {
        console.log('⚠️ Could not activate fullscreen:', error.message);
        // Try alternative method for mobile
        try {
            const video = document.getElementById('cameraPreview');
            if (video && video.webkitEnterFullscreen) {
                video.webkitEnterFullscreen();
            }
        } catch (e) {
            console.log('⚠️ Alternative fullscreen also failed');
        }
    }
    
    // Setup camera overlay for this photo type
    setupCameraOverlay(photoType);
    
    // Show and position car miniature
    showCarMiniature(photoType);
    
    // Initialize 3D car model
    init3DCar(photoType);
    
    // Use the stream we already obtained
    if (window.pendingCameraStream) {
        cameraStream = window.pendingCameraStream;
        // DON'T clear pendingCameraStream - we need it for next photos
        
        // Set video source
        const video = document.getElementById('cameraPreview');
        video.srcObject = cameraStream;
        video.style.display = 'block'; // Make sure video is visible
        
        // Show camera buttons immediately (no countdown)
        video.addEventListener('loadedmetadata', () => {
            const cameraButtons = document.getElementById('cameraButtons');
            if (cameraButtons) {
                cameraButtons.style.display = 'flex';
            }
            console.log('✅ Camera ready - buttons shown');
        });
    } else {
        console.error('❌ No pending camera stream found');
        closeCamera();
    }
}

// Camera functions
async function openCamera(photoType) {
currentPhotoType = photoType;
const photo = photoTypes.find(p => p.type === photoType);
    
// Update modal content with simplified info
document.getElementById('cameraLocation').textContent = photo.label.toUpperCase();
document.getElementById('cameraInstruction').textContent = photo.instruction;
    
// Show modal
const modal = document.getElementById('cameraModal');
modal.classList.add('active');
    
// Request fullscreen
try {
if (document.documentElement.requestFullscreen) {
await document.documentElement.requestFullscreen();
} else if (document.documentElement.webkitRequestFullscreen) {
await document.documentElement.webkitRequestFullscreen();
} else if (document.documentElement.msRequestFullscreen) {
await document.documentElement.msRequestFullscreen();
}
console.log('✅ Fullscreen activated for camera');
} catch (error) {
console.log('⚠️ Could not activate fullscreen:', error.message);
}
    
// Setup camera overlay for this photo type
setupCameraOverlay(photoType);
    
// Show and position car miniature
showCarMiniature(photoType);
    
// Initialize 3D car model
init3DCar(photoType);
    
try {
// Request camera access
cameraStream = await navigator.mediaDevices.getUserMedia({
video: {
facingMode: 'environment', // Use back camera on mobile
width: { ideal: 1920 },
height: { ideal: 1080 }
}
});
    
// Set video source
const video = document.getElementById('cameraPreview');
video.srcObject = cameraStream;
    
// Start countdown after video loads
video.addEventListener('loadedmetadata', () => {
startCameraCountdown();
});
    
} catch (error) {
console.error('Camera error:', error);
showNotification('Could not access camera: ' + error.message, 'error');
closeCamera();
}
}

function startCameraCountdown() {
    // Prevent multiple countdowns running simultaneously
    if (window.countdownRunning) {
        console.log('⚠️ Countdown already running, skipping...');
        return;
    }
    
    window.countdownRunning = true;
    
    // Remove any existing countdown and clear any running intervals
    const existingCountdown = document.getElementById('cameraCountdown');
    if (existingCountdown) {
        existingCountdown.remove();
    }
    
    // Clear any existing countdown intervals
    if (window.countdownInterval) {
        clearInterval(window.countdownInterval);
        window.countdownInterval = null;
    }
    
    // Make sure car miniature is visible during countdown
    const carMiniature = document.getElementById('carMiniature');
    if (carMiniature) {
        carMiniature.style.display = 'block';
        carMiniature.style.zIndex = '100000'; // Above countdown overlay
    }
    
    // Hide camera buttons during countdown
    const cameraButtons = document.getElementById('cameraButtons');
    if (cameraButtons) {
        cameraButtons.style.display = 'none';
    }
    
    console.log('🔄 Starting new countdown...');
    
    // Create countdown overlay that doesn't cover buttons
    const countdownOverlay = document.createElement('div');
    countdownOverlay.id = 'cameraCountdown';
    countdownOverlay.style.cssText = `
        position: fixed;
        inset: 0;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        z-index: 99999;
        pointer-events: none;
        background: rgba(0, 0, 0, 0.8);
    `;
    
    // Get photo label and instruction
    const photo = photoTypes.find(p => p.type === currentPhotoType);
    const photoLabel = photo ? photo.label : 'Foto';
    const photoInstruction = photo ? photo.instruction : '';
    
    countdownOverlay.innerHTML = `
        <div style="position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0, 0, 0, 0.7); z-index: -1;"></div>
        
        <!-- Text at top -->
        <div style="position: absolute; top: 50px; left: 0; right: 0; text-align: center; z-index: 10;">
            <h3 style="font-size: 22px; font-weight: 600; color: white; margin-bottom: 8px; text-shadow: 0 2px 8px rgba(0,0,0,0.5);">${photoLabel}</h3>
            <p style="font-size: 14px; font-weight: 400; color: white; opacity: 0.8; text-shadow: 0 2px 8px rgba(0,0,0,0.5);">${photoInstruction}</p>
        </div>
        
        <!-- Countdown circle in center -->
        <div style="text-align: center; position: relative; z-index: 10;">
            <svg width="160" height="160" viewBox="0 0 160 160" style="transform: rotate(-90deg);">
                <circle cx="80" cy="80" r="70" fill="none" stroke="rgba(255,255,255,0.15)" stroke-width="10"/>
                <circle id="countdownCircle" cx="80" cy="80" r="70" fill="none" stroke="#009cb6" stroke-width="10" 
                    stroke-dasharray="440" stroke-dashoffset="0" 
                    style="transition: stroke-dashoffset 1s linear;"/>
            </svg>
            <div id="countdownNumber" style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); font-size: 72px; font-weight: 800; color: white; text-shadow: 0 4px 12px rgba(0,0,0,0.5);">3</div>
        </div>
        
        <!-- Space for buttons at bottom (they will be visible underneath) -->
    `;
    
    document.body.appendChild(countdownOverlay);
    
    // Countdown animation
    let count = 3;
    const circle = document.getElementById('countdownCircle');
    const numberEl = document.getElementById('countdownNumber');
    const circumference = 440; // 2 * PI * 70
    
    window.countdownInterval = setInterval(() => {
        count--;
        const progress = count / 3;
        circle.style.strokeDashoffset = circumference * (1 - progress);
        
        if (count > 0) {
            numberEl.textContent = count;
        } else {
            clearInterval(window.countdownInterval);
            window.countdownInterval = null;
            window.countdownRunning = false; // Reset flag
            countdownOverlay.remove();
            // Show camera button after countdown
            const cameraButtons = document.getElementById('cameraButtons');
            if (cameraButtons) {
                cameraButtons.style.display = 'flex';
                console.log('📷 Camera buttons shown after countdown');
            }
            console.log('Countdown finished - ready to capture');
        }
    }, 1000);
}

let scene, camera3D, renderer, carModel, animationId;

function setupCameraOverlay(photoType) {
    // Clean camera view - no 3D overlay
    const overlayContainer = document.getElementById('cameraOverlay');
    if (overlayContainer) {
        overlayContainer.innerHTML = '';
    }
    return; // Exit early - no overlay needed
    
    const hints = {
        'front': 'Frente do veículo',
        'back': 'Traseira do veículo',
        'left': 'Lado esquerdo',
        'right': 'Lado direito',
        'interior': 'Interior do veículo',
        'odometer': 'Odómetro'
    };
    
    const isInteriorOrOdo = photoType === 'interior' || photoType === 'odometer';
    
    // Check if THREE.js is loaded
    if (typeof THREE === 'undefined') {
        console.error('THREE.js not loaded! Showing fallback.');
        overlayContainer.innerHTML = `
            <div style="position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.3); display: flex; flex-direction: column; align-items: center; justify-content: center;">
                <div style="text-align: center; color: white;">
                    <div style="display: inline-flex; align-items: center; gap: 10px; background: rgba(0,156,182,0.95); padding: 12px 24px; backdrop-filter: blur(10px);">
                        <svg style="width: 20px; height: 20px;" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                        </svg>
                        <span style="font-size: 16px; font-weight: 600;">${hints[photoType]}</span>
                    </div>
                </div>
            </div>
        `;
        return;
    }
    
    // Create container for 3D scene
    overlayContainer.innerHTML = `
        <div style="position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.3); display: flex; flex-direction: column; align-items: center; justify-content: center;">
            
            <!-- Three.js 3D Container -->
            <div id="threejs-container" style="width: 100%; height: 400px; margin-bottom: 40px;"></div>
            
            <!-- Direction hint with icon -->
            <div style="text-align: center; color: white;">
                <div style="display: flex; align-items: center; justify-content: center; gap: 12px; background: rgba(0,156,182,0.9); padding: 16px 32px; border-radius: 12px; box-shadow: 0 8px 24px rgba(0,0,0,0.4);">
                    <svg style="width: 32px; height: 32px;" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        ${isInteriorOrOdo ? 
                            '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"/>' :
                            '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"/>'
                        }
                    </svg>
                    <span style="font-size: 20px; font-weight: 700;">${hints[photoType]}</span>
                </div>
                <p style="margin-top: 16px; font-size: 14px; opacity: 0.9;">Posicione-se e alinhe o veículo</p>
            </div>
        </div>
    `;
    
    // Initialize Three.js 3D car
    setTimeout(() => init3DCar(photoType), 100);
}

let targetRotation = 0;
let currentRotation = 0;
let isRotating = false;

function init3DCar(photoType) {
    console.log('init3DCar called for:', photoType);
    
    const container = document.getElementById('threejs-container');
    console.log('Container found:', !!container);
    
    if (!container) {
        console.error('threejs-container not found!');
        return;
    }
    
    // Target rotation based on photo type
    const rotations = {
        'front': 0,
        'left': Math.PI / 2,
        'back': Math.PI,
        'right': -Math.PI / 2,
        'interior': 0,
        'odometer': 0
    };
    
    targetRotation = rotations[photoType] || 0;
    console.log('Target rotation:', targetRotation);
    
    // If scene already exists, just animate to new rotation
    if (renderer && carModel) {
        console.log('Reusing existing scene, animating to new rotation');
        isRotating = true;
        return;
    }
    
    console.log('Creating new Three.js scene...');
    
    // Create scene (first time only)
    scene = new THREE.Scene();
    
    // Create camera
    camera3D = new THREE.PerspectiveCamera(45, container.clientWidth / container.clientHeight, 0.1, 1000);
    camera3D.position.set(0, 3, 8);
    camera3D.lookAt(0, 0, 0);
    
    // Create renderer
    renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
    renderer.setSize(container.clientWidth, container.clientHeight);
    renderer.setClearColor(0x000000, 0);
    container.appendChild(renderer.domElement);
    
    // Add lights
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
    scene.add(ambientLight);
    
    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(5, 10, 5);
    scene.add(directionalLight);
    
    // Add point lights for more drama
    const pointLight1 = new THREE.PointLight(0xffffff, 0.5);
    pointLight1.position.set(-5, 3, 5);
    scene.add(pointLight1);
    
    const pointLight2 = new THREE.PointLight(0xffffff, 0.5);
    pointLight2.position.set(5, 3, -5);
    scene.add(pointLight2);
    
    try {
        // Create 3D car model
        console.log('Creating 3D car model...');
        carModel = create3DCarModel();
        scene.add(carModel);
        
        // Set initial rotation
        currentRotation = targetRotation;
        carModel.rotation.y = currentRotation;
        
        console.log('3D car created successfully!');
        console.log('Starting animation loop...');
        
        // Animate
        animate3DCar();
    } catch (error) {
        console.error('Error creating 3D car:', error);
        alert('Erro ao criar carro 3D: ' + error.message);
    }
}

function create3DCarModel() {
    const carGroup = new THREE.Group();
    
    // Car body (main)
    const bodyGeometry = new THREE.BoxGeometry(4, 1.2, 2);
    const bodyMaterial = new THREE.MeshPhongMaterial({ 
        color: 0x10b981,
        shininess: 100,
        specular: 0x444444
    });
    const body = new THREE.Mesh(bodyGeometry, bodyMaterial);
    body.position.y = 0.6;
    carGroup.add(body);
    
    // Car cabin (roof)
    const cabinGeometry = new THREE.BoxGeometry(2.5, 1, 1.8);
    const cabin = new THREE.Mesh(cabinGeometry, bodyMaterial);
    cabin.position.set(-0.3, 1.7, 0);
    carGroup.add(cabin);
    
    // Windows
    const windowMaterial = new THREE.MeshPhongMaterial({ 
        color: 0x64b5f6,
        transparent: true,
        opacity: 0.5,
        shininess: 100
    });
    
    // Front window
    const frontWindowGeometry = new THREE.BoxGeometry(0.1, 0.8, 1.6);
    const frontWindow = new THREE.Mesh(frontWindowGeometry, windowMaterial);
    frontWindow.position.set(0.95, 1.7, 0);
    carGroup.add(frontWindow);
    
    // Rear window
    const rearWindow = new THREE.Mesh(frontWindowGeometry, windowMaterial);
    rearWindow.position.set(-1.55, 1.7, 0);
    carGroup.add(rearWindow);
    
    // Wheels
    const wheelGeometry = new THREE.CylinderGeometry(0.4, 0.4, 0.3, 16);
    const wheelMaterial = new THREE.MeshPhongMaterial({ color: 0x1f2937 });
    
    // Front left wheel
    const wheel1 = new THREE.Mesh(wheelGeometry, wheelMaterial);
    wheel1.position.set(1.2, 0.4, 1.1);
    wheel1.rotation.z = Math.PI / 2;
    carGroup.add(wheel1);
    
    // Front right wheel
    const wheel2 = new THREE.Mesh(wheelGeometry, wheelMaterial);
    wheel2.position.set(1.2, 0.4, -1.1);
    wheel2.rotation.z = Math.PI / 2;
    carGroup.add(wheel2);
    
    // Rear left wheel
    const wheel3 = new THREE.Mesh(wheelGeometry, wheelMaterial);
    wheel3.position.set(-1.2, 0.4, 1.1);
    wheel3.rotation.z = Math.PI / 2;
    carGroup.add(wheel3);
    
    // Rear right wheel
    const wheel4 = new THREE.Mesh(wheelGeometry, wheelMaterial);
    wheel4.position.set(-1.2, 0.4, -1.1);
    wheel4.rotation.z = Math.PI / 2;
    carGroup.add(wheel4);
    
    // Headlights
    const headlightGeometry = new THREE.SphereGeometry(0.2, 16, 16);
    const headlightMaterial = new THREE.MeshPhongMaterial({ 
        color: 0xffffaa,
        emissive: 0xffff00,
        emissiveIntensity: 0.5
    });
    
    const headlight1 = new THREE.Mesh(headlightGeometry, headlightMaterial);
    headlight1.position.set(2.1, 0.8, 0.7);
    carGroup.add(headlight1);
    
    const headlight2 = new THREE.Mesh(headlightGeometry, headlightMaterial);
    headlight2.position.set(2.1, 0.8, -0.7);
    carGroup.add(headlight2);
    
    // Tail lights
    const taillightMaterial = new THREE.MeshPhongMaterial({ 
        color: 0xff0000,
        emissive: 0xff0000,
        emissiveIntensity: 0.3
    });
    
    const taillight1 = new THREE.Mesh(headlightGeometry, taillightMaterial);
    taillight1.position.set(-2.1, 0.8, 0.7);
    carGroup.add(taillight1);
    
    const taillight2 = new THREE.Mesh(headlightGeometry, taillightMaterial);
    taillight2.position.set(-2.1, 0.8, -0.7);
    carGroup.add(taillight2);
    
    return carGroup;
}

function animate3DCar() {
    animationId = requestAnimationFrame(animate3DCar);
    
    if (carModel) {
        // Smooth rotation to target angle
        if (isRotating || Math.abs(targetRotation - currentRotation) > 0.01) {
            // Calculate shortest rotation path
            let diff = targetRotation - currentRotation;
            
            // Normalize to -PI to PI range
            while (diff > Math.PI) diff -= Math.PI * 2;
            while (diff < -Math.PI) diff += Math.PI * 2;
            
            // Smooth easing (ease-out cubic)
            const rotationSpeed = diff * 0.08;
            currentRotation += rotationSpeed;
            
            // Stop rotating when close enough
            if (Math.abs(diff) < 0.01) {
                currentRotation = targetRotation;
                isRotating = false;
            }
            
            carModel.rotation.y = currentRotation;
        } else {
            // Slow idle rotation when not transitioning
            carModel.rotation.y += 0.003;
            currentRotation = carModel.rotation.y;
        }
    }
    
    renderer.render(scene, camera3D);
}


function getCarFrontSVG() {
    return `
        <g opacity="0.9" transform="scale(0.9)">
            <!-- Main car body outline -->
            <path d="M 200 100 L 200 280 Q 200 320 240 320 L 460 320 Q 500 320 500 280 L 500 100 Q 500 80 480 80 L 220 80 Q 200 80 200 100 Z" 
                  fill="none" stroke="#10b981" stroke-width="4" stroke-dasharray="12,8"/>
            
            <!-- Hood -->
            <path d="M 230 110 L 230 160 L 470 160 L 470 110 Q 470 100 460 100 L 240 100 Q 230 100 230 110 Z" 
                  fill="none" stroke="#10b981" stroke-width="2.5"/>
            
            <!-- Headlights (detailed) -->
            <g>
                <path d="M 240 120 Q 250 120 255 125 L 255 145 Q 255 150 250 150 L 240 150 Q 235 150 235 145 L 235 125 Q 235 120 240 120 Z" 
                      fill="none" stroke="#10b981" stroke-width="2"/>
                <circle cx="247" cy="135" r="8" fill="none" stroke="#10b981" stroke-width="1.5"/>
                
                <path d="M 460 120 Q 450 120 445 125 L 445 145 Q 445 150 450 150 L 460 150 Q 465 150 465 145 L 465 125 Q 465 120 460 120 Z" 
                      fill="none" stroke="#10b981" stroke-width="2"/>
                <circle cx="453" cy="135" r="8" fill="none" stroke="#10b981" stroke-width="1.5"/>
            </g>
            
            <!-- Grille (detailed) -->
            <rect x="310" y="125" width="80" height="40" rx="4" fill="none" stroke="#10b981" stroke-width="2.5"/>
            <line x1="320" y1="135" x2="380" y2="135" stroke="#10b981" stroke-width="1"/>
            <line x1="320" y1="145" x2="380" y2="145" stroke="#10b981" stroke-width="1"/>
            <line x1="320" y1="155" x2="380" y2="155" stroke="#10b981" stroke-width="1"/>
            
            <!-- Windshield -->
            <path d="M 240 170 L 250 190 Q 250 195 255 195 L 445 195 Q 450 195 450 190 L 460 170" 
                  fill="none" stroke="#10b981" stroke-width="2.5"/>
            
            <!-- Roof line -->
            <path d="M 250 200 L 255 220 L 445 220 L 450 200" fill="none" stroke="#10b981" stroke-width="2"/>
            
            <!-- Side mirrors -->
            <ellipse cx="215" cy="210" rx="10" ry="15" fill="none" stroke="#10b981" stroke-width="2"/>
            <ellipse cx="485" cy="210" rx="10" ry="15" fill="none" stroke="#10b981" stroke-width="2"/>
            
            <!-- Front bumper -->
            <path d="M 220 290 L 210 305 L 490 305 L 480 290" fill="none" stroke="#10b981" stroke-width="2.5"/>
            
            <!-- License plate (highlighted) -->
            <rect x="310" y="285" width="80" height="25" rx="3" fill="rgba(245, 158, 11, 0.1)" stroke="#f59e0b" stroke-width="3"/>
            <text x="350" y="302" text-anchor="middle" fill="#f59e0b" font-size="11" font-weight="bold">XX-XX-XX</text>
            
            <!-- Wheel wells -->
            <ellipse cx="260" cy="310" rx="35" ry="20" fill="none" stroke="#10b981" stroke-width="2"/>
            <ellipse cx="440" cy="310" rx="35" ry="20" fill="none" stroke="#10b981" stroke-width="2"/>
        </g>
    `;
}

function getCarBackSVG() {
    return `
        <g opacity="0.9" transform="scale(0.9)">
            <!-- Main car body outline -->
            <path d="M 200 100 L 200 280 Q 200 320 240 320 L 460 320 Q 500 320 500 280 L 500 100 Q 500 80 480 80 L 220 80 Q 200 80 200 100 Z" 
                  fill="none" stroke="#10b981" stroke-width="4" stroke-dasharray="12,8"/>
            
            <!-- Roof line -->
            <path d="M 250 100 L 255 120 L 445 120 L 450 100" fill="none" stroke="#10b981" stroke-width="2"/>
            
            <!-- Rear window -->
            <path d="M 240 130 L 250 150 Q 250 155 255 155 L 445 155 Q 450 155 450 150 L 460 130" 
                  fill="none" stroke="#10b981" stroke-width="2.5"/>
            
            <!-- Trunk/Boot -->
            <path d="M 230 165 L 230 270 L 470 270 L 470 165" fill="none" stroke="#10b981" stroke-width="2.5"/>
            <line x1="240" y1="180" x2="460" y2="180" stroke="#10b981" stroke-width="1.5"/>
            
            <!-- Tail lights (detailed) -->
            <g>
                <!-- Left tail light -->
                <rect x="235" y="245" width="45" height="50" rx="4" fill="rgba(239, 68, 68, 0.1)" stroke="#ef4444" stroke-width="2.5"/>
                <rect x="240" y="250" width="35" height="18" rx="2" fill="none" stroke="#ef4444" stroke-width="1.5"/>
                <rect x="240" y="272" width="35" height="18" rx="2" fill="none" stroke="#ef4444" stroke-width="1.5"/>
                
                <!-- Right tail light -->
                <rect x="420" y="245" width="45" height="50" rx="4" fill="rgba(239, 68, 68, 0.1)" stroke="#ef4444" stroke-width="2.5"/>
                <rect x="425" y="250" width="35" height="18" rx="2" fill="none" stroke="#ef4444" stroke-width="1.5"/>
                <rect x="425" y="272" width="35" height="18" rx="2" fill="none" stroke="#ef4444" stroke-width="1.5"/>
            </g>
            
            <!-- License plate (highlighted) -->
            <rect x="310" y="255" width="80" height="28" rx="3" fill="rgba(245, 158, 11, 0.1)" stroke="#f59e0b" stroke-width="3"/>
            <text x="350" y="274" text-anchor="middle" fill="#f59e0b" font-size="11" font-weight="bold">XX-XX-XX</text>
            
            <!-- Side mirrors -->
            <ellipse cx="215" cy="160" rx="10" ry="15" fill="none" stroke="#10b981" stroke-width="2"/>
            <ellipse cx="485" cy="160" rx="10" ry="15" fill="none" stroke="#10b981" stroke-width="2"/>
            
            <!-- Rear bumper -->
            <path d="M 220 300 L 210 315 L 490 315 L 480 300" fill="none" stroke="#10b981" stroke-width="2.5"/>
            
            <!-- Wheel wells -->
            <ellipse cx="260" cy="310" rx="35" ry="20" fill="none" stroke="#10b981" stroke-width="2"/>
            <ellipse cx="440" cy="310" rx="35" ry="20" fill="none" stroke="#10b981" stroke-width="2"/>
            
            <!-- Exhaust -->
            <ellipse cx="420" cy="313" rx="8" ry="5" fill="none" stroke="#10b981" stroke-width="1.5"/>
        </g>
    `;
}

function getCarSideSVG() {
    return `
        <g opacity="0.9" transform="scale(0.85)">
            <!-- Main body outline -->
            <path d="M 120 240 L 120 200 Q 120 190 130 185 L 160 180 L 180 150 Q 185 140 195 135 L 250 120 L 450 120 Q 460 120 465 130 L 485 155 L 515 165 Q 525 170 525 180 L 550 185 Q 560 190 560 200 L 560 240 Q 560 255 550 260 L 530 265 L 150 265 Q 130 260 120 250 Z" 
                  fill="none" stroke="#10b981" stroke-width="4" stroke-dasharray="12,8"/>
            
            <!-- Roof line -->
            <path d="M 190 140 L 250 125 L 450 125 L 470 140" fill="none" stroke="#10b981" stroke-width="2.5"/>
            
            <!-- Windows -->
            <g>
                <!-- Front window -->
                <path d="M 195 145 L 205 135 L 265 130 L 275 145 L 270 175 L 200 175 Z" 
                      fill="none" stroke="#10b981" stroke-width="2"/>
                
                <!-- Rear window -->
                <path d="M 425 145 L 445 130 L 465 135 L 475 145 L 470 175 L 430 175 Z" 
                      fill="none" stroke="#10b981" stroke-width="2"/>
            </g>
            
            <!-- Door lines -->
            <g>
                <!-- Front door -->
                <path d="M 280 150 L 280 250" stroke="#10b981" stroke-width="2.5"/>
                <ellipse cx="290" cy="200" rx="5" ry="8" fill="none" stroke="#10b981" stroke-width="1.5"/>
                
                <!-- Rear door -->
                <path d="M 420 150 L 420 250" stroke="#10b981" stroke-width="2.5"/>
                <ellipse cx="410" cy="200" rx="5" ry="8" fill="none" stroke="#10b981" stroke-width="1.5"/>
            </g>
            
            <!-- Side skirts -->
            <path d="M 150 260 L 145 265 L 535 265 L 530 260" fill="none" stroke="#10b981" stroke-width="2"/>
            
            <!-- Wheels (detailed) -->
            <g>
                <!-- Front wheel -->
                <circle cx="210" cy="275" r="42" fill="none" stroke="#10b981" stroke-width="3"/>
                <circle cx="210" cy="275" r="28" fill="none" stroke="#10b981" stroke-width="2.5"/>
                <circle cx="210" cy="275" r="15" fill="none" stroke="#10b981" stroke-width="2"/>
                <!-- Spokes -->
                <line x1="210" y1="260" x2="210" y2="290" stroke="#10b981" stroke-width="1.5"/>
                <line x1="195" y1="275" x2="225" y2="275" stroke="#10b981" stroke-width="1.5"/>
                
                <!-- Rear wheel -->
                <circle cx="470" cy="275" r="42" fill="none" stroke="#10b981" stroke-width="3"/>
                <circle cx="470" cy="275" r="28" fill="none" stroke="#10b981" stroke-width="2.5"/>
                <circle cx="470" cy="275" r="15" fill="none" stroke="#10b981" stroke-width="2"/>
                <!-- Spokes -->
                <line x1="470" y1="260" x2="470" y2="290" stroke="#10b981" stroke-width="1.5"/>
                <line x1="455" y1="275" x2="485" y2="275" stroke="#10b981" stroke-width="1.5"/>
            </g>
            
            <!-- Bumpers -->
            <g>
                <!-- Front bumper -->
                <path d="M 115 230 L 110 235 L 110 255 L 115 260" fill="none" stroke="#10b981" stroke-width="2.5"/>
                
                <!-- Rear bumper -->
                <path d="M 565 230 L 570 235 L 570 255 L 565 260" fill="none" stroke="#10b981" stroke-width="2.5"/>
            </g>
            
            <!-- Side mirror -->
            <ellipse cx="185" cy="175" rx="15" ry="10" fill="none" stroke="#10b981" stroke-width="2"/>
            
            <!-- Headlight & taillight indicators -->
            <ellipse cx="125" cy="220" rx="8" ry="12" fill="none" stroke="#10b981" stroke-width="1.5"/>
            <rect x="545" y="215" width="15" height="25" rx="2" fill="rgba(239, 68, 68, 0.1)" stroke="#ef4444" stroke-width="2"/>
        </g>
    `;
}

function getInteriorSVG() {
    return `
        <g opacity="0.9" transform="scale(0.9)">
            <!-- Main interior frame -->
            <rect x="180" y="80" width="340" height="260" rx="12" fill="none" stroke="#10b981" stroke-width="4" stroke-dasharray="12,8"/>
            
            <!-- Dashboard (detailed) -->
            <path d="M 200 120 L 200 180 Q 200 190 210 190 L 490 190 Q 500 190 500 180 L 500 120 Q 500 110 490 110 L 210 110 Q 200 110 200 120 Z" 
                  fill="none" stroke="#10b981" stroke-width="2.5"/>
            
            <!-- Instrument cluster -->
            <g>
                <circle cx="350" cy="145" r="28" fill="none" stroke="#10b981" stroke-width="2"/>
                <circle cx="350" cy="145" r="20" fill="none" stroke="#10b981" stroke-width="1.5"/>
                <text x="350" y="152" text-anchor="middle" fill="#10b981" font-size="14" font-weight="bold">km/h</text>
            </g>
            
            <!-- Center console -->
            <rect x="290" y="195" width="120" height="35" rx="4" fill="none" stroke="#10b981" stroke-width="2"/>
            <circle cx="325" cy="212" r="8" fill="none" stroke="#10b981" stroke-width="1.5"/>
            <circle cx="350" cy="212" r="8" fill="none" stroke="#10b981" stroke-width="1.5"/>
            <circle cx="375" cy="212" r="8" fill="none" stroke="#10b981" stroke-width="1.5"/>
            
            <!-- Steering wheel (detailed) -->
            <g>
                <circle cx="260" cy="160" r="32" fill="none" stroke="#10b981" stroke-width="3"/>
                <circle cx="260" cy="160" r="22" fill="none" stroke="#10b981" stroke-width="2.5"/>
                <circle cx="260" cy="160" r="10" fill="none" stroke="#10b981" stroke-width="2"/>
                <line x1="240" y1="160" x2="228" y2="160" stroke="#10b981" stroke-width="2.5"/>
                <line x1="280" y1="160" x2="292" y2="160" stroke="#10b981" stroke-width="2.5"/>
            </g>
            
            <!-- Front seats (detailed) -->
            <g>
                <!-- Driver seat -->
                <path d="M 220 240 L 220 260 Q 220 270 230 270 L 270 270 Q 280 270 280 260 L 280 240 Q 280 235 275 235 L 225 235 Q 220 235 220 240 Z" 
                      fill="none" stroke="#10b981" stroke-width="2.5"/>
                <path d="M 225 235 L 225 210 Q 225 200 235 200 L 265 200 Q 275 200 275 210 L 275 235" 
                      fill="none" stroke="#10b981" stroke-width="2"/>
                
                <!-- Passenger seat -->
                <path d="M 420 240 L 420 260 Q 420 270 430 270 L 470 270 Q 480 270 480 260 L 480 240 Q 480 235 475 235 L 425 235 Q 420 235 420 240 Z" 
                      fill="none" stroke="#10b981" stroke-width="2.5"/>
                <path d="M 425 235 L 425 210 Q 425 200 435 200 L 465 200 Q 475 200 475 210 L 475 235" 
                      fill="none" stroke="#10b981" stroke-width="2"/>
            </g>
            
            <!-- Gear shift -->
            <ellipse cx="320" cy="245" rx="12" ry="20" fill="none" stroke="#10b981" stroke-width="2"/>
        </g>
    `;
}

function getOdometerSVG() {
    return `
        <g opacity="0.9" transform="scale(0.95)">
            <!-- Instrument cluster frame -->
            <rect x="220" y="130" width="260" height="140" rx="12" fill="none" stroke="#10b981" stroke-width="4" stroke-dasharray="12,8"/>
            
            <!-- Main display background -->
            <rect x="240" y="150" width="220" height="100" rx="8" fill="rgba(16, 185, 129, 0.05)" stroke="#10b981" stroke-width="2.5"/>
            
            <!-- Digital display -->
            <g>
                <rect x="255" y="165" width="190" height="50" rx="6" fill="rgba(0, 0, 0, 0.1)" stroke="#10b981" stroke-width="2"/>
                
                <!-- Digital numbers (7-segment style) -->
                <text x="350" y="200" text-anchor="middle" fill="#10b981" font-size="32" font-family="monospace" font-weight="bold" letter-spacing="4">123456</text>
            </g>
            
            <!-- KM label -->
            <rect x="320" y="220" width="60" height="22" rx="4" fill="none" stroke="#10b981" stroke-width="1.5"/>
            <text x="350" y="236" text-anchor="middle" fill="#10b981" font-size="14" font-weight="bold">km</text>
            
            <!-- Side indicators -->
            <g>
                <!-- Fuel indicator -->
                <circle cx="260" cy="185" r="8" fill="none" stroke="#10b981" stroke-width="1.5"/>
                <text x="260" y="190" text-anchor="middle" fill="#10b981" font-size="10" font-weight="bold">F</text>
                
                <!-- Temperature indicator -->
                <circle cx="440" cy="185" r="8" fill="none" stroke="#10b981" stroke-width="1.5"/>
                <text x="440" y="190" text-anchor="middle" fill="#10b981" font-size="10" font-weight="bold">T</text>
            </g>
            
            <!-- Border detail lines -->
            <line x1="250" y1="220" x2="310" y2="220" stroke="#10b981" stroke-width="1"/>
            <line x1="390" y1="220" x2="450" y2="220" stroke="#10b981" stroke-width="1"/>
        </g>
    `;
}

let hintInterval;
const hints = [
    'Mova para cima',
    'Mova para baixo',
    'Mova para a esquerda',
    'Mova para a direita',
    'Ajuste o ângulo',
    'Afaste-se um pouco',
    'Aproxime-se mais',
    'Posicionamento correto'
];

function startPositioningHints(photoType) {
    // Clear previous interval
    if (hintInterval) clearInterval(hintInterval);
    
    // Change hints every 3 seconds to simulate positioning feedback
    hintInterval = setInterval(() => {
        const hintText = document.getElementById('hintText');
        if (!hintText) {
            clearInterval(hintInterval);
            return;
        }
        
        changeCount++;
        
        // After a few changes, show "perfect" hint
        if (changeCount > 3) {
            hintText.innerHTML = 'Posicionamento correto - Pode tirar a foto';
            hintText.style.background = 'rgba(16, 185, 129, 0.9)'; // Green
            clearInterval(hintInterval);
            return;
        }
        
        // Show random positioning hint
        const randomHint = hints[Math.floor(Math.random() * (hints.length - 1))];
        hintText.innerHTML = randomHint;
        hintText.style.background = 'rgba(0, 0, 0, 0.7)'; // Dark
        
    }, 3000);
}

let changeCount = 0;

// OCR License Plate Detection
async function detectLicensePlate(blob) {
    console.log('🔍 Detectando matrícula com OCR...');
    
    // Check if license plate field is already filled
    const plateField = document.getElementById('inputPlate');
    if (plateField && plateField.value.trim()) {
        console.log('Matrícula já preenchida, saltando OCR');
        return;
    }
    
    showNotification('🔍 A detectar matrícula...', 'info');
    
    try {
        // Convert blob to image URL
        const imageUrl = URL.createObjectURL(blob);
        
        // Process with Tesseract OCR
        const result = await Tesseract.recognize(
            imageUrl,
            'eng', // English works better for alphanumeric
            {
                logger: info => {
                    if (info.status === 'recognizing text') {
                        console.log(`OCR Progress: ${Math.round(info.progress * 100)}%`);
                    }
                }
            }
        );
        
        console.log('OCR Text detected:', result.data.text);
        
        // Extract license plate pattern
        // Portuguese format: XX-XX-XX or XX-00-XX or 00-XX-00
        const text = result.data.text.toUpperCase();
        
        // Try multiple patterns
        const patterns = [
            /([A-Z0-9]{2}[-\s]?[A-Z0-9]{2}[-\s]?[A-Z0-9]{2})/g,  // XX-XX-XX
            /([A-Z]{2}[-\s]?\d{2}[-\s]?[A-Z]{2})/g,              // AA-00-AA
            /(\d{2}[-\s]?[A-Z]{2}[-\s]?\d{2})/g,                // 00-AA-00
            /([A-Z]{2}[-\s]?\d{2}[-\s]?\d{2})/g,                // AA-00-00
        ];
        
        let detectedPlate = null;
        for (const pattern of patterns) {
            const matches = text.match(pattern);
            if (matches && matches.length > 0) {
                // Get the match and format it
                detectedPlate = matches[0].replace(/\s+/g, '-');
                // Ensure format XX-XX-XX
                if (detectedPlate.length >= 6 && detectedPlate.length <= 10) {
                    break;
                }
            }
        }
        
        if (detectedPlate) {
            // Format properly: XX-XX-XX
            detectedPlate = detectedPlate.replace(/[^A-Z0-9]/g, '');
            if (detectedPlate.length >= 6) {
                const formatted = `${detectedPlate.slice(0,2)}-${detectedPlate.slice(2,4)}-${detectedPlate.slice(4,6)}`;
                
                // Fill the field
                if (plateField) {
                    plateField.value = formatted;
                    plateField.style.background = '#fef3c7'; // Highlight yellow
                    setTimeout(() => {
                        plateField.style.background = '';
                    }, 2000);
                }
                
                showNotification(`✅ Matrícula detectada: ${formatted}`, 'success');
                console.log('✅ License plate detected:', formatted);
            } else {
                throw new Error('Formato inválido');
            }
        } else {
            throw new Error('Matrícula não encontrada');
        }
        
        // Clean up
        URL.revokeObjectURL(imageUrl);
        
    } catch (error) {
        console.warn('OCR failed:', error);
        showNotification('⚠️ Não foi possível detectar a matrícula automaticamente. Por favor, insira manualmente.', 'warning');
    }
}

function closeCamera(keepStream = false) {
    // Stop camera stream only if not keeping it for next photo
    if (cameraStream && !keepStream) {
        cameraStream.getTracks().forEach(track => track.stop());
        cameraStream = null;
        window.savedCameraStream = null;
        window.pendingCameraStream = null;
    }
    
    // Clear camera preview only if not keeping stream
    const video = document.getElementById('cameraPreview');
    if (video && !keepStream) {
        video.srcObject = null;
    }
    
    // Hide car miniature
    const miniature = document.getElementById('carMiniature');
    if (miniature) {
        miniature.style.display = 'none';
    }
    
    // Exit fullscreen only if not keeping stream
    if (!keepStream) {
        try {
            if (document.fullscreenElement) {
                if (document.exitFullscreen) {
                    document.exitFullscreen();
                } else if (document.webkitExitFullscreen) {
                    document.webkitExitFullscreen();
                } else if (document.msExitFullscreen) {
                    document.msExitFullscreen();
                }
                console.log('✅ Fullscreen exited');
            }
        } catch (error) {
            console.log('⚠️ Could not exit fullscreen:', error.message);
        }
        
        // Hide modal only if not keeping stream
        document.getElementById('cameraModal').classList.remove('active');
    }
}

// Functions for new button layout
function retakePhoto() {
    // Remove preview if exists
    const preview = document.getElementById('photoPreviewContainer');
    if (preview) preview.remove();
    
    // Show camera again
    document.getElementById('cameraPreview').style.display = 'block';
    document.getElementById('cameraOverlay').style.display = 'block';
    
    // Restart countdown
    startCameraCountdown();
}

function acceptPhoto() {
    // Save the photo
    if (window.tempPhotoBlob && currentPhotoType) {
        savePhotoToInspection(window.tempPhotoBlob, currentPhotoType);
    }
}

function capturePhoto() {
    const video = document.getElementById('cameraPreview');
    
    // Validate video is ready
    if (!video || !video.videoWidth || !video.videoHeight) {
        alert('Câmera ainda não está pronta. Aguarde um momento.');
        console.error('Video not ready:', video);
        return;
    }
    
    if (!currentPhotoType) {
        alert('Erro: Tipo de foto não definido.');
        console.error('currentPhotoType is null');
        return;
    }
    
    console.log('Capturing photo:', currentPhotoType, `${video.videoWidth}x${video.videoHeight}`);
    
    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    
    const ctx = canvas.getContext('2d');
    // Mirror image back for display
    ctx.translate(canvas.width, 0);
    ctx.scale(-1, 1);
    ctx.drawImage(video, 0, 0);
    
    console.log('Canvas created, converting to blob...');
    
    // Convert to blob
    canvas.toBlob(blob => {
        if (!blob) {
            alert('Erro ao criar imagem. Tente novamente.');
            console.error('Blob creation failed');
            return;
        }
        
        console.log('Photo blob created:', blob.size, 'bytes');
        
        // Check if this is a pickup damage photo
        if (window.isPickupDamagePhoto) {
            // Save as pickup damage photo
            savePickupDamagePhoto(blob, currentPhotoType);
            // Reset flag
            window.isPickupDamagePhoto = false;
            // Close camera
            closeCamera();
        } else {
            // Show preview with options (normal checkout flow)
            showPhotoPreview(blob, currentPhotoType);
        }
        
    }, 'image/jpeg', 0.9);
}

// Save pickup damage photo
function savePickupDamagePhoto(blob, photoType) {
    if (!window.pickupDamagePhotos) {
        window.pickupDamagePhotos = [];
    }
    
    // Convert blob to base64
    const reader = new FileReader();
    reader.onloadend = function() {
        const base64data = reader.result;
        
        window.pickupDamagePhotos.push({
            type: photoType,
            side: window.currentDamageSide,
            data: base64data,
            timestamp: new Date().toISOString()
        });
        
        console.log('✅ Pickup damage photo saved:', photoType, window.pickupDamagePhotos.length, 'photos total');
        showNotification(`Foto de dano guardada: ${formatPhotoType(photoType)}`, 'success');
        
        // Update photo grid
        updatePickupDamagePhotosGrid();
        
        // Continue with next damage side if needed
        continuePickupDamageFlow();
    };
    reader.readAsDataURL(blob);
}

function showPhotoPreview(blob, photoType) {
    // Hide camera video
    document.getElementById('cameraPreview').style.display = 'none';
    document.getElementById('cameraOverlay').style.display = 'none';
    
    // Create preview overlay
    const cameraModal = document.getElementById('cameraModal');
    const previewContainer = document.createElement('div');
    previewContainer.id = 'photoPreviewContainer';
    previewContainer.style.cssText = `
        position: absolute;
        inset: 0;
        background: rgba(0,0,0,0.95);
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        z-index: 10001;
    `;
    
    const photoLabel = photoTypes.find(p => p.type === photoType).label;
    
    previewContainer.innerHTML = `
        <div style="text-align: center; color: white; margin-bottom: 20px;">
            <h3 style="font-size: 24px; font-weight: 600;">${photoLabel}</h3>
            <p style="font-size: 14px; opacity: 0.8; margin-top: 8px;">Verifique a qualidade da foto</p>
        </div>
        
        <div style="position: relative; max-width: 90%; max-height: 60vh;">
            <img src="${URL.createObjectURL(blob)}" style="max-width: 100%; max-height: 60vh; border-radius: 12px; box-shadow: 0 8px 32px rgba(0,0,0,0.5);">
        </div>
        
        <div style="display: flex; gap: 16px; margin-top: 32px;">
            <button id="btnRetake" onclick="window.retakePhotoAction()" style="display: flex; align-items: center; gap: 8px; background: #009cb6; color: white; padding: 14px 28px; border-radius: 8px; border: none; font-size: 16px; font-weight: 600; cursor: pointer; transition: all 0.2s; box-shadow: 0 4px 12px rgba(0,0,0,0.3);">
                <svg style="width: 20px; height: 20px;" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
                </svg>
                Repetir
            </button>
            <button id="btnAccept" onclick="window.acceptPhotoAction()" style="display: flex; align-items: center; gap: 8px; background: #f59e0b; color: white; padding: 14px 28px; border-radius: 8px; border: none; font-size: 16px; font-weight: 600; cursor: pointer; transition: all 0.2s; box-shadow: 0 4px 12px rgba(0,0,0,0.3);">
                <svg style="width: 20px; height: 20px;" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
                </svg>
                Próxima
            </button>
        </div>
    `;
    
    cameraModal.querySelector('.flex').appendChild(previewContainer);
    
    // Store blob temporarily and photo type
    window.tempPhotoBlob = blob;
    window.tempPhotoType = photoType;
    
    // Create global functions for onclick handlers
    window.retakePhotoAction = function() {
        console.log('Retake button clicked via onclick!');
        retakePhoto();
    };
    
    window.acceptPhotoAction = function() {
        console.log('Accept button clicked via onclick! PhotoType:', photoType);
        acceptPhoto(photoType);
    };
}

function retakePhoto() {
    // Remove preview
    const preview = document.getElementById('photoPreviewContainer');
    if (preview) preview.remove();
    
    // Show camera again
    const video = document.getElementById('cameraPreview');
    video.style.display = 'block';
    
    // Restart camera stream if not active
    if (!video.srcObject || !video.srcObject.active) {
        navigator.mediaDevices.getUserMedia({
            video: {
                facingMode: 'environment',
                width: { ideal: 1920 },
                height: { ideal: 1080 }
            }
        }).then(stream => {
            video.srcObject = stream;
            video.play();
        }).catch(err => {
            console.error('Error restarting camera:', err);
            showNotification('Erro ao reiniciar a câmera', 'error');
        });
    }
    
    // Show overlay
    document.getElementById('cameraOverlay').style.display = 'block';
    
    // Clear temp blob
    window.tempPhotoBlob = null;
}

function showSavingAnimation() {
    // Create saving overlay
    const savingOverlay = document.createElement('div');
    savingOverlay.id = 'savingOverlay';
    savingOverlay.style.cssText = `
        position: fixed;
        inset: 0;
        background: rgba(0, 156, 182, 0.95);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 10001;
        animation: fadeIn 0.2s ease-in;
    `;
    
    savingOverlay.innerHTML = `
        <div style="text-align: center; color: white;">
            <svg style="width: 64px; height: 64px; margin: 0 auto 20px; animation: spin 1s linear infinite;" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
            </svg>
            <h3 style="font-size: 24px; font-weight: 600; margin: 0;">A guardar foto...</h3>
        </div>
        <style>
            @keyframes fadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
            }
            @keyframes spin {
                from { transform: rotate(0deg); }
                to { transform: rotate(360deg); }
            }
        </style>
    `;
    
    document.body.appendChild(savingOverlay);
    
    // Remove after 2.5 seconds (longer delay)
    setTimeout(() => {
        savingOverlay.style.animation = 'fadeOut 0.3s ease-out';
        setTimeout(() => savingOverlay.remove(), 300);
    }, 2500);
}

function showFinalPhotoCompletionMessage() {
    const completionOverlay = document.createElement('div');
    completionOverlay.id = 'finalPhotoCompletion';
    completionOverlay.innerHTML = `
        <div style="
            position: fixed;
            inset: 0;
            background: linear-gradient(135deg, #10b981, #059669);
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            z-index: 99999;
            color: white;
            text-align: center;
            animation: slideIn 0.5s ease-out;
        ">
            <div style="
                background: rgba(255, 255, 255, 0.1);
                padding: 40px;
                border-radius: 20px;
                backdrop-filter: blur(10px);
                border: 2px solid rgba(255, 255, 255, 0.2);
                max-width: 500px;
                margin: 20px;
            ">
                <div style="
                    width: 80px;
                    height: 80px;
                    background: white;
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    margin: 0 auto 20px;
                    animation: checkmark 0.8s ease-out 0.3s both;
                ">
                    <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="3">
                        <polyline points="20,6 9,17 4,12"></polyline>
                    </svg>
                </div>
                <h2 style="
                    font-size: 28px;
                    font-weight: bold;
                    margin: 0 0 15px;
                    animation: fadeInUp 0.6s ease-out 0.5s both, pulse 2s ease-in-out 1s infinite;
                ">INSPEÇÃO FOTOGRÁFICA TERMINADA</h2>
                <p style="
                    font-size: 18px;
                    margin: 0 0 20px;
                    opacity: 0.9;
                    animation: fadeInUp 0.6s ease-out 0.7s both;
                ">6 fotos processadas com sucesso</p>
                <div style="
                    background: rgba(255, 255, 255, 0.2);
                    padding: 15px;
                    border-radius: 10px;
                    font-size: 16px;
                    animation: fadeInUp 0.6s ease-out 0.9s both;
                ">
                    Prosseguindo para marcação de danos...
                </div>
            </div>
        </div>
        <style>
            @keyframes slideIn {
                from { transform: translateY(-100%); opacity: 0; }
                to { transform: translateY(0); opacity: 1; }
            }
            @keyframes fadeInUp {
                from { transform: translateY(20px); opacity: 0; }
                to { transform: translateY(0); opacity: 1; }
            }
            @keyframes checkmark {
                0% { transform: scale(0) rotate(-45deg); opacity: 0; }
                50% { transform: scale(1.2) rotate(0deg); opacity: 1; }
                100% { transform: scale(1) rotate(0deg); opacity: 1; }
            }
            @keyframes pulse {
                0%, 100% { transform: scale(1); }
                50% { transform: scale(1.05); }
            }
        </style>
    `;
    
    document.body.appendChild(completionOverlay);
    
    // Remove after 3 seconds
    setTimeout(() => {
        completionOverlay.style.animation = 'slideIn 0.5s ease-out reverse';
        setTimeout(() => completionOverlay.remove(), 500);
    }, 3000);
}

function acceptPhoto(photoType) {
    // Check if override function exists (from template HTML)
    if (typeof window.acceptPhotoOverride === 'function') {
        console.log('🔄 Using acceptPhotoOverride from template');
        return window.acceptPhotoOverride(photoType);
    }
    
    console.log('🔵 acceptPhoto called for:', photoType);
    console.log('🔵 window.tempPhotoBlob:', window.tempPhotoBlob);
    const blob = window.tempPhotoBlob;
    
    if (!blob) {
        alert('Erro: Foto não encontrada');
        console.error('❌ No blob found in window.tempPhotoBlob');
        return;
    }
    
    console.log('🔵 Blob size:', blob.size, 'bytes');
    console.log('🔵 Blob type:', blob.type);
    
    // Show blue processing window between photos
    showPhotoProcessingWindow(photoType);
    
    // Convert Blob to dataURL (base64) before storing
    console.log('🔵 Starting FileReader conversion...');
    const reader = new FileReader();
    
    reader.onerror = function(error) {
        console.error('❌ FileReader error:', error);
        alert('Erro ao processar foto. Tente novamente.');
    };
    
    reader.onloadend = function() {
        const dataURL = reader.result;
        console.log(`✅ Photo ${photoType} converted to dataURL:`, dataURL.substring(0, 50) + '...');
        console.log(`✅ DataURL length:`, dataURL.length);
        
        // Store photo with dataURL immediately (no delay)
        console.log('💾 Calling savePhotoData...');
        savePhotoData(photoType, dataURL, blob);
        
        // Continue processing after a short delay
        setTimeout(() => {
            console.log('▶️ Continuing photo processing...');
            continuePhotoProcessing(photoType, blob);
        }, 1000);
    };
    
    console.log('🔵 Calling reader.readAsDataURL...');
    reader.readAsDataURL(blob);
}

function showPhotoProcessingWindow(photoType) {
    const photoLabel = photoTypes.find(p => p.type === photoType)?.label || 'Foto';
    
    const processingOverlay = document.createElement('div');
    processingOverlay.id = 'photoProcessingOverlay';
    processingOverlay.innerHTML = `
        <div style="
            position: fixed;
            inset: 0;
            background: linear-gradient(135deg, #009cb6, #007a8f);
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            z-index: 99999;
            color: white;
            text-align: center;
        ">
            <div style="
                background: rgba(255, 255, 255, 0.1);
                padding: 40px;
                border-radius: 20px;
                backdrop-filter: blur(10px);
                border: 2px solid rgba(255, 255, 255, 0.2);
                max-width: 500px;
                margin: 20px;
            ">
                <div style="
                    width: 60px;
                    height: 60px;
                    border: 4px solid rgba(255, 255, 255, 0.3);
                    border-top: 4px solid white;
                    border-radius: 50%;
                    margin: 0 auto 25px;
                    animation: spin 1s linear infinite;
                "></div>
                <h2 style="
                    font-size: 24px;
                    font-weight: bold;
                    margin: 0 0 15px;
                ">PROCESSANDO FOTO</h2>
                <p style="
                    font-size: 18px;
                    margin: 0 0 20px;
                    opacity: 0.9;
                ">${photoLabel}</p>
                <p style="
                    font-size: 16px;
                    margin: 0;
                    opacity: 0.8;
                ">
                    ✓ Foto capturada com sucesso
                </p>
            </div>
        </div>
        <style>
            @keyframes spin {
                from { transform: rotate(0deg); }
                to { transform: rotate(360deg); }
            }
        </style>
    `;
    
    document.body.appendChild(processingOverlay);
    
    // Remove after 2 seconds
    setTimeout(() => {
        processingOverlay.remove();
    }, 2000);
}

function continuePhotoProcessing(photoType, blob) {
    // Update UI
    const slot = document.getElementById(`slot-${photoType}`);
    if (slot) {
        slot.innerHTML = `<img src="${URL.createObjectURL(blob)}" alt="${photoType}">`;
        slot.classList.add('captured');
        
        // Show animation
        slot.classList.add('shutter-animation');
        setTimeout(() => slot.classList.remove('shutter-animation'), 300);
    }
    
    // Update check icon if exists
    const checkIcon = document.getElementById(`check-${photoType}`);
    if (checkIcon) {
        checkIcon.classList.remove('hidden');
    }
    
    // Update diagram indicator if function exists
    if (typeof updateDiagramIndicator === 'function') {
        updateDiagramIndicator(photoType, true);
    }
    
    showNotification(`${photoTypes.find(p => p.type === photoType).label} guardada`, 'success');
    
    // OCR: Auto-detect license plate from front photo
    if (photoType === 'front') {
        detectLicensePlate(blob);
    }
    
    // Auto-open diagram if all photos captured
    if (Object.keys(inspectionData.photos).length === 9) {
        // Mark delivery as complete if this is a delivery process
        const processType = localStorage.getItem('processType');
        if (processType === 'delivery') {
            const contractKey = localStorage.getItem('currentContractKey');
            if (contractKey) {
                const contracts = getActiveContracts();
                if (contracts[contractKey]) {
                    contracts[contractKey].deliveryComplete = true;
                    saveActiveContracts(contracts);
                    console.log('✅ Delivery marked as complete for contract:', contractKey);
                }
            }
        }
        
        // Show special completion message
        showFinalPhotoCompletionMessage();
        
        // Wait a bit then auto-navigate to diagram
        setTimeout(() => {
            console.log('🔵 Auto-opening diagram after 9 photos');
            showDiagramStep();
            // Also initialize canvas
            const canvasEl = document.getElementById('drawingCanvas');
            if (canvasEl && window.canvas) {
                const img = document.querySelector('#carDiagram img');
                if (img) {
                    canvasEl.width = img.offsetWidth;
                    canvasEl.height = img.offsetHeight;
                    console.log('✅ Canvas auto-initialized');
                }
            }
        }, 3500); // Longer delay to show completion message
    }
    
    // Remove preview
    const preview = document.getElementById('photoPreviewContainer');
    if (preview) preview.remove();
    
    // Clear temp blob
    window.tempPhotoBlob = null;
    
    // Check if we need to capture more photos
    const totalPhotos = Object.keys(inspectionData.photos).length;
    console.log(`Photos captured: ${totalPhotos}/9`);
    
    if (totalPhotos < 9) {
        // Find next photo type to capture
        const nextPhotoType = photoTypes.find(pt => !inspectionData.photos[pt.type]);
        
        if (nextPhotoType) {
            console.log('Opening next photo:', nextPhotoType.type);
            
            // Show processing overlay to prevent seeing main screen
            const processingOverlay = document.createElement('div');
            processingOverlay.id = 'processingOverlay';
            processingOverlay.style.cssText = `
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.95);
                z-index: 999998;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
            `;
            processingOverlay.innerHTML = `
                <div style="text-align: center;">
                    <div style="width: 60px; height: 60px; border: 4px solid #009cb6; border-top-color: transparent; border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto 20px;"></div>
                    <p style="color: white; font-size: 18px; font-weight: 500;">A processar foto...</p>
                </div>
                <style>
                    @keyframes spin {
                        to { transform: rotate(360deg); }
                    }
                </style>
            `;
            document.body.appendChild(processingOverlay);
            
            // Close current camera but keep stream for next photo
            closeCamera(true);
            
            // Show car diagram preview for next photo after short delay
            setTimeout(() => {
                // Remove processing overlay
                const overlay = document.getElementById('processingOverlay');
                if (overlay) overlay.remove();
                
                showCarDiagramPreview(nextPhotoType.type);
            }, 1500);
        }
    } else {
        // All photos captured, close camera
        console.log('✅ All 9 photos captured, closing camera');
        closeCamera();
    }
}

function showCompletionMessage() {
    // Close camera
    closeCamera();
    
    // Show completion screen
    const overlay = document.createElement('div');
    overlay.style.cssText = `
        position: fixed;
        inset: 0;
        background: rgba(16, 185, 129, 0.95);
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        z-index: 10000;
        backdrop-filter: blur(10px);
    `;
    
    overlay.innerHTML = `
        <div style="text-align: center; color: white; padding: 40px;">
            <svg style="width: 120px; height: 120px; margin: 0 auto 30px;" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
            </svg>
            <h2 style="font-size: 36px; font-weight: bold; margin-bottom: 16px;">Inspeção Terminada</h2>
            <p style="font-size: 18px; opacity: 0.9;">Todas as 6 fotos foram capturadas com sucesso</p>
            <p style="font-size: 16px; opacity: 0.8; margin-top: 12px;">A processar com AI...</p>
        </div>
    `;
    
    document.body.appendChild(overlay);
    
    setTimeout(() => {
        document.body.removeChild(overlay);
        autoSequenceMode = false;
    }, 3000);
}

// AI Analysis
async function startAIAnalysis() {
    const resultsDiv = document.getElementById('analysisResults');
    const progressDiv = document.getElementById('analysisProgress');
    resultsDiv.innerHTML = '';
    resultsDiv.classList.add('hidden');
    progressDiv.classList.remove('hidden');
    
    let analyzed = 0;
    const total = Object.keys(inspectionData.photos).length;
    
    for (const [photoType, photoBlob] of Object.entries(inspectionData.photos)) {
        try {
            // Create form data
            const formData = new FormData();
            formData.append('file', photoBlob, `${photoType}.jpg`);
            
            // Call AI API
            const response = await fetch('/api/vehicle/detect-damage', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            // Store result
            inspectionData.aiResults[photoType] = result;
            
            // Update progress
            analyzed++;
            const percent = Math.round((analyzed / total) * 100);
            document.getElementById('analysisPercent').textContent = `${percent}%`;
            document.getElementById('analysisBar').style.width = `${percent}%`;
            
            // Add result to display
            addAnalysisResult(photoType, result);
            
        } catch (error) {
            console.error(`Error analyzing ${photoType}:`, error);
            inspectionData.aiResults[photoType] = {ok: false, error: error.message};
        }
    }
    
    // Hide progress, show results
    progressDiv.classList.add('hidden');
    resultsDiv.classList.remove('hidden');
    document.getElementById('btnNextToReview').disabled = false;
    
    showNotification('AI analysis complete!', 'success');
}

function addAnalysisResult(photoType, result) {
    const photo = photoTypes.find(p => p.type === photoType);
    const resultsDiv = document.getElementById('analysisResults');
    
    let badgeClass = 'bg-green-100 text-green-800';
    let badgeText = 'No Damage';
    let icon = '';
    
    if (result.ok && result.has_damage) {
        if (result.confidence_percent > 70) {
            badgeClass = 'bg-red-100 text-red-800';
            badgeText = `${result.damage_type} (${result.confidence_percent}%)`;
            icon = '';
        } else {
            badgeClass = 'bg-yellow-100 text-yellow-800';
            badgeText = `Possible ${result.damage_type} (${result.confidence_percent}%)`;
            icon = '';
        }
    }
    
    const resultHtml = `
        <div class="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
            <div class="flex items-center gap-3">
                <img src="${URL.createObjectURL(inspectionData.photos[photoType])}" 
                     class="w-16 h-16 object-cover rounded" alt="${photo.label}">
                <div>
                    <div class="font-medium text-gray-900">${photo.label}</div>
                    <div class="text-sm text-gray-600">${result.verdict || 'Analysis complete'}</div>
                </div>
            </div>
            <div class="px-3 py-1 ${badgeClass} rounded-full text-xs font-semibold flex items-center gap-1">
                <span>${icon}</span>
                <span>${badgeText}</span>
            </div>
        </div>
    `;
    
    resultsDiv.insertAdjacentHTML('beforeend', resultHtml);
}

// Formatting functions
function formatFuelLevel(fuelLevel) {
    if (!fuelLevel && fuelLevel !== 0) return 'N/A';
    
    const percentage = parseInt(fuelLevel);
    let levelText = '';
    
    if (percentage === 0) {
        levelText = 'Vazio (OUT)';
    } else if (percentage <= 10) {
        levelText = 'Reserva (R)';
    } else if (percentage <= 25) {
        levelText = '1/4';
    } else if (percentage <= 50) {
        levelText = '1/2';
    } else if (percentage <= 75) {
        levelText = '3/4';
    } else {
        levelText = 'Cheio (F)';
    }
    
    return `${levelText} (${percentage}%)`;
}

function formatOdometerReading(reading) {
    if (!reading && reading !== 0) return 'N/A';
    
    const km = parseInt(reading);
    if (isNaN(km)) return 'N/A';
    
    // Format with thousands separator
    return `${km.toLocaleString('pt-PT')} km`;
}

// Review
function generateReview() {
    const summary = document.getElementById('reviewSummary');
    
    // Count damages
    let damageCount = 0;
    let highConfidenceDamages = [];
    
    for (const [photoType, result] of Object.entries(inspectionData.aiResults)) {
        if (result.ok && result.has_damage) {
            damageCount++;
            if (result.confidence_percent > 70) {
                highConfidenceDamages.push({
                    photo: photoTypes.find(p => p.type === photoType).label,
                    type: result.damage_type,
                    confidence: result.confidence_percent
                });
            }
        }
    }
    
    const hasDamage = damageCount > 0;
    
    summary.innerHTML = `
        <div class="space-y-6">
            <!-- Vehicle Info -->
            <div>
                <h3 class="font-semibold text-gray-900 mb-3">Vehicle Information</h3>
                <div class="grid grid-cols-2 gap-3 text-sm">
                    <div><span class="text-gray-600">Plate:</span> <span class="font-medium">${inspectionData.vehicleInfo.vehicle_plate}</span></div>
                    <div><span class="text-gray-600">Type:</span> <span class="font-medium">${inspectionData.vehicleInfo.inspection_type === 'check_in' ? 'Check-in' : 'Check-out'}</span></div>
                    <div><span class="text-gray-600">Brand:</span> <span class="font-medium">${inspectionData.vehicleInfo.vehicle_brand || 'N/A'}</span></div>
                    <div><span class="text-gray-600">Model:</span> <span class="font-medium">${inspectionData.vehicleInfo.vehicle_model || 'N/A'}</span></div>
                    <div><span class="text-gray-600">Contract:</span> <span class="font-medium">${inspectionData.vehicleInfo.contract_number || 'N/A'}</span></div>
                    <div><span class="text-gray-600">Odometer:</span> <span class="font-medium">${formatOdometerReading(inspectionData.vehicleInfo.odometer_reading)}</span></div>
                    <div><span class="text-gray-600">Fuel:</span> <span class="font-medium">${formatFuelLevel(inspectionData.vehicleInfo.fuel_level)}</span></div>
                    <div><span class="text-gray-600">Inspector:</span> <span class="font-medium">${inspectionData.vehicleInfo.inspector_name}</span></div>
                </div>
            </div>

            <!-- Damage Status -->
            <div>
                <h3 class="font-semibold text-gray-900 mb-3">Damage Assessment</h3>
                <div class="p-4 rounded-lg ${hasDamage ? 'bg-red-50 border border-red-200' : 'bg-green-50 border border-green-200'}">
                    <div class="flex items-center gap-2 mb-2">
                        <span class="text-2xl"></span>
                        <span class="font-bold text-lg">${hasDamage ? `${damageCount} Damage(s) Detected` : 'No Damage Detected'}</span>
                    </div>
                    ${highConfidenceDamages.length > 0 ? `
                        <div class="mt-3 space-y-1">
                            ${highConfidenceDamages.map(d => `
                                <div class="text-sm">• ${d.photo}: <strong>${d.type}</strong> (${d.confidence}% confidence)</div>
                            `).join('')}
                        </div>
                    ` : ''}
                </div>
            </div>

            <!-- Photos -->
            <div>
                <h3 class="font-semibold text-gray-900 mb-3">Captured Photos (${Object.keys(inspectionData.photos).length})</h3>
                <div class="grid grid-cols-3 gap-2">
                    ${Object.keys(inspectionData.photos).map(type => `
                        <img src="${URL.createObjectURL(inspectionData.photos[type])}" 
                             class="w-full h-24 object-cover rounded" 
                             alt="${photoTypes.find(p => p.type === type).label}">
                    `).join('')}
                </div>
            </div>

            ${inspectionData.vehicleInfo.inspector_notes ? `
                <div>
                    <h3 class="font-semibold text-gray-900 mb-2">Inspector Notes</h3>
                    <p class="text-sm text-gray-700 bg-gray-50 p-3 rounded">${inspectionData.vehicleInfo.inspector_notes}</p>
                </div>
            ` : ''}
        </div>
    `;
}

// Logout function
function logout() {
    // Clear user data
    localStorage.removeItem('userName');
    localStorage.removeItem('userToken');
    
    // Show confirmation
    if (confirm('Tem a certeza que deseja terminar a sessão?')) {
        // Redirect to login page
        window.location.href = '/login';
    }
}

// Save inspection
async function saveInspection() {
    showNotification('Saving inspection...', 'info');
    
    try {
        // Ensure we have the latest vehicle info with fuel and odometer data
        saveVehicleInfo();
        
        // Create form data with all information
        const formData = new FormData();
        
        // Add vehicle info
        for (const [key, value] of Object.entries(inspectionData.vehicleInfo)) {
            formData.append(key, value || '');
        }
        
        // Add photos
        for (const [photoType, photoBlob] of Object.entries(inspectionData.photos)) {
            formData.append(`photo_${photoType}`, photoBlob, `${photoType}.jpg`);
        }
        
        // Add AI results as JSON
        formData.append('ai_results', JSON.stringify(inspectionData.aiResults));
        
        // Add diagram data if exists
        if (window.diagramData) {
            formData.append('diagram_data', JSON.stringify(window.diagramData));
        }
        
        // Save to API
        const response = await fetch('/api/vehicle-inspections/create', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (result.ok) {
            showNotification('Inspection saved successfully!', 'success');
            
            // Redirect to inspections list after 2 seconds
            setTimeout(() => {
                window.location.href = '/vehicle-inspections';
            }, 2000);
        } else {
            throw new Error(result.error || 'Save failed');
        }
        
    } catch (error) {
        console.error('Save error:', error);
        showNotification('Error saving inspection: ' + error.message, 'error');
    }
}
