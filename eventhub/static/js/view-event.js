const slides = document.querySelectorAll('.carousel-slide');
const nextBtn = document.getElementById('nextBtn');
const prevBtn = document.getElementById('prevBtn');

const orderForm = document.querySelector('.order-summary');
const selectedTicketsDiv = document.getElementById('selectedTickets');
const subtotalSpan = document.getElementById('subtotal');
const serviceFeeSpan = document.getElementById('serviceFee');
const taxSpan = document.getElementById('tax');
const totalSpan = document.getElementById('total');
const checkoutBtn = document.getElementById('checkoutBtn');

const SERVICE_FEE = 0.08
const TAX = 0.13

// img carousel manipulation
function showSlide(index) {
    slides.forEach(slide => slide.classList.remove('active'));
    slides[index].classList.add('active');
}

// round the second digit of the number
function round(number) {
    return Math.round(number * 100) / 100;
}

let currentIndex = 0;
try {
    nextBtn.addEventListener('click', () => {
        currentIndex = (currentIndex + 1) % slides.length;
        showSlide(currentIndex);
    });

    prevBtn.addEventListener('click', () => {
        currentIndex = (currentIndex - 1 + slides.length) % slides.length;
        showSlide(currentIndex);
    });
} catch{/* page only has 1 image */}

let price_zones = [];
function updateOrderSummary() {
    const ticketTypes = document.querySelectorAll('.ticket-type');
    let summaryHTML = '';
    let subtotal = 0;
    let selectedTicketsExists = false;
    
    price_zones = [];

    ticketTypes.forEach(ticket => {
        const qtyInput = ticket.querySelector('.qty-input');
        
        const id = ticket.dataset.zoneId;
        const name = ticket.dataset.ticketName;
        const price = parseFloat(ticket.dataset.price);
        const quantity = parseInt(qtyInput.value);
        
        price_zones.push({id, quantity});

        if (quantity > 0) {
            const totalForType = quantity * price;
            subtotal += totalForType;
            summaryHTML += `
                <div>
                    <span>${quantity} × ${name}</span>
                    <span class="price">$${round(totalForType).toFixed(2)}</span>
                </div>
            `;
            selectedTicketsExists = true;
        }
    });

    if (selectedTicketsExists) {
        subtotal = round(subtotal)
        const serviceFee = round(subtotal * SERVICE_FEE);
        const tax = round(subtotal * TAX);
        const total = round(subtotal + serviceFee + tax);

        selectedTicketsDiv.innerHTML = summaryHTML;
        subtotalSpan.textContent = `$${subtotal.toFixed(2)}`;
        serviceFeeSpan.textContent = `$${serviceFee.toFixed(2)}`;
        taxSpan.textContent = `$${tax.toFixed(2)}`;
        totalSpan.textContent = `$${total.toFixed(2)}`;
        checkoutBtn.disabled = false;
    } else {
        selectedTicketsDiv.innerHTML = '<p class="empty-state">No tickets selected</p>';
        subtotalSpan.textContent = '$0.00';
        serviceFeeSpan.textContent = '$0.00';
        taxSpan.textContent = '$0.00';
        totalSpan.textContent = '$0.00';
        checkoutBtn.disabled = true;
    }
}


// Quantity button event handling
const qtyBtns = document.querySelectorAll('.qty-btn');
qtyBtns.forEach(btn => {
    btn.addEventListener('click', function () {
        const action = this.getAttribute('data-action');
        const input = this.parentElement.querySelector('.qty-input');
        let value = parseInt(input.value);
        const max = parseInt(input.getAttribute('max'));

        if (action === 'increase' && value < max) {
            value++;
        } else if (action === 'decrease' && value > 0) {
            value--;
        }

        input.value = value;
        updateOrderSummary();
    });
});

orderForm.addEventListener('submit', (e) => {
    e.preventDefault();
    input = document.createElement('input');
    input.name = 'price_zones';
    input.type = 'hidden';
    input.value = JSON.stringify(price_zones);
    orderForm.append(input);
    orderForm.submit();
});