// This script checks if we're viewing a directory and redirects to index.html if needed
(function() {
    // Get the current path
    const path = window.location.pathname;
    
    // Check if the path ends with a slash (directory)
    if (path.endsWith('/')) {
        // Redirect to index.html in that directory
        window.location.href = path + 'index.html';
    } 
    // Check if we're at a directory without a trailing slash
    else if (!path.includes('.')) {
        // Redirect to index.html in that directory
        window.location.href = path + '/index.html';
    }
})();
