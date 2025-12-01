// calculate how many events fit in the row
function calculateEventsPerPage() {
    const gridContainer = document.querySelector('.events-grid');
    const eventCard = document.querySelector('.event-card');

    if (!gridContainer || !eventCard) return 2;

    const gridWidth = gridContainer.offsetWidth;
    const eventWidth = eventCard.offsetWidth;

    if (eventWidth === 0) return 2;
    const eventsPerRow = Math.floor(gridWidth / eventWidth);

    return eventsPerRow;
}

function updatePagination() {
    const eventsPerPage = calculateEventsPerPage();

    // update url query
    const urlParams = new URLSearchParams(window.location.search);
    urlParams.set('show', eventsPerPage);
    window.history.replaceState(null, '', '?' + urlParams.toString());
}

// pagination update
let hasReloaded = false;
window.addEventListener('load', () => {
    const currentURL = new URLSearchParams(window.location.search);
    updatePagination();

    if (!currentURL.has('show') && !hasReloaded) {
        hasReloaded = true;
        window.location.reload();
    }
});

let resizeTimeout;
window.addEventListener('resize', () => {
    updatePagination();

    if (hasReloaded)
        return;

    // wait till resizing stops and reload page
    clearTimeout(resizeTimeout);
    resizeTimeout = setTimeout(() => {
        window.location.reload();
    }, 300);
});