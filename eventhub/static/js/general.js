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
document.querySelectorAll(".date-month").forEach(el => {
    UTCtoLocalTime(el.dataset.utc, el, { month: 'short' });
});
document.querySelectorAll(".date-day").forEach(el => {
    UTCtoLocalTime(el.dataset.utc, el, { day: 'numeric' });
});

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

// footer dynamic year update
document.addEventListener("DOMContentLoaded", () => {
    const footerYear = document.getElementById("current-year");
    if (footerYear) {
        footerYear.textContent = new Date().getFullYear();
    }
});