const modal = document.getElementById("eventTeamModal");
const eventTeam = modal.querySelector(".event-team");
const openModalBtns = document.querySelectorAll(".eventTeamModalOpen");
const closeModalBtn = document.getElementById("eventTeamModalClose");

const script = document.getElementById('validate-tickets-script');
const EVENT_ID = script.dataset.eventId;
const STORAGE_KEY = "eventTeamModalOpen_" + EVENT_ID;

function openModal() {
    modal.classList.add("open");
    requestAnimationFrame(() => {
        eventTeam.classList.add("open");
    });
}

function closeModal() {
    eventTeam.classList.remove("open");
    setTimeout(() => {
        modal.classList.remove("open");
    }, 250);
}

// cleanup old modal state for other events (these is always 1 modal state for the latest visited event)
Object.keys(sessionStorage).forEach(key => {
    if (key.startsWith("eventTeamModalOpen_") && key !== STORAGE_KEY)
        sessionStorage.removeItem(key);
});

// restore modal state for this event (if this event was last opened)
const savedState = sessionStorage.getItem(STORAGE_KEY);
if (savedState === "true") {
    openModal();
}

// open/close event team modal
openModalBtns.forEach(btn => {
    btn.addEventListener("click", function (e) {
        e.preventDefault();
        openModal();
        sessionStorage.setItem(STORAGE_KEY, "true");
    });
});

closeModalBtn.addEventListener("click", function (e) {
    e.preventDefault();
    closeModal();
    sessionStorage.setItem(STORAGE_KEY, "false");
});

// close event team modal if user clicks outside of the modal
modal.addEventListener("click", function (e) {
    if (!eventTeam.contains(e.target)) {
        closeModal();
        sessionStorage.setItem(STORAGE_KEY, "false");
    }
});