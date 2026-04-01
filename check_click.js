// Check the click event on commissions icon
console.log('=== CHECKING CLICK EVENT ===');

// Find the commissions icon
const commissionsIcon = document.querySelector('a[href="/admin/commissions"]');
if (commissionsIcon) {
  console.log('Found commissions icon');
  
  // Check if there are any event listeners
  console.log('onclick attribute:', commissionsIcon.getAttribute('onclick'));
  
  // Check parent elements for click handlers
  let parent = commissionsIcon.parentElement;
  while (parent && parent !== document.body) {
    if (parent.getAttribute('onclick')) {
      console.log('Parent has onclick:', parent.tagName, parent.getAttribute('onclick'));
    }
    parent = parent.parentElement;
  }
  
  // Add a test click listener
  commissionsIcon.addEventListener('click', function(e) {
    console.log('=== CLICK DETECTED ===');
    console.log('Event:', e);
    console.log('Default prevented?', e.defaultPrevented);
    console.log('Propagation stopped?', e.cancelBubble);
    
    // Check if href is being followed
    console.log('Href:', this.getAttribute('href'));
    console.log('Will navigate to:', this.href);
  });
  
  console.log('Click listener added. Try clicking the icon now.');
  
} else {
  console.log('Commissions icon NOT found');
}

// Check for any global click handlers
console.log('=== GLOBAL CLICK HANDLERS ===');
if (window.onclick) {
  console.log('Global onclick exists:', window.onclick.toString());
}

// Check for any navigation interceptors
console.log('=== NAVIGATION INTERCEPTORS ===');
if (window.addEventListener) {
  // This will show if there are any popstate or hashchange listeners
  console.log('Checking for navigation listeners...');
}

// Check if there's any JavaScript that might be redirecting
const scripts = document.querySelectorAll('script');
console.log('Scripts found:', scripts.length);

// Look for any redirect patterns in the page content
const pageText = document.body.textContent || document.body.innerText;
if (pageText.includes('location.href') || pageText.includes('window.location')) {
  console.log('Found location redirect patterns in page text');
}

console.log('=== END CLICK EVENT CHECK ===');
