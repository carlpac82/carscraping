// Check why content is not visible
console.log('=== VISIBILITY CHECK ===');

// Check if we're actually on the commissions page
console.log('Current URL:', window.location.href);
console.log('Page title:', document.title);

// Check main content
const main = document.querySelector('main');
if (main) {
  console.log('Main element found');
  console.log('Main visible:', main.offsetParent !== null);
  console.log('Main display:', window.getComputedStyle(main).display);
  console.log('Main height:', main.offsetHeight);
  console.log('Main scroll height:', main.scrollHeight);
  
  // Check if content is inside
  const content = main.innerHTML;
  console.log('Main content length:', content.length);
  console.log('Main content preview:', content.substring(0, 300));
  
  // Check for the cards container
  const cardsContainer = document.getElementById('cardsContainer');
  if (cardsContainer) {
    console.log('Cards container found');
    console.log('Cards container visible:', cardsContainer.offsetParent !== null);
    console.log('Cards container children:', cardsContainer.children.length);
    console.log('Cards container height:', cardsContainer.offsetHeight);
    
    // Show first few cards
    const cards = cardsContainer.children;
    for (let i = 0; i < Math.min(3, cards.length); i++) {
      console.log(`Card ${i}:`, cards[i].outerHTML.substring(0, 150));
    }
  } else {
    console.log('Cards container NOT found');
  }
} else {
  console.log('Main element NOT found');
}

// Check body height
console.log('Body height:', document.body.offsetHeight);
console.log('Window height:', window.innerHeight);
console.log('Document height:', document.documentElement.scrollHeight);

// Check for any overlays
const overlays = document.querySelectorAll('.modal, .overlay, [role="dialog"]');
console.log('Overlays found:', overlays.length);

// Check if page is scrolled
console.log('Scroll position:', window.scrollY, window.scrollX);

console.log('=== END VISIBILITY CHECK ===');
