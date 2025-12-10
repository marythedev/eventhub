const body = document.body;
const themeToggle = document.getElementById('themeToggle');
const savedTheme = localStorage.getItem('theme');
const systemPrefersLight = window.matchMedia('(prefers-color-scheme: light)').matches;

function setTheme(theme) {
    if (theme === 'light') {
        body.classList.add('light-theme');
        themeToggle.innerHTML = '<i class="fas fa-sun"></i>';
    } else {
        body.classList.remove('light-theme');
        themeToggle.innerHTML = '<i class="fas fa-moon"></i>';
    }
    localStorage.setItem('theme', theme);
}

if (savedTheme) {
    setTheme(savedTheme);
} else {
    setTheme(systemPrefersLight ? 'light' : 'dark');
}

themeToggle.addEventListener('click', async function () {
    const currentTheme = body.classList.contains('light-theme') ? 'light' : 'dark';
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    setTheme(newTheme);

    // checkout form stripe input color update if user is on checkout page
    await updateCheckoutFormColor();
});

// initial checkout form stripe input color fetch
document.addEventListener('DOMContentLoaded', async () => {
    await updateCheckoutFormColor();
});

async function updateCheckoutFormColor() {
    if (document.getElementById('checkout-form')) {
        const { updateStripeColors, getStripeInputColors } = await import('./checkout.js');
        const { inputColor, errorColor } = getStripeInputColors();
        updateStripeColors(inputColor, errorColor);
    }
}

window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function (e) {
    if (!localStorage.getItem('theme')) {
        setTheme(e.matches ? 'dark' : 'light');
    }
});