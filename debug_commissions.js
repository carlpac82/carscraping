// Debug script for commissions redirect issue
console.log('=== DEBUG COMMISSIONS REDIRECT ===');

// 1. Check if we're on the right page
console.log('Current URL:', window.location.href);
console.log('Path:', window.location.pathname);

// 2. Check session data
fetch('/api/user-session')
  .then(response => response.json())
  .then(data => {
    console.log('Session data:', data);
    console.log('Can manage commissions:', data.can_manage_commissions);
    console.log('Is admin:', data.is_admin);
    console.log('Username:', data.username);
  })
  .catch(error => console.error('Error getting session:', error));

// 3. Test the commissions route directly
fetch('/admin/commissions', {
  method: 'GET',
  redirect: 'manual'  // Don't follow redirects automatically
})
.then(response => {
  console.log('Commissions route response:', response.status);
  console.log('Response headers:', Object.fromEntries(response.headers.entries()));
  if (response.status === 302 || response.status === 303) {
    console.log('Redirect location:', response.headers.get('location'));
  }
})
.catch(error => console.error('Error testing commissions route:', error));

// 4. Check if the icon click event is working
const commissionsIcon = document.querySelector('a[href="/admin/commissions"]');
if (commissionsIcon) {
  console.log('Found commissions icon:', commissionsIcon);
  console.log('Icon title:', commissionsIcon.getAttribute('title'));
  console.log('Icon is visible:', commissionsIcon.offsetParent !== null);
} else {
  console.log('Commissions icon NOT found in DOM');
}

// 5. Check all navigation links
const navLinks = document.querySelectorAll('nav a, .desktop-nav a');
console.log('All navigation links:');
navLinks.forEach((link, index) => {
  console.log(`${index}: ${link.getAttribute('href')} - ${link.getAttribute('title')}`);
});

console.log('=== END DEBUG ===');
