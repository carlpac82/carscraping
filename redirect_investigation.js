// Check what's causing the redirect when clicking the icon
console.log('=== REDIRECT INVESTIGATION ===');

// Find the commissions icon
const icon = document.querySelector('a[href="/admin/commissions"]');
if (icon) {
  console.log('Icon found:', icon.outerHTML);
  
  // Check if there's something intercepting the click
  icon.addEventListener('click', function(e) {
    e.preventDefault(); // Stop the default behavior
    e.stopPropagation(); // Stop event bubbling
    
    console.log('=== CLICK INTERCEPTED ===');
    console.log('Click event stopped');
    console.log('Original href:', this.getAttribute('href'));
    console.log('Should navigate to:', this.href);
    
    // Now try to navigate manually
    console.log('Attempting manual navigation...');
    window.location.href = '/admin/commissions';
    
    return false; // Extra safety
  }, true); // Use capture phase
  
  console.log('Click interceptor added. Now click the icon.');
  
} else {
  console.log('Icon NOT found');
}

// Also check if there's any global navigation hijacking
console.log('Checking for navigation hijackers...');

// Check for any hashchange or popstate listeners
const originalPushState = history.pushState;
const originalReplaceState = history.replaceState;

history.pushState = function() {
  console.log('pushState called:', arguments);
  return originalPushState.apply(this, arguments);
};

history.replaceState = function() {
  console.log('replaceState called:', arguments);
  return originalReplaceState.apply(this, arguments);
};

window.addEventListener('popstate', function(e) {
  console.log('popstate event:', e);
});

// Check for any location.assign/replace hijacking
const originalAssign = location.assign;
const originalReplace = location.replace;

location.assign = function(url) {
  console.log('location.assign called with:', url);
  debugger; // This will pause execution if dev tools are open
  return originalAssign.call(this, url);
};

location.replace = function(url) {
  console.log('location.replace called with:', url);
  debugger; // This will pause execution if dev tools are open
  return originalReplace.call(this, url);
};

console.log('Navigation monitors installed');
console.log('=== END REDIRECT INVESTIGATION ===');
