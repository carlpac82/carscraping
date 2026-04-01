// Test direct navigation to commissions page
console.log('=== TESTING DIRECT NAVIGATION ===');

// Test 1: Try to navigate directly
console.log('Current URL before test:', window.location.href);

// Test 2: Check if we can access the commissions API directly
fetch('/api/admin/commissions/summary')
  .then(response => {
    console.log('API Response status:', response.status);
    if (response.ok) {
      return response.json();
    } else {
      console.log('API Response text:', response.statusText);
      throw new Error('API failed');
    }
  })
  .then(data => {
    console.log('API Data:', data);
    console.log('API access SUCCESSFUL - session is valid');
  })
  .catch(error => {
    console.log('API Error:', error);
    console.log('API access FAILED - session might be invalid');
  });

// Test 3: Check session validity
fetch('/api/user-session')
  .then(response => response.json())
  .then(sessionData => {
    console.log('Session data:', sessionData);
    
    // Check if session has required fields
    const hasAuth = sessionData.username && sessionData.is_admin;
    const hasCommissionPermission = sessionData.can_manage_commissions;
    
    console.log('Has auth:', hasAuth);
    console.log('Has commission permission:', hasCommissionPermission);
    
    if (hasAuth && hasCommissionPermission) {
      console.log('SESSION IS VALID - should be able to access commissions');
      
      // Try manual navigation
      console.log('Trying manual navigation...');
      window.location.href = '/admin/commissions';
    } else {
      console.log('SESSION IS INVALID - missing required permissions');
      console.log('Missing auth:', !hasAuth);
      console.log('Missing commission permission:', !hasCommissionPermission);
    }
  })
  .catch(error => {
    console.log('Session check failed:', error);
  });

console.log('=== END DIRECT NAVIGATION TEST ===');
