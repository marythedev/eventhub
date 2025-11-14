const script = document.getElementById('checkout-script');

// stripe setup
const STRIPE_PUBLIC_KEY = script.dataset.stripePublicKey;
const stripe = Stripe(`${STRIPE_PUBLIC_KEY}`);
const elements = stripe.elements();

let { inputColor, errorColor } = getStripeInputColors();
let style = {
    base: { color: inputColor },
    invalid: { color: errorColor }
};

const cardNumber = elements.create('cardNumber', { style });
const cardExpiry = elements.create('cardExpiry', { style });
const cardCvc = elements.create('cardCvc', { style });
cardNumber.mount('#card-number');
cardExpiry.mount('#card-expiry');
cardCvc.mount('#card-cvc');

// validation errors
cardNumber.on('change', e => {
    document.getElementById('card-number-errors').textContent = e.error ? e.error.message : '';
});
cardExpiry.on('change', e => {
    document.getElementById('card-expiry-errors').textContent = e.error ? e.error.message : '';
});
cardCvc.on('change', e => {
    document.getElementById('card-cvc-errors').textContent = e.error ? e.error.message : '';
});

// update stripe colors (for theme switch)
export function getStripeInputColors() {
    return {
        inputColor: getComputedStyle(document.body).getPropertyValue('--text-primary').trim(),
        errorColor: getComputedStyle(document.body).getPropertyValue('--error-color').trim()
    };
}

export function updateStripeColors(newInputColor, newErrorColor) {
    style = {
        base: { color: newInputColor },
        invalid: { color: newErrorColor }
    };

    cardNumber.update({ style });
    cardExpiry.update({ style });
    cardCvc.update({ style });
}


// get payment_method_id from stripe and submit to backend
const form = document.getElementById('checkout-form');
const userEmail = script.dataset.userEmail;

form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const { paymentMethod, error } = await stripe.createPaymentMethod({
        type: 'card',
        card: cardNumber,
        billing_details: {
            name: document.getElementById('cardholderName').value,
            email: userEmail,
        },
    });

    if (error) {
        document.getElementById('card-number-errors').textContent = error.message;
    } else {
        const hiddenInput = document.createElement('input');
        hiddenInput.setAttribute('type', 'hidden');
        hiddenInput.setAttribute('name', 'payment_method_id');
        hiddenInput.setAttribute('value', paymentMethod.id);

        form.appendChild(hiddenInput);
        form.submit();
    }
});