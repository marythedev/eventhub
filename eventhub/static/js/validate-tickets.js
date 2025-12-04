const resultModal = document.getElementById("validationResultModal");
const resultContent = document.getElementById("validationResult");
const closeResultModalBtn = document.getElementById("validationResultModalClose");

function closeResultModal() {
    resultModal.classList.remove("open");
    resultContent.classList.remove("open");
}

// close result modal when okay is clicked
closeResultModalBtn.addEventListener("click", function (e) {
    e.preventDefault();
    closeResultModal();
});

try {
    const eventTeamModal = document.getElementById("eventTeamModal");
    const eventTeamContent = document.getElementById("eventTeam");
    const openModalBtns = document.querySelectorAll(".eventTeamModalOpen");
    const closeEventTeamModalBtn = document.getElementById("eventTeamModalClose");

    const script = document.getElementById('validate-tickets-script');
    const EVENT_ID = script.dataset.eventId;
    const STORAGE_KEY = "eventTeamModalOpen_" + EVENT_ID;

    function openEventTeamModal() {
        eventTeamModal.classList.add("open");
        requestAnimationFrame(() => {
            eventTeamContent.classList.add("open");
        });
    }

    function closeEventTeamModal() {
        eventTeamContent.classList.remove("open");
        setTimeout(() => {
            eventTeamModal.classList.remove("open");
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
        openEventTeamModal();
    }

    // open/close event team modal
    openModalBtns.forEach(btn => {
        btn.addEventListener("click", function (e) {
            e.preventDefault();
            openEventTeamModal();
            sessionStorage.setItem(STORAGE_KEY, "true");
        });
    });

    closeEventTeamModalBtn.addEventListener("click", function (e) {
        e.preventDefault();
        closeEventTeamModal();
        sessionStorage.setItem(STORAGE_KEY, "false");
    });

    // close event team modal if user clicks outside of the modal
    eventTeamModal.addEventListener("click", function (e) {
        if (!eventTeamContent.contains(e.target)) {
            closeEventTeamModal();
            sessionStorage.setItem(STORAGE_KEY, "false");
        }
    });
} catch {/* event team modal doesn't exist (user is a team member, not organizer) */ }