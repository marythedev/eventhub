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

// footer dynamic year update
document.getElementById('current-year').textContent = new Date().getFullYear();