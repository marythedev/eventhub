const slides = document.querySelectorAll('.carousel-slide');
const nextBtn = document.getElementById('nextBtn');
const prevBtn = document.getElementById('prevBtn');

const selectedTicketsDiv = document.getElementById('selectedTickets');
const subtotalSpan = document.getElementById('subtotal');
const serviceFeeSpan = document.getElementById('serviceFee');
const taxSpan = document.getElementById('tax');
const totalSpan = document.getElementById('total');
const checkoutBtn = document.getElementById('checkoutBtn');


// img carousel manipulation
function showSlide(index) {
    slides.forEach(slide => slide.classList.remove('active'));
    slides[index].classList.add('active');
}

let currentIndex = 0;
nextBtn.addEventListener('click', () => {
    currentIndex = (currentIndex + 1) % slides.length;
    showSlide(currentIndex);
});

prevBtn.addEventListener('click', () => {
    currentIndex = (currentIndex - 1 + slides.length) % slides.length;
    showSlide(currentIndex);
});

function updateOrderSummary() {
    const ticketTypes = document.querySelectorAll('.ticket-type');
    let summaryHTML = '';
    let subtotal = 0;

    ticketTypes.forEach(ticket => {
        const qtyInput = ticket.querySelector('.qty-input');
        const quantity = parseInt(qtyInput.value);
        const price = parseFloat(ticket.dataset.price);
        const name = ticket.dataset.ticketName;

        if (quantity > 0) {
            const totalForType = quantity * price;
            subtotal += totalForType;
            summaryHTML += `
                <div>
                    <span>${quantity} × ${name}</span>
                    <span>$${totalForType.toFixed(2)}</span>
                </div>
            `;
        }
    });

    if (subtotal === 0) {
        selectedTicketsDiv.innerHTML = '<p class="empty-state">No tickets selected</p>';
        subtotalSpan.textContent = '$0.00';
        serviceFeeSpan.textContent = '$0.00';
        taxSpan.textContent = '$0.00';
        totalSpan.textContent = '$0.00';
        checkoutBtn.disabled = true;
    } else {
        const serviceFee = subtotal * 0.08;
        const tax = subtotal * 0.13;
        const total = subtotal + serviceFee + tax;

        selectedTicketsDiv.innerHTML = summaryHTML;
        subtotalSpan.textContent = `$${subtotal.toFixed(2)}`;
        serviceFeeSpan.textContent = `$${serviceFee.toFixed(2)}`;
        taxSpan.textContent = `$${tax.toFixed(2)}`;
        totalSpan.textContent = `$${total.toFixed(2)}`;
        checkoutBtn.disabled = false;
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
