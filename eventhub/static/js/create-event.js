function updateCounter(counterField, maxLength, inputField) {
    const currentLength = inputField.value.length;
    counterField.textContent = `${currentLength} / ${maxLength} characters`;
}

function renderPricingZone() {
    const totalForms = document.querySelector('#id_zones-TOTAL_FORMS');
    const formCount = parseInt(totalForms.value, 10);

    // create new price zone
    const zoneDraft = document.querySelector('.pricing-zone-item');
    const newZone = zoneDraft.cloneNode(true);
    clearZoneInputs(newZone, formCount);
    removeZoneErrors(newZone);
    pricingZones.appendChild(newZone);
    initiateCharCounters();

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

function initiateCharCounters() {
    const charCounters = document.querySelectorAll('.zoneNameCounter');
    for (const ctr of charCounters) {
        const nameInput = ctr.parentElement.parentElement.querySelector('input');
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

// dynamic update of input characters for event name
const nameInput = document.getElementById('eventName');
const nameCounter = document.getElementById('nameCounter');
if (nameInput) {
    const nameMaxLength = nameInput.getAttribute('maxlength');
    updateCounter(nameCounter, nameMaxLength, nameInput);
    nameInput.addEventListener('input', () => updateCounter(nameCounter, nameMaxLength, nameInput));
}

// dynamic update of input characters for event description
const descTextarea = document.getElementById('eventDescription');
const descCounter = document.getElementById('descCounter');
if (descTextarea) {
    const descMaxLength = descTextarea.getAttribute('maxlength');
    updateCounter(descCounter, descMaxLength, descTextarea);
    descTextarea.addEventListener('input', () => updateCounter(descCounter, descMaxLength, descTextarea));
}


// pricing zones

// pre-rendered pricing zones forms:
//      initially there is 1 pricing zone form;
//      after any submission to backend, django will pre-renders as many forms 
//          as submitted after backend validations (if the global event creation form had errors)

// initiate char counters for all pre-rendered price zones
initiateCharCounters();

// setup remove on click event for all pre-rendered price zones
const removeButtons = document.querySelectorAll('.remove-zone');
for (const removeBtn of removeButtons)
    removeBtn.addEventListener('click', () => removePricingZone(removeBtn.closest('.pricing-zone-item')));

// setup price zone render on click
const pricingZones = document.getElementById('pricingZones');
const addZoneButton = document.getElementById('addPricingZone');
if (addZoneButton)
    addZoneButton.addEventListener('click', () => renderPricingZone());