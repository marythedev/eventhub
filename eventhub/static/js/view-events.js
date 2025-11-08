// helper functions
const clearPriceFilter = () => {
    const freeOnlyCheckbox = document.querySelector("input[name='free_only']");

    priceInputs.forEach(input => input.value = "");
    freeOnlyCheckbox.checked = false;
}

const clearLocationFilter = () => {
    const locationInput = document.querySelector(".filter-group input[type='text']");
    const radiusSlider = document.getElementById("radiusSlider");
    const radiusValue = document.getElementById("radiusValue");

    locationInput.value = "";
    radiusSlider.value = 25;
    radiusValue.textContent = 25;
}

const clearDateFilter = () => {
    const dateFromInput = document.getElementById("dateFrom");
    const dateToInput = document.getElementById("dateTo");

    dateFromInput.value = "";
    dateFromInput.removeAttribute("max");
    dateToInput.value = "";
    dateToInput.removeAttribute("min");
}

const clearCategoryFilter = () => {
    const categoryCheckboxes = document.querySelectorAll("input[name='category']");
    categoryCheckboxes.forEach(checkbox => checkbox.checked = false);
}

const formatDate = (d) => {
    const date = new Date(d);
    const day = String(date.getDate()).padStart(2, '0');
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const year = date.getFullYear();
    return `${year}-${month}-${day}`;
}



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
    clearPriceFilter();
    clearLocationFilter();
    clearDateFilter();
    clearCategoryFilter();
});


// update location radius on slider move
const radiusSlider = document.getElementById('radiusSlider');
const radiusValue = document.getElementById('radiusValue');

if (radiusSlider && radiusValue) {
    radiusSlider.addEventListener('input', function () {
        radiusValue.textContent = this.value;
    });
}


const dateTo = document.getElementById("dateTo");
const dateFrom = document.getElementById("dateFrom");

// user can't select the date (date to) before 'date from'
document.getElementById("dateFrom").addEventListener("change", function () {
    dateTo.setAttribute("min", this.value);
    if (new Date(dateTo.value) < new Date(this.value))
        dateTo.value = this.value;
});

// user can't select the date (date from) after 'date to'
document.getElementById("dateTo").addEventListener("change", function () {
    dateFrom.setAttribute("max", this.value);
    if (new Date(dateFrom.value) > new Date(this.value))
        dateFrom.value = this.value;
});

// set date ranges when quick dates button is clicked
const quickDates = document.querySelector('.quick-dates');
const quickDatesBtns = quickDates.querySelectorAll('.quick-date-btn');

quickDates.addEventListener('click', function (e) {
    if (e.target && e.target.tagName === 'BUTTON') {
        quickDatesBtns.forEach(btn => btn.classList.remove('active'));
        e.target.classList.add('active');

        // update date range based on the clicked button
        const buttonText = e.target.textContent.trim().toLowerCase();
        let startDate = new Date();
        let endDate = new Date();

        if (buttonText === 'this week')
            endDate.setDate(startDate.getDate() + 6);
        else if (buttonText === 'this month') {
            endDate.setMonth(startDate.getMonth() + 1);
            endDate.setDate(0);     // end on the last day of the current month
        }

        dateFrom.value = formatDate(startDate);
        dateTo.value = formatDate(endDate);
    }
});


// change the position of create event button depending on breakpoint of max-width: 615px
const eventsHeader = document.querySelector('.events-header');
const eventControlsBtns = document.querySelector('.events-controls-btns');

const winWidth = window.matchMedia("(max-width: 615px)");

function onWidthChange(e) {
    const addEventBtn = document.querySelector('#events #addEventBtn');
    if (e.matches) {
        // move from header to event controls
        if (addEventBtn && !eventControlsBtns.contains(addEventBtn)) {
            addEventBtn.remove();
            eventControlsBtns.appendChild(addEventBtn);
        }
    }
    else {
        // move from event controls to header
        if (addEventBtn && !eventsHeader.contains(addEventBtn)) {
            addEventBtn.remove();
            eventsHeader.appendChild(addEventBtn);
        }
    }
}

winWidth.addEventListener('change', onWidthChange);
onWidthChange(winWidth);