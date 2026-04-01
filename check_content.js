// Check if content is loaded but hidden
console.log('=== CHECKING CONTENT VISIBILITY ===');

// 1. Check main content area
const mainContent = document.querySelector('main, .main-content, #content, .container');
if (mainContent) {
  console.log('Main content found:', mainContent);
  console.log('Main content visible:', mainContent.offsetParent !== null);
  console.log('Main content display:', window.getComputedStyle(mainContent).display);
  console.log('Main content visibility:', window.getComputedStyle(mainContent).visibility);
  console.log('Main content opacity:', window.getComputedStyle(mainContent).opacity);
} else {
  console.log('Main content NOT found');
}

// 2. Check if there are any loading spinners
const loaders = document.querySelectorAll('.loading, .spinner, .loader');
console.log('Loading elements found:', loaders.length);

// 3. Check body for any classes that might hide content
const bodyClasses = document.body.className;
console.log('Body classes:', bodyClasses);

// 4. Check if content is inside a hidden container
const allContainers = document.querySelectorAll('div, section, article');
let hiddenContainers = [];
allContainers.forEach(container => {
  const style = window.getComputedStyle(container);
  if (style.display === 'none' || style.visibility === 'hidden' || style.opacity === '0') {
    hiddenContainers.push(container);
  }
});
console.log('Hidden containers:', hiddenContainers.length);

// 5. Check for any overlay or modal
const overlays = document.querySelectorAll('.modal, .overlay, [role="dialog"]');
console.log('Modals/overlays found:', overlays.length);

// 6. Check page title
console.log('Page title:', document.title);

// 7. Check if there are any error messages
const errorElements = document.querySelectorAll('.error, .alert-danger, [role="alert"]');
console.log('Error elements:', errorElements.length);
errorElements.forEach((el, i) => {
  console.log(`Error ${i}:`, el.textContent.trim());
});

console.log('=== END CONTENT CHECK ===');
