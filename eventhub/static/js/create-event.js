import { updateCounter } from "./general.js";

function renderPricingZone() {
    const totalForms = document.querySelector('#id_zones-TOTAL_FORMS');
    const formCount = parseInt(totalForms.value, 10);

    // create new price zone
    const zoneDraft = document.querySelector('.pricing-zone-item');
    const newZone = zoneDraft.cloneNode(true);
    clearZoneInputs(newZone, formCount);
    removeZoneErrors(newZone);
    pricingZones.appendChild(newZone);
    initiatePriceZoneCharCounters();

    // update metadata (formset)
    totalForms.value = formCount + 1;

    // setup remove on click for new zone
    const removeBtn = newZone.querySelector('.remove-zone');
    removeBtn.addEventListener('click', () => removePricingZone(newZone));
}

function clearZoneInputs(zone, formCount) {
    const zoneInputs = zone.querySelectorAll('.form-group input');
    for (const input of zoneInputs) {
        input.value = '';
        const name = input.name.replace(`zones-0-`, `zones-${formCount}-`);
        input.name = name;
        input.id = `id_${name}`;
    }
}

function initiatePriceZoneCharCounters() {
    const charCounters = document.querySelectorAll('.zoneInputCounter');
    for (const ctr of charCounters) {
        const nameInput = ctr.parentElement.parentElement.parentElement.querySelector('input');
        if (nameInput) {
            const maxLen = nameInput.getAttribute('maxlength');
            updateCounter(ctr, maxLen, nameInput);
            nameInput.addEventListener('input', () => updateCounter(ctr, maxLen, nameInput));
        }
    }
}

function removeZoneErrors(zone) {
    const errors = zone.querySelectorAll('.form-error');
    for (const e of errors)
        e.remove();
}

function removePricingZone(zone) {
    const totalForms = document.querySelector('#id_zones-TOTAL_FORMS');

    if (totalForms.value > 1) {
        // update the formset
        const deleteSignal = zone.querySelector('input[name^="zones-"][name$="-DELETE"]');
        if (deleteSignal)
            deleteSignal.value = 'on';
        totalForms.value = parseInt(totalForms.value, 10) - 1;

        // remove from DOM
        pricingZones.removeChild(zone);
    }
}

// set min date input to today (user can't create a past event)
const dateInput = document.getElementById('eventDate');
if (dateInput) {
    const currentDate = new Date();
    const day = String(currentDate.getDate()).padStart(2, '0');
    const month = String(currentDate.getMonth() + 1).padStart(2, '0');
    dateInput.min = `${currentDate.getFullYear()}-${month}-${day}`;
}


// pricing zones
// pre-rendered pricing zones forms:
//      initially there is 1 pricing zone form;
//      after any submission to backend, django will pre-renders as many forms 
//          as submitted after backend validations (if the global event creation form had errors)

// initiate char counters for all pre-rendered price zones
initiatePriceZoneCharCounters();

// setup remove on click event for all pre-rendered price zones
const removeButtons = document.querySelectorAll('.remove-zone');
for (const removeBtn of removeButtons)
    removeBtn.addEventListener('click', () => removePricingZone(removeBtn.closest('.pricing-zone-item')));

// setup price zone render on click
const pricingZones = document.getElementById('pricingZones');
const addZoneButton = document.getElementById('addPricingZone');
if (addZoneButton)
    addZoneButton.addEventListener('click', () => renderPricingZone());


// prompt event deletion alert
const deleteEventBtn = document.getElementById('deleteEventBtn');
if (deleteEventBtn) {
    deleteEventBtn.addEventListener('click', (e) => {
        if (!confirm("Are you sure you want to delete this event?\nThis cannot be undone.")) {
            e.stopImmediatePropagation();
            return;
        }
    }, true);
}