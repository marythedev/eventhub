// calculate how many event cards fit in the grid row
function calculateEventsPerGridRow() {
    const gridContainer = document.querySelector('.events-grid');
    const eventCard = document.querySelector('.event-card');

    if (!gridContainer || !eventCard)
        return 2;

    const gridWidth = gridContainer.offsetWidth;
    const eventWidth = eventCard.offsetWidth;

    if (eventWidth === 0)
        return 2;

    const eventsPerRow = Math.floor(gridWidth / eventWidth);

    return eventsPerRow;
}

// check if current page layout fits the optimal amount of event cards per grid row
function isUpdateNeeded() {
    const urlParams = new URLSearchParams(window.location.search);

    const eventsNum = calculateEventsPerGridRow();
    const currentEventsNum = parseInt(urlParams.get('show'), 0);

    if (eventsNum == currentEventsNum)
        return false;

    // update 'show' query parameter with optimal event card number for grid row
    urlParams.set('show', eventsNum);
    window.history.replaceState(null, '', '?' + urlParams.toString());
    return true;
}

window.addEventListener('load', () => {
    if (isUpdateNeeded())
        window.location.reload();
});

let resizeTimeout;
window.addEventListener('resize', () => {

    clearTimeout(resizeTimeout);

    resizeTimeout = setTimeout(() => {
        if (isUpdateNeeded())
            window.location.reload();
    }, 250);

});