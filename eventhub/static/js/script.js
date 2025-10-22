/* ACCOUNT */
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


/* CREATE EVENT PAGE */
function updateCounter(counterField, maxLength, inputField) {
    const currentLength = inputField.value.length;
    counterField.textContent = `${currentLength} / ${maxLength} characters`;
}

// dynamic update of input characters for event name
const nameInput = document.getElementById('eventName');
const nameCounter = document.getElementById('nameCounter');
if (nameInput) {
    const nameMaxLength = nameInput.getAttribute('maxlength');
    updateCounter(nameCounter, nameMaxLength, nameInput);
    nameInput.addEventListener('input', () => updateCounter(nameCounter, nameMaxLength, nameInput));
}

// dynamic update of input characters for event description
const descTextarea = document.getElementById('eventDescription');
const descCounter = document.getElementById('descCounter');
if (descTextarea) {
    const descMaxLength = descTextarea.getAttribute('maxlength');
    updateCounter(descCounter, descMaxLength, descTextarea);
    descTextarea.addEventListener('input', () => updateCounter(descCounter, descMaxLength, descTextarea));
}


/* FOOTER */
document.getElementById('current-year').textContent = new Date().getFullYear();