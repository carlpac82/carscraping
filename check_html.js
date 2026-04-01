// Check the actual HTML structure around the icon
console.log('=== CHECKING HTML STRUCTURE ===');

// Get the icon and its surroundings
const commissionsIcon = document.querySelector('a[href="/admin/commissions"]');
if (commissionsIcon) {
  console.log('Icon found');
  console.log('Icon HTML:', commissionsIcon.outerHTML);
  
  // Check parent structure
  console.log('Parent HTML:', commissionsIcon.parentElement.outerHTML);
  
  // Check if it's inside a form
  const form = commissionsIcon.closest('form');
  if (form) {
    console.log('INSIDE A FORM!');
    console.log('Form action:', form.action);
    console.log('Form method:', form.method);
  }
  
  // Check if there's a wrapper that might be intercepting clicks
  const wrapper = commissionsIcon.closest('[onclick], [data-href], .clickable, .nav-item');
  if (wrapper) {
    console.log('Found clickable wrapper:', wrapper);
    console.log('Wrapper classes:', wrapper.className);
    console.log('Wrapper onclick:', wrapper.getAttribute('onclick'));
  }
  
  // Check all event listeners on the icon
  const listeners = getEventListeners ? getEventListeners(commissionsIcon) : 'Not available';
  console.log('Event listeners:', listeners);
  
  // Check if the href is correct
  console.log('Href attribute:', commissionsIcon.getAttribute('href'));
  console.log('Full href:', commissionsIcon.href);
  
  // Try to prevent default and test manually
  console.log('=== TESTING MANUAL NAVIGATION ===');
  console.log('Trying to navigate to:', commissionsIcon.href);
  
} else {
  console.log('Icon NOT found');
  
  // Let's search for any links that mention commissions
  const allLinks = document.querySelectorAll('a');
  console.log('All links found:', allLinks.length);
  
  allLinks.forEach((link, index) => {
    if (link.href && link.href.includes('commission')) {
      console.log(`Commission link ${index}:`, link.outerHTML);
    }
  });
}

// Check for any meta refresh tags
const metaRefresh = document.querySelector('meta[http-equiv="refresh"]');
if (metaRefresh) {
  console.log('META REFRESH FOUND:', metaRefresh.outerHTML);
}

// Check for any redirect scripts
const scripts = document.querySelectorAll('script');
scripts.forEach((script, index) => {
  if (script.textContent.includes('location') || script.textContent.includes('redirect')) {
    console.log(`Script ${index} contains location/redirect:`, script.textContent.substring(0, 200));
  }
});

console.log('=== END HTML STRUCTURE CHECK ===');
