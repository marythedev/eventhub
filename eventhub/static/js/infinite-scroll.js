import { convertDateToLocalTime } from './general.js';

const eventsWrapper = document.getElementById('events-wrapper');
const eventsGrid = document.getElementById('eventsGrid');
const loadingIndicator = document.getElementById('loadingIndicator');

let pageCounter = 1;
let moreEventsAvailable = true;
let isLoading = false;

function truncate(str, maxLength) {
    let resultStr;

    if (str.length > maxLength)
        resultStr = str.slice(0, maxLength) + '…';
    else
        resultStr = str;

    return resultStr;
}

function getEventHtml(event) {
    return `
        <a href="/events/${event.id}/">
            <div class="event-card">
                <div class="event-image">
                    <img src="${event.image_url}" alt="${event.name}">
                    ${event.badge ? `<div class="event-badge ${event.badge.toLowerCase()}">${event.badge}</div>` : ''}
                </div>

                <div class="event-content">
                    <div class="event-description">
                        <div class="event-date">
                            <span class="date-day" data-utc="${event.date}"></span>
                            <span class="date-month" data-utc="${event.date}"></span>
                        </div>

                        <div class="event-info">
                            <h3>${event.name}</h3>
                            <p class="event-location"><i class="fas fa-map-marker-alt"></i>
                                ${truncate(event.location, 50)}
                            </p>
                            <p class="event-category"><i class="fas ${event.category_icon}"></i>
                                ${event.category_label}
                            </p>
                        </div>
                    </div>

                    <div class="event-footer">
                        <span class="event-price ${event.min_price == 0 ? 'free' : ''}">
                            ${event.min_price != 0 ? `From $${event.min_price.toFixed(2)}` : 'Free'}
                        </span>

                        <button class="btn-primary btn-small">
                            ${event.min_price == 0 ? `Reserve Spot` : 'Get Tickets'}
                        </button>
                    </div>
                </div>
            </div>
        </a>
    `;
}

async function fetchMoreEvents() {
    const params = new URLSearchParams(window.location.search);
    params.set('page', pageCounter);

    const response = await fetch(`/api/load-events/?${params.toString()}`);
    return await response.json();
}

function appendEventsToGrid(events) {
    events.forEach(event => {
        const html = getEventHtml(event);
        eventsGrid.insertAdjacentHTML('beforeend', html);
    });

    convertDateToLocalTime();
}


window.addEventListener('scroll', async () => {
    if (!moreEventsAvailable || isLoading)
        return;

    const scrollPosition = eventsWrapper.scrollTop + eventsWrapper.clientHeight;
    const eventsWrapperHeight = eventsWrapper.scrollHeight;

    if (scrollPosition >= eventsWrapperHeight - 10) {

        // display loading indicator as user scrolls to the end of the page
        isLoading = true;
        loadingIndicator.classList.add('active');

        pageCounter++;
        const data = await fetchMoreEvents();
        appendEventsToGrid(data.events);

        loadingIndicator.classList.remove('active');
        isLoading = false;

        moreEventsAvailable = data.has_next;
    }
});