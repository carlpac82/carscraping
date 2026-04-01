// Check what's in the hidden containers
console.log('=== CHECKING HIDDEN CONTAINERS ===');

const allContainers = document.querySelectorAll('div, section, article');
let hiddenContainers = [];
allContainers.forEach(container => {
  const style = window.getComputedStyle(container);
  if (style.display === 'none' || style.visibility === 'hidden' || style.opacity === '0') {
    hiddenContainers.push(container);
  }
});

console.log('Hidden containers details:');
hiddenContainers.forEach((container, index) => {
  console.log(`--- Hidden Container ${index} ---`);
  console.log('Tag:', container.tagName);
  console.log('Classes:', container.className);
  console.log('ID:', container.id);
  console.log('Display:', window.getComputedStyle(container).display);
  console.log('Visibility:', window.getComputedStyle(container).visibility);
  console.log('Opacity:', window.getComputedStyle(container).opacity);
  
  // Check if it contains important content
  const textContent = container.textContent.trim();
  if (textContent.length > 0 && textContent.length < 200) {
    console.log('Text content:', textContent);
  }
  
  // Check for form elements
  const forms = container.querySelectorAll('form, input, select, button');
  if (forms.length > 0) {
    console.log('Form elements:', forms.length);
  }
  
  console.log('');
});

// Also check if the main content has the expected structure
const mainContent = document.querySelector('main');
if (mainContent) {
  console.log('=== MAIN CONTENT STRUCTURE ===');
  console.log('Main HTML preview:', mainContent.innerHTML.substring(0, 500) + '...');
  
  // Check for the cards container
  const cardsContainer = document.getElementById('cardsContainer');
  if (cardsContainer) {
    console.log('Cards container found');
    console.log('Cards container children:', cardsContainer.children.length);
    console.log('Cards container visible:', cardsContainer.offsetParent !== null);
    
    // Check first few cards
    const cards = cardsContainer.querySelectorAll('.bg-white, .card, [class*="card"]');
    console.log('Cards found:', cards.length);
    if (cards.length > 0) {
      console.log('First card HTML:', cards[0].outerHTML.substring(0, 200));
    }
  } else {
    console.log('Cards container NOT found');
  }
}

console.log('=== END HIDDEN CONTAINERS CHECK ===');
