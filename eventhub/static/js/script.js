/* ACCOUNT */
// highlight the clicked link in the account sidebar
const accountNavLinks = document.querySelectorAll('.account-nav-link');
accountNavLinks.forEach(link => {
    link.addEventListener('click', function (e) {
        accountNavLinks.forEach(l => l.classList.remove('active'));
        this.classList.add('active');
    });
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


/* CREATE EVENT PAGE */
function updateCounter(counterField, maxLength, inputField) {
    const currentLength = inputField.value.length;
    counterField.textContent = `${currentLength} / ${maxLength} characters`;
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

// pricing zones dynamic render & removal
const pricingZonesContainer = document.getElementById('pricingZones');
const addZoneButton = document.getElementById('addPricingZone');
let zoneCount = 1;

if (addZoneButton)
    addZoneButton.addEventListener('click', function () {
        renderPricingZone();
        zoneCount++;
    });

// remove on click event for pricing zone 1
const zone1 = pricingZonesContainer.querySelector('.zone-1');
const zone1Remove = pricingZonesContainer.querySelector('.remove-zone-1');
if (zone1Remove)
    zone1Remove.addEventListener('click', () => removePricingZone(zone1));

function renderPricingZone() {
    const newZone = document.createElement('div');
    newZone.classList.add('pricing-zone-item', `zone-${zoneCount}`);

    newZone.innerHTML = `
        <div class="form-row">
            <div class="form-group">
                <div class="label-row">
                    <label for="zone_name_${zoneCount}">Zone Name</label>
                    <div class="remove-zone-${zoneCount}">
                        <i class="fas fa-times"></i>
                    </div>
                </div>
                <input type="text" name="zone_name_${zoneCount}" placeholder="e.g. General Admission">
            </div>
            <div class="form-group">
                <label for="zone_price_${zoneCount}">Price (USD)</label>
                <input type="number" name="zone_price_${zoneCount}" placeholder="0.00" min="0" step="0.01">
            </div>
            <div class="form-group">
                <label for="zone_seats_${zoneCount}">Seats</label>
                <input type="number" name="zone_seats_${zoneCount}" placeholder="Seat capacity" min="1">
            </div>
        </div>
    `;

    pricingZonesContainer.appendChild(newZone);

    const removeButton = newZone.querySelector(`.remove-zone-${zoneCount}`);
    removeButton.addEventListener('click', () => removePricingZone(newZone));
}

function removePricingZone(newZone) {
    if (zoneCount > 1) {
        pricingZonesContainer.removeChild(newZone);
        zoneCount--;
    }
}


/* FOOTER */
document.getElementById('current-year').textContent = new Date().getFullYear();