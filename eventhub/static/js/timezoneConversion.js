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