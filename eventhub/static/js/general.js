// smooth scroll to #id sections
// stops 100px before the section to avoid nav overlap
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();

        const targetID = this.getAttribute('href').substring(1);
        const targetElement = document.getElementById(targetID);

        if (targetElement) {
            const yOffset = -100;
            const y = targetElement.getBoundingClientRect().top + window.pageYOffset + yOffset;

            window.scrollTo({ top: y, behavior: 'smooth' });
        }
    });
});

// smooth scroll to the hash section (for redirection links from 3rd party apps i.e. stripe)
window.addEventListener("DOMContentLoaded", () => {
    const hash = window.location.hash;

    if (hash) {
        window.scrollTo(0, 0);

        setTimeout(() => {
            const id = hash.substring(1);
            const targetLink = document.querySelector(`a[href="#${id}"]`);

            if (targetLink) {
                targetLink.click();
                history.replaceState(null, null, window.location.pathname);
            }
        }, 0);
    }
});

// disable main form button to avoid multiple form submissions
const formBtns = document.querySelectorAll("form .btn-primary");
formBtns.forEach(btn => {
    btn.addEventListener('click', function () {
        const form = btn.closest('form');
        form.requestSubmit();

        if (form.checkValidity() && (form.id != 'checkout-form' || areStripeFieldsValid())) {
            btn.textContent = "Loading...";
            btn.disabled = true;
        }
    });
});

function areStripeFieldsValid() {
    const cardNumber = document.querySelector("#card-number");
    const cardExpiry = document.querySelector("#card-expiry");
    const cardCvc = document.querySelector("#card-cvc");

    const cardNumberValid = cardNumber.classList.contains("StripeElement--complete");
    const cardExpiryValid = cardExpiry.classList.contains("StripeElement--complete");
    const cardCvcValid = cardCvc.classList.contains("StripeElement--complete");

    return cardNumberValid && cardExpiryValid && cardCvcValid;
}


// footer dynamic year update
document.addEventListener("DOMContentLoaded", () => {
    const footerYear = document.getElementById("current-year");
    if (footerYear) {
        footerYear.textContent = new Date().getFullYear();
    }
});