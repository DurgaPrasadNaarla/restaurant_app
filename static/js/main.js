// filepath: andhra-cuisine-app/static/js/main.js

document.addEventListener('DOMContentLoaded', function() {
    // Add event listeners for add to cart buttons
    const addToCartButtons = document.querySelectorAll('.btn-primary');
    addToCartButtons.forEach(button => {
        button.addEventListener('click', function() {
            const itemId = this.getAttribute('data-item-id');
            addToCart(itemId);
        });
    });
});

// Function to add item to cart
function addToCart(itemId) {
    fetch(`/add_to_cart/${itemId}`, {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
        // Optionally update cart UI here
    })
    .catch(error => console.error('Error adding to cart:', error));
}

// Function to remove item from cart
function removeFromCart(itemId) {
    fetch(`/remove_from_cart/${itemId}`, {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
        // Optionally update cart UI here
        location.reload(); // Reload to reflect changes
    })
    .catch(error => console.error('Error removing from cart:', error));
}