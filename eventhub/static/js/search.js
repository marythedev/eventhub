function getSearchType(input) {
    if (input.classList.contains('my-events'))
        return 'my-events';
    if (input.classList.contains('my-orders'))
        return 'my-orders';
    if (input.classList.contains('upcoming-events'))
        return 'upcoming-events';
    return 'all';
}

function getSearchResultsRoute(searchType) {
    const routes = {
        'my-events': '/events/my-events/',
        'my-orders': '/tickets/orders/',
        'upcoming-events': '/tickets/events/',
        'all': '/events/explore/'
    };
    return routes[searchType] || '/events/explore/';
}

function getSuggestionRoute(searchType) {
    const routes = {
        'my-events': '/api/search/my-events/',
        'my-orders': '/api/search/my-orders/',
        'upcoming-events': '/api/search/my-orders/',
        'all': '/api/search/all/'
    };
    return routes[searchType] || '/api/search/all/';
}

function searchResults(input, searchType) {
    const query = input.value.trim();
    const params = new URLSearchParams(window.location.search);

    // user searched something
    if (query.length > 0)
        params.set("search", query);

    // user cleared search input
    else
        params.delete("search");

    window.location.href = `${getSearchResultsRoute(searchType)}?${params.toString()}`;
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

const searchInputs = document.querySelectorAll(".eventsSearch");
const suggestionBoxes = document.querySelectorAll(".searchSuggestions");

searchInputs.forEach((input, index) => {
    const suggestionsBox = suggestionBoxes[index];
    const searchType = getSearchType(input);
    let searchTimeout = null;

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
            fetch(`${getSuggestionRoute(searchType)}?search=${encodeURIComponent(query)}`, {
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
            searchResults(input, searchType);
        }
    });

    // search submit on search icon click
    if (searchType !== 'all') {
        const searchIcon = input.parentElement.querySelector("i.fas.fa-search");
        if (searchIcon) {
            searchIcon.addEventListener("click", () => {
                searchResults(input, searchType);
            });
        }
    }

    // hide suggestions if user clicks somewhere outside
    document.addEventListener("click", (e) => {
        if (!input.contains(e.target) && !suggestionsBox.contains(e.target))
            suggestionsBox.style.display = "none";
    });
});


// filter tabs (all events, upcoming, past) for my-events, my-orders & upcoming-events
const filterTabs = document.querySelectorAll('.filter-tab');
const params = new URLSearchParams(window.location.search);
const currentShow = params.get('show') || 'all';

let filterSearchType = undefined;
for (const input of searchInputs) {
    const type = getSearchType(input);
    if (type !== 'all') {
        filterSearchType = type;
        break;
    }
}

filterTabs.forEach(tab => {
    if (tab.dataset.filter === currentShow)
        tab.classList.add('active');

    tab.addEventListener('click', function () {
        const filter = this.getAttribute('data-filter');

        filterTabs.forEach(t => t.classList.remove('active'));
        this.classList.add('active');

        const params = new URLSearchParams(window.location.search);
        params.set('show', filter);

        window.location.href = `${getSearchResultsRoute(filterSearchType)}?${params.toString()}`;
    });
});