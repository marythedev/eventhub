// navbar redirection
const loginBtn = document.getElementById('loginBtn');
const registerBtn = document.getElementById('registerBtn');

if (loginBtn) {
    loginBtn.addEventListener('click', function () {
        window.location.href = '/login';
    });
}

if (registerBtn) {
    registerBtn.addEventListener('click', function () {
        window.location.href = '/register';
    });
}


// mobile menu toggle
const mobileMenu = document.getElementById('mobileMenu');
const mobileMenuClose = document.getElementById('mobileMenuClose');
const mobileMenuToggle = document.getElementById('mobileMenuToggle');

mobileMenuToggle.addEventListener('click', function () {
    mobileMenu.classList.add('active');
});

mobileMenuClose.addEventListener('click', function () {
    mobileMenu.classList.remove('active');
});


// change the position of login/register buttons depending on breakpoint of max-width: 615px
const winWidth = window.matchMedia("(max-width: 615px)");

function onWidthChange(e) {
    const authButtons = document.querySelector('.auth-buttons');
    if (e.matches) {
        // move from desktop nav to mobile menu
        if (authButtons && !mobileMenu.contains(authButtons)) {
            authButtons.remove();
            mobileMenu.appendChild(authButtons);
        }
    }
    else {
        // move from mobile menu to desktop nav
        const navActions = document.querySelector('.nav-actions');
        if (authButtons && !navActions.contains(authButtons)) {
            authButtons.remove();
            navActions.insertBefore(authButtons, mobileMenuToggle);
        }
    }
}

winWidth.addEventListener('change', onWidthChange);
onWidthChange(winWidth);