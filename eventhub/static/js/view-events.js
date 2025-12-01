// helper functions
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
const today = formatDate(new Date());

if (dateFrom) {
    dateFrom.setAttribute('min', today);

    // user can't select the date (date to) before 'date from'
    dateFrom.addEventListener("change", function () {
        dateTo.setAttribute("min", this.value);
        if (new Date(dateTo.value) < new Date(this.value))
            dateTo.value = this.value;
    });
}
if (dateTo) {
    dateTo.setAttribute('min', today);

    // user can't select the date (date from) after 'date to'
    dateTo.addEventListener("change", function () {
        dateFrom.setAttribute("max", this.value);
        if (new Date(dateFrom.value) > new Date(this.value))
            dateFrom.value = this.value;
    });
}

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


// apply filters
// get all filter data and update query string with it
const applyBtn = document.getElementById("applyFilters");

applyBtn.addEventListener("click", function (e) {
    e.preventDefault();

    const sidebar = document.getElementById("filtersSidebar");
    const inputs = sidebar.querySelectorAll("input");

    // clean up any previous filter data in the query
    const params = new URLSearchParams(window.location.search);
    inputs.forEach(input => params.delete(input.name));

    // update query with relevant filter data
    inputs.forEach(input => {
        if (input.type === "checkbox") {
            if (input.checked) {
                params.append(input.name, input.value || "true");
            }
        } else if (input.value.trim() !== "") {
            params.append(input.name, input.value.trim());
        }
    });

    window.location.href = `/events/explore/?${params.toString()}`;
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