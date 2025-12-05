// search functionality
const searchInputs = document.querySelectorAll(".eventsSearch");
const suggestionBoxes = document.querySelectorAll(".searchSuggestions");

searchInputs.forEach((input, index) => {

    const suggestionsBox = suggestionBoxes[index];
    let searchTimeout = null;
    const isMyEventsSearch = input.classList.contains('my-events');
    const isMyOrdersSearch = input.classList.contains('my-orders');

    // live suggestion fetch on input
    input.addEventListener("input", function () {
        const query = this.value.trim();

        clearTimeout(searchTimeout);

        if (!query) {
            suggestionsBox.style.display = "none";
            return;
        }

        // fetch and display search suggestions
        searchTimeout = setTimeout(() => {
            fetch(`${suggestionRoute(isMyEventsSearch, isMyOrdersSearch)}?search=${encodeURIComponent(query)}`, {
                headers: {
                    "X-App-Request": "true"
                }
            }).then(res => res.json())
                .then(data => showSuggestions(data.results, suggestionsBox));
        }, 250);
    });

    // search submit on Enter press
    input.addEventListener("keydown", function (e) {
        if (e.key === "Enter") {
            e.preventDefault();
            searchResults(input);
        }
    });

    if (isMyEventsSearch || isMyOrdersSearch) {
        const searchIcon = input.parentElement.querySelector("i.fas.fa-search");
        if (searchIcon) {
            searchIcon.addEventListener("click", () => {
                searchResults(input);
            });
        }
    }

    // hide suggestions if user clicks somewhere outside
    document.addEventListener("click", (e) => {
        if (!input.contains(e.target) && !suggestionsBox.contains(e.target))
            suggestionsBox.style.display = "none";
    });
});

function suggestionRoute(isMyEventsSearch, isMyOrdersSearch) {
    let route;

    isMyEventsSearch ? route = '/api/search/my-events/' :
        isMyOrdersSearch ? route = '/api/search/my-orders/' :
            route = '/api/search/all/';

    return route;
}

function showSuggestions(events, suggestionsBox) {
    if (!events.length) {
        suggestionsBox.style.display = "none";
        return;
    }

    let suggestion = "";
    events.forEach(event => {
        suggestion += `
            <div class="suggestion-item" onclick="window.location='/events/${event.id}/'">
                <img src="${event.image}" class="suggestion-img">
                <div>
                    <div><strong>${event.name}</strong></div>
                    <div><small>${event.location}</small></div>
                </div>
            </div>
        `;
    });

    suggestionsBox.innerHTML = suggestion;
    suggestionsBox.style.display = "block";
}

function searchResultsRoute(isMyEventsSearch, isMyOrdersSearch) {
    let route;

    isMyEventsSearch ? route = '/events/my-events/' :
        isMyOrdersSearch ? route = '/tickets/orders/' :
            route = '/events/explore/';

    return route;
}

function searchResults(input) {
    const query = input.value.trim();
    const params = new URLSearchParams(window.location.search);

    // user searched something
    if (query.length > 0)
        params.set("search", query);

    // user cleared search input
    else
        params.delete("search");

    window.location.href = `${searchResultsRoute(isMyEventsSearch, isMyOrdersSearch)}?${params.toString()}`;
}


// filter tabs (all events, upcoming, past) for my-events & my-orders
const filterTabs = document.querySelectorAll('.filter-tab');
const params = new URLSearchParams(window.location.search);
const currentShow = params.get('show') || 'all';
const isMyEventsSearch = document.querySelector('.eventsSearch.my-events');
const isMyOrdersSearch = document.querySelector('.eventsSearch.my-orders');

filterTabs.forEach(tab => {
    if (tab.dataset.filter === currentShow)
        tab.classList.add('active');

    tab.addEventListener('click', function () {
        const filter = this.getAttribute('data-filter');

        filterTabs.forEach(t => t.classList.remove('active'));
        this.classList.add('active');

        const params = new URLSearchParams(window.location.search);
        params.set('show', filter);

        window.location.href = `${searchResultsRoute(isMyEventsSearch, isMyOrdersSearch)}?${params.toString()}`;
    });
});


// convert from UTC to user's browser timezone
function UTCtoLocalTime(utcString, element, options = undefined) {
    const localDate = new Date(utcString);

    if (options == undefined) {
        options = {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: 'numeric',
            minute: 'numeric',
            hour12: true
        };
    }
    element.innerText = localDate.toLocaleString('en-US', options);
}

// event date conversion from UTC to user's local time
export function convertDateToLocalTime() {
    document.querySelectorAll(".full-date").forEach(el => {
        UTCtoLocalTime(el.dataset.utc, el);
    });
    document.querySelectorAll(".full-date-no-week-day").forEach(el => {
        UTCtoLocalTime(el.dataset.utc, el, {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: 'numeric',
            minute: 'numeric',
            hour12: true
        })
    });
    document.querySelectorAll(".regular-date").forEach(el => {
        UTCtoLocalTime(el.dataset.utc, el, {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
        })
    });
    document.querySelectorAll(".regular-date-short-month").forEach(el => {
        UTCtoLocalTime(el.dataset.utc, el, {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
        })
    });
    document.querySelectorAll(".date-month-day").forEach(el => {
        UTCtoLocalTime(el.dataset.utc, el, { month: 'short', day: 'numeric' });
    });
    document.querySelectorAll(".date-month").forEach(el => {
        UTCtoLocalTime(el.dataset.utc, el, { month: 'short' });
    });
    document.querySelectorAll(".date-day").forEach(el => {
        UTCtoLocalTime(el.dataset.utc, el, { day: 'numeric' });
    });
}
convertDateToLocalTime()

// update fields with user timezone information for correct backend date/time processing
document.querySelectorAll(".userTimezone").forEach(inputEl => {
    inputEl.value = Intl.DateTimeFormat().resolvedOptions().timeZone;
});

// set date input with date in YYYY-MM-DD format
document.querySelectorAll(".input-date").forEach(input => {
    const utcString = input.dataset.utc;
    if (utcString) {
        const localDate = new Date(utcString);
        const yyyy = localDate.getFullYear();
        const mm = String(localDate.getMonth() + 1).padStart(2, '0');
        const dd = String(localDate.getDate()).padStart(2, '0');
        input.value = `${yyyy}-${mm}-${dd}`;
    }
});

// set time input with time in HH:MM format
document.querySelectorAll(".input-time").forEach(input => {
    const utcString = input.dataset.utc;
    if (utcString) {
        const localDate = new Date(utcString);
        const hh = String(localDate.getHours()).padStart(2, '0');
        const min = String(localDate.getMinutes()).padStart(2, '0');
        input.value = `${hh}:${min}`;
    }
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