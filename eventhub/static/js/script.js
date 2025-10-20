// highlight the clicked link in the account sidebar
const accountNavLinks = document.querySelectorAll('.account-nav-link');
accountNavLinks.forEach(link => {
    link.addEventListener('click', function (e) {
        accountNavLinks.forEach(l => l.classList.remove('active'));
        this.classList.add('active');
    });
});

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


//footer 
document.getElementById('current-year').textContent = new Date().getFullYear();