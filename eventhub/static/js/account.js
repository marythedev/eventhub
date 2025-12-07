const loadingIndicator = document.getElementById('loadingIndicator');
let stripeConnectBtn = document.getElementById("stripe-setup");
let stripeDeleteBtn = document.getElementById("stripe-delete");

function showLoading() {
    if (loadingIndicator) loadingIndicator.classList.add("active");
    if (stripeConnectBtn) stripeConnectBtn.style.display = "none";
    if (stripeDeleteBtn) stripeDeleteBtn.style.display = "none";
}

function hideLoading() {
    if (loadingIndicator) loadingIndicator.classList.remove("active");
    if (stripeConnectBtn) stripeConnectBtn.style.display = "block";
    if (stripeDeleteBtn) stripeDeleteBtn.style.display = "block";
}

function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2)
        return parts.pop().split(';').shift();
}

async function fetchURL(url) {
    const res = await fetch(url, {
        method: "POST",
        headers: {
            "X-CSRFToken": getCookie("csrftoken"),
            "Content-Type": "application/json"
        }
    });
    const data = await res.json();
    return data;
}

// onboard / manage stripe account
if (stripeConnectBtn) {
    stripeConnectBtn.onclick = async () => {
        showLoading();

        try {
            const data = await fetchURL("/api/stripe/setup/");
            if (data.error)
                throw new Error(data.error);

            // account has not onboarded (account setup link)
            if (data.onboarding_url)
                window.location.href = data.onboarding_url;

            // account has completed onboarding (account manage link)
            else {
                hideLoading();
                window.open(data.login_link, "_blank");
            }
        } catch (err) {
            alert("Something went wrong.");
            hideLoading();
        }
    };
}

// delete stripe connected account
if (stripeDeleteBtn) {
    stripeDeleteBtn.onclick = async () => {
        if (!confirm("Are you sure you want to delete your connected Stripe account?\nThis cannot be undone."))
            return;

        showLoading();

        try {
            const data = await fetchURL("/api/stripe/delete/");
            if (data.error)
                throw new Error(data.error);

            window.location.reload();
        } catch (err) {
            alert("Something went wrong.");
            hideLoading();
        }
    };
}

// reset UI when navigating back (loading indicator will be reset)
window.addEventListener("pageshow", () => {
    if (loadingIndicator) loadingIndicator.classList.remove("active");
    if (stripeConnectBtn) stripeConnectBtn.style.display = "block";
    if (stripeDeleteBtn) stripeDeleteBtn.style.display = "block";
});

// highlight the clicked link in the account sidebar
const accountNavLinks = document.querySelectorAll('.account-nav-link');
accountNavLinks.forEach(link => {
    link.addEventListener('click', function (e) {
        accountNavLinks.forEach(l => l.classList.remove('active'));
        this.classList.add('active');
    });
});


// prompt account deletion alert and submit form to delete account upon confirmation
const deactivateAccountBtn = document.getElementById('deactivateAccountBtn');
deactivateAccountBtn.addEventListener('click', (e) => {
    e.preventDefault()
    if (!confirm("Are you sure you want to delete your account?\nThis cannot be undone."))
        return;
    deactivateAccountBtn.closest('form').submit();
});