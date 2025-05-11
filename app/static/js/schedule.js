
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

        // record & render
        selectedSlots.push({ classtimeId }); 
        firstCell.setAttribute('rowspan', span);
        firstCell.classList.add('selected');
        firstCell.textContent = `${name} (${type}) ${s}–${e}`;
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
    const day       = document.getElementById('unavailable-day').value;
    const [startStr,endStr] = document.getElementById('unavailable-time').value
                             .split('-').map(s=>s.trim());
    const s         = parseInt(startStr.split(':')[0],10);
    const e         = parseInt(endStr.split(':')[0],10);
    const span      = e - s;
    const firstCell = document.querySelector(`.slot-cell[data-day="${day}"][data-hour="${s}"]`);

    // record & render
    unavailableSlots.push({ day, startHour: s, endHour: e });
    firstCell.setAttribute('rowspan', span);
    firstCell.classList.add('unavailable');
    firstCell.textContent = `Unavailable ${startStr}–${endStr}`;
    for (let h = s+1; h < e; h++) {
      document.querySelector(`.slot-cell[data-day="${day}"][data-hour="${h}"]`)
              .style.display = 'none';
    }

    // remove any conflicting classes
    document.querySelectorAll('.timeslot-checkbox:checked').forEach(cb => {
      const d = cb.dataset.day;
      const cs = parseInt(cb.dataset.startHour,10);
      const ce = parseInt(cb.dataset.endHour,  10);
      if (d===day && overlaps(s, e, cs, ce)) {
        cb.checked = false;
        cb.dispatchEvent(new Event('change'));
      }
    });
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