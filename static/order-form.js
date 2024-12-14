const decreaseBtns = document.querySelectorAll('.decrease');
const increaseBtns = document.querySelectorAll('.increase');
const itemPrice = 14.49;
const shippingOptions = {
    standard: 5.00,
    express: 10.00,
};

const taxRate = 0.09; // 9% tax rate
let selectedShipping = "standard"; // Default shipping option

// Get stock level and color from the hidden inputs
const stockLevel = parseInt(document.getElementById('stockLevel').value, 10);
const itemColor = document.getElementById('itemColor').value;

// Event listeners for quantity buttons
decreaseBtns.forEach((btn) => {
    btn.addEventListener('click', (e) => {
        e.preventDefault();
        const quantityElement = btn.nextElementSibling;
        let quantity = parseInt(quantityElement.textContent);
        if (quantity > 1) {
            quantity -= 1;
            quantityElement.textContent = quantity;
        }
        updateSummary();
    });
});

increaseBtns.forEach((btn) => {
    btn.addEventListener('click', (e) => {
        e.preventDefault();
        const quantityElement = btn.previousElementSibling;
        let quantity = parseInt(quantityElement.textContent);

        // Check if quantity is less than the stock level
        if (quantity < stockLevel) {
            quantity += 1;
            quantityElement.textContent = quantity;
        } else {
            alert(`Sorry, we don't have enough stock for the ${itemColor} item.`);
        }
        updateSummary();
    });
});


// Event listener for shipping selection
document.querySelector(".form-select").addEventListener("change", (e) => {
    selectedShipping = e.target.value; // Update selected shipping
    updateSummary();
});

// Function to update the summary
function updateSummary() {
    const quantities = document.querySelectorAll('.quantity');
    let totalQuantity = 0;
    quantities.forEach((quantityElement) => {
        totalQuantity += parseInt(quantityElement.textContent);
    });

    const baseShippingPrice = shippingOptions[selectedShipping];
    const additionalShipping = totalQuantity > 1 ? 2 * (totalQuantity - 1) : 0;
    const shippingPrice = baseShippingPrice + additionalShipping;

    const subtotal = totalQuantity * itemPrice;
    const tax = subtotal * taxRate;
    const totalPrice = subtotal + shippingPrice + tax;

    // Update UI elements
    document.querySelector('.total-quantity').textContent = totalQuantity;
    document.querySelector('.subtotal-price').textContent = `$${subtotal.toFixed(2)}`;
    document.querySelector('.shipping-fee').textContent = `$${shippingPrice.toFixed(2)}`;
    document.querySelector('.tax-fee').textContent = `$${tax.toFixed(2)}`;
    document.querySelector('.total-price').textContent = `$${totalPrice.toFixed(2)}`;
}

// Initialize the summary
updateSummary();


// PayPal Button Render
paypal.Buttons({
createOrder: (data, actions) => {
    const totalQuantity = Array.from(document.querySelectorAll('.quantity')).reduce(
        (sum, el) => sum + parseInt(el.textContent),
        0
    );

    const itemTotal = (itemPrice * totalQuantity).toFixed(2); // Calculate item total
    const shippingValue = selectedShipping === "standard" 
        ? shippingOptions.standard 
        : shippingOptions.express;
    const additionalShipping = totalQuantity > 1 ? 2 * (totalQuantity - 1) : 0;
    const shippingCost = (shippingValue + additionalShipping).toFixed(2);

    const taxValue = (itemTotal * taxRate).toFixed(2); // Calculate tax
    const totalValue = (parseFloat(itemTotal) + parseFloat(shippingCost) + parseFloat(taxValue)).toFixed(2);

    const fullName = document.getElementById('fullName').value;
    const addressLine1 = document.getElementById('address1').value;
    const addressLine2 = document.getElementById('address2').value;
    const city = document.getElementById('city').value;
    const state = document.getElementById('state').value;
    const postalCode = document.getElementById('postalCode').value;
    const countryCode = document.getElementById('countryCode').value;
    const sku = "{{ color }}";

    return actions.order.create({
        purchase_units: [{
            items: [{
                name: 'Smart Pet Tag',
                sku: sku,
                unit_amount: {
                    currency_code: 'USD',
                    value: itemPrice.toFixed(2),
                },
                quantity: totalQuantity,
            }],
            amount: {
                currency_code: 'USD',
                value: totalValue, // Total must match breakdown
                breakdown: {
                    item_total: {
                        currency_code: 'USD',
                        value: itemTotal,
                    },
                    shipping: {
                        currency_code: 'USD',
                        value: shippingCost,
                    },
                    tax_total: {
                        currency_code: 'USD',
                        value: taxValue,
                    },
                },
            },
            shipping: {
                name: {
                    full_name: fullName
                },
                address: {
                    address_line_1: addressLine1,
                    address_line_2: addressLine2,
                    admin_area_2: city,
                    admin_area_1: state,
                    postal_code: postalCode,
                    country_code: countryCode
                }
            }
        }],
        application_context: {
            shipping_preference: 'SET_PROVIDED_ADDRESS' // Ensures the provided address is used
        }
    });
},
onApprove: (data, actions) => {
    return actions.order.capture().then((details) => {
        alert('Payment Successful! Thank you, ' + details.payer.name.given_name);
    });
},
onError: (err) => {
    // Display error message in an alert
    alert('Payment error. Please check your delivery info and item quantity. Contact support if the issue persists.');
},
onCancel: (data) => {
    // Display cancellation message in an alert
    alert('Payment was cancelled. Please try again if this was unintentional.');
},
}).render('#paypal-button-container');
