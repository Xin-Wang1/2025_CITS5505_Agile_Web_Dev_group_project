document.getElementById('apply-preferences-btn').addEventListener('click', () => {
  // Get selected preferred days
  const preferredDays = [];
  document.querySelectorAll('#preferred-days .form-check-input:checked').forEach(cb => {
    preferredDays.push(cb.value);
  });

  if (preferredDays.length === 0) {
    alert('Please select at least one preferred day.');
    return;
  }

  // Clear previous selections
  document.querySelectorAll('.timeslot-checkbox').forEach(cb => {
    cb.checked = false;
    cb.dispatchEvent(new Event('change'));
  });

  // Auto-schedule classes based on preferred days
  autoScheduleClasses(preferredDays);
});

function autoScheduleClasses(preferredDays) {
  // Iterate over all available class times
  document.querySelectorAll('.timeslot-checkbox').forEach(cb => {
    const day = cb.dataset.day;
    const type = cb.dataset.classType;

    // Always schedule lectures
    if (type === 'Lecture') {
      cb.checked = true;
      cb.dispatchEvent(new Event('change'));
    } else if (preferredDays.includes(day)) {
      // Schedule other classes on preferred days
      cb.checked = true;
      cb.dispatchEvent(new Event('change'));
    }
  });
}

document.addEventListener('DOMContentLoaded', () => {
  const selectedSlots    = [];
  const unavailableSlots = [];

  // simple [aStart,aEnd) vs [bStart,bEnd) overlap test
  function overlaps(aStart, aEnd, bStart, bEnd) {
    return !(aEnd <= bStart || aStart >= bEnd);
  }

  function hasOverlap(slots, day, s, e) {
    return slots.some(x => x.day === day && overlaps(s, e, x.startHour, x.endHour));
  }

  // 1) CLASS SELECTION logic
  document.querySelectorAll('.timeslot-checkbox').forEach(cb => {
    cb.addEventListener('change', () => {
      const day       = cb.dataset.day;
      const s         = parseInt(cb.dataset.startHour, 10);
      const e         = parseInt(cb.dataset.endHour,   10);
      const span      = e - s;
      const name      = cb.dataset.unitName;
      const type      = cb.dataset.classType;
      const classtimeId = cb.dataset.classtimeId;
      const unitId = cb.dataset.unitId;
      const firstCell = document.querySelector(`.slot-cell[data-day="${day}"][data-hour="${s}"]`);

      if (cb.checked) {
        // 1a) block conflict?
        if (hasOverlap(unavailableSlots, day, s, e)) {
          alert('⛔ That time is marked unavailable.');
          cb.checked = false;
          return;
        }
        // 1b) class conflict?
        if (hasOverlap(selectedSlots, day, s, e)) {
          alert('⚠️ This class overlaps one you already selected.');
          cb.checked = false;
          return;
        }
        const existingSelection = selectedSlots.find(
        slot => slot.unitId === unitId && slot.type === type
        );
        if (existingSelection) {
          alert(`⚠️ You can only select one ${type} for ${name}.`);
          cb.checked = false;
          return;
        }

        // record & render
        selectedSlots.push({ classtimeId, unitId, type, day, startHour: s, endHour: e }); 
        firstCell.setAttribute('rowspan', span);
        firstCell.classList.add('selected');
       
        //firstCell.textContent = `${name} (${type}) ${s}–${e}`;
        const listItem = document.createElement('li');
        listItem.className = 'list-group-item';
        listItem.innerHTML = `
        <strong>${name}</strong> - ${type} 
        (${day.charAt(0).toUpperCase() + day.slice(1)} ${s}:00–${e}:00)`;

        const listContainer = document.createElement('ul');
        listContainer.className = 'list-group';
        listContainer.appendChild(listItem);

        firstCell.innerHTML = ''; // Clear any existing content
        firstCell.appendChild(listContainer);
        for (let h = s+1; h < e; h++) {
          document.querySelector(`.slot-cell[data-day="${day}"][data-hour="${h}"]`)
                  .style.display = 'none';
        }
      } else {
        // deselect
        const idx = selectedSlots.findIndex(x => x.classtimeId === classtimeId);
        if (idx > -1) selectedSlots.splice(idx, 1);

        // un-render
        firstCell.removeAttribute('rowspan');
        firstCell.classList.remove('selected');
        firstCell.textContent = '';
        for (let h = s+1; h < e; h++) {
          document.querySelector(`.slot-cell[data-day="${day}"][data-hour="${h}"]`)
                  .style.display = '';
        }
      }
    });
  });

  // 2) ADD UNAVAILABLE handler
  document.getElementById('add-unavailable-btn').addEventListener('click', () => {
    const day = document.getElementById('unavailable-day').value;
    const timeRange = document.getElementById('unavailable-time').value;

  // Validate inputs
    if (!day || !timeRange) {
      alert('Please select a day and time range.');
      return;
    }

    const [startStr, endStr] = timeRange.split('-').map(s => s.trim());
    const s = parseInt(startStr.split(':')[0], 10);
    const e = parseInt(endStr.split(':')[0], 10);

    if (isNaN(s) || isNaN(e) || s >= e) {
      alert('Invalid time range. Please enter a valid range like "10:00-12:00".');
      return;
    }

    const span = e - s;
    const firstCell = document.querySelector(`.slot-cell[data-day="${day}"][data-hour="${s}"]`);

    if (!firstCell) {
      alert('Invalid time slot. Please ensure the selected time range is within the schedule.');
      return;
    }
    // record & render
    unavailableSlots.push({ day, startHour: s, endHour: e });
    const listItem = document.createElement('li');
    listItem.className = 'list-group-item';
    listItem.innerHTML = `
    <strong>Unavailable</strong> 
    (${day.charAt(0).toUpperCase() + day.slice(1)} ${startStr}–${endStr})
    <button class="btn btn-sm btn-danger float-end remove-unavailable-btn">Remove</button>
    `;

    const listContainer = document.createElement('ul');
    listContainer.className = 'list-group';
    listContainer.appendChild(listItem);

    firstCell.setAttribute('rowspan', span);
    firstCell.classList.add('unavailable');
    firstCell.innerHTML = ''; // Clear any existing content
    firstCell.appendChild(listContainer);

  // Hide subsequent cells in the same column
    for (let h = s + 1; h < e; h++) {
      const nextCell = document.querySelector(`.slot-cell[data-day="${day}"][data-hour="${h}"]`);
      if (nextCell) {
        nextCell.style.display = 'none';
      }
    }

  // Add event listener to the "Remove" button
    const removeButton = listItem.querySelector('.remove-unavailable-btn');
    if (removeButton) {
      removeButton.addEventListener('click', () => {
      // Remove the unavailable slot from the array
        const idx = unavailableSlots.findIndex(slot => slot.day === day && slot.startHour === s && slot.endHour === e);
        if (idx > -1) unavailableSlots.splice(idx, 1);

      // Restore the cell
        firstCell.removeAttribute('rowspan');
        firstCell.classList.remove('unavailable');
        firstCell.innerHTML = '';

      // Restore the hidden cells
        for (let h = s + 1; h < e; h++) {
          const nextCell = document.querySelector(`.slot-cell[data-day="${day}"][data-hour="${h}"]`);
          if (nextCell) {
            nextCell.style.display = '';
          }
        }
      });
    }
  });

  // 3) GENERATE SCHEDULE → inject arrays as JSON
  document.getElementById('generate-form').addEventListener('submit', (e) => {
    const container = document.getElementById('hidden-inputs');
    container.innerHTML = '';  // clear old

    const selectedInput = document.createElement('input');
    selectedInput.type = 'hidden';
    selectedInput.name = 'selected_classtime_ids';
    selectedInput.value = JSON.stringify(selectedSlots.map(slot => slot.classtimeId)); // Save only IDs
    container.appendChild(selectedInput);

  // Add unavailable slots as a hidden input (if needed)
    const unavailableInput = document.createElement('input');
    unavailableInput.type = 'hidden';
    unavailableInput.name = 'unavailable_slots';
    unavailableInput.value = JSON.stringify(unavailableSlots);
    container.appendChild(unavailableInput);
    // then form submits normally
  });
});