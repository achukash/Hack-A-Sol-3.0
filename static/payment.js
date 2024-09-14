function validateNext() {
    const cardNumber = document.getElementById('card-number').value.trim();
    const cvv = document.getElementById('cvv').value.trim();
    const errorMessage = document.getElementById('error-message');

    // Reset error message
    errorMessage.textContent = '';

    // Check if card number and CVV are valid
    if (cardNumber.length === 0) {
        errorMessage.textContent = 'Enter card number';
        return;  // Exit if validation fails
    } else if (cvv.length === 0) {
        errorMessage.textContent = 'Enter CVV';
        return;  // Exit if validation fails
    }

    // Example validation (you can replace this with your actual validation logic)
    if (cardNumber === '123456' && cvv === '123') {
        // Redirect to /upload if valid
        window.location.href = '/upload';
    } else {
        errorMessage.textContent = 'Enter valid card number and CVV';
    }
}
