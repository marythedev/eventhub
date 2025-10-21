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



/* EXPLORE EVENTS PAGE */
// open/close filters
const filterToggleBtn = document.getElementById('filterToggleBtn');
const filtersSidebar = document.getElementById('filtersSidebar');
let filterBtnText = document.getElementById('filterBtnText');

if (filterToggleBtn && filtersSidebar) {
    filterToggleBtn.addEventListener('click', function () {
        filtersSidebar.classList.toggle('active');
        filterBtnText.textContent === 'Filters' ?
            filterBtnText.textContent = 'Close Filters' : filterBtnText.textContent = 'Filters'
    });
}


// clear all filters
document.getElementById("clearFilters").addEventListener("click", function () {
    // clear price filters
    const priceInputs = document.querySelectorAll(".price-inputs input");
    const freeOnlyCheckbox = document.querySelector("input[name='free_only']");

    priceInputs.forEach(input => input.value = "");
    freeOnlyCheckbox.checked = false;

    // clear location & set radius to default
    const locationInput = document.querySelector(".filter-group input[type='text']");
    const radiusSlider = document.getElementById("radiusSlider");
    const radiusValue = document.getElementById("radiusValue");

    locationInput.value = "";
    radiusSlider.value = 25;
    radiusValue.textContent = 25;

    // clear date filters
    const dateFromInput = document.getElementById("dateFrom");
    const dateToInput = document.getElementById("dateTo");

    dateFromInput.value = "";
    dateFromInput.removeAttribute("max");
    dateToInput.value = "";
    dateToInput.removeAttribute("min");

    // clear categories
    const categoryCheckboxes = document.querySelectorAll("input[name='category']");
    categoryCheckboxes.forEach(checkbox => checkbox.checked = false);
});


// update location radius value on slider move
const radiusSlider = document.getElementById('radiusSlider');
const radiusValue = document.getElementById('radiusValue');

if (radiusSlider && radiusValue) {
    radiusSlider.addEventListener('input', function () {
        radiusValue.textContent = this.value;
    });
}


// user can't select the date (date to) before 'date from'
document.getElementById("dateFrom").addEventListener("change", function () {
    const dateTo = document.getElementById("dateTo");
    dateTo.setAttribute("min", this.value);
    if (new Date(dateTo.value) < new Date(this.value))
        dateTo.value = this.value;
});

// user can't select the date (date from) after 'date to'
document.getElementById("dateTo").addEventListener("change", function () {
    const dateFrom = document.getElementById("dateFrom");
    dateFrom.setAttribute("max", this.value);
    if (new Date(dateFrom.value) > new Date(this.value))
        dateFrom.value = this.value;
});



/* FOOTER */
document.getElementById('current-year').textContent = new Date().getFullYear();