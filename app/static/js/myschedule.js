 

function generateTimetableStructure(scheduleId) {
  const times = [...Array(13)].map((_, i) => 8 + i); // Hours from 8:00 to 20:00
  const days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"];
  const tbody = document.getElementById(`timetable-body-${scheduleId}`);
  // const tbody = document.getElementById(`timetable-body-message-${scheduleId}`);

  times.forEach((hour) => {
    const row = document.createElement("tr");
    const timeCell = document.createElement("td");
    timeCell.textContent = `${hour}:00 – ${hour + 1}:00`;
    row.appendChild(timeCell);
    days.forEach((day) => {
      const cell = document.createElement("td");
      cell.id = `schedule-${scheduleId}-${day}-${hour}`;
      row.appendChild(cell);
    });
    tbody.appendChild(row);
  });
}

function renderTimetable(schedule) {
  schedule.classtimes.forEach((classtime) => {
    const startHour = parseInt(classtime.start_time.split(":")[0]);
    const cellId = `schedule-${schedule.id}-${classtime.day_of_week}-${startHour}`;
    const cell = document.getElementById(cellId);
    if (cell) {
      cell.innerHTML = `
        <div class="slot slot-${classtime.type.toLowerCase()}">
          <strong>${classtime.unit_name}</strong><br>
          ${classtime.type}<br>
          ${classtime.start_time} – ${classtime.end_time}
        </div>
      `;
    }
  });
}

$(document).ready(function () {
  // Iterate over all schedules and generate their timetables
  scheduleData.forEach((schedule) => {
    generateTimetableStructure(schedule.id);
    renderTimetable(schedule);
  });
});

function renderListView() {
  const listViewContent = $('#listViewContent');
  listViewContent.empty();
  timetableData.forEach(slot => {
    listViewContent.append(
      `<li class="list-group-item">${slot.course} - ${slot.type} (${slot.day.charAt(0).toUpperCase() + slot.day.slice(1)} ${slot.time}:00, ${slot.location})</li>`
    );
  });
}

$('#toggleView').click(function () {
  const isListView = $('#listView').hasClass('d-none');
  $('#listView').toggleClass('d-none', !isListView);
  $('#timetable').toggleClass('d-none', isListView);
  $(this).text(isListView ? 'Switch to Calendar View' : 'Switch to List View');
  if (isListView) renderListView();
});

$('#searchInput').on('input', function () {
  const query = $(this).val().toLowerCase();
  $('.slot').each(function () {
    const text = $(this).text().toLowerCase();
    $(this).parent().toggle(text.includes(query));
  });
});

$('#exportPDF').click(function () {
  const { jsPDF } = window.jspdf;
  const doc = new jsPDF();
  doc.text('My Schedule', 10, 10);
  let y = 20;
  timetableData.forEach(slot => {
    doc.text(`${slot.course} - ${slot.type} (${slot.day.charAt(0).toUpperCase() + slot.day.slice(1)} ${slot.time}:00, ${slot.location})`, 10, y);
    y += 10;
  });
  doc.save('timetable.pdf');
});

function showRenamePrompt(button) {
  const scheduleId = button.getAttribute("data-id");
  const currentName = button.getAttribute("data-name");

  const newName = prompt("Enter new name for the schedule:", currentName);
  if (newName && newName.trim() !== "" && newName !== currentName) {
    renameSchedule(scheduleId, newName.trim());
  }
}

function renameSchedule(scheduleId, newName) {
  fetch(`/schedule/rename/${scheduleId}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-Requested-With': 'XMLHttpRequest'
    },
    body: JSON.stringify({ new_name: newName })
  })
  .then(res => res.json())
  .then(data => {
    if (data.success) {
      document.getElementById(`schedule-name-${scheduleId}`).textContent = newName;
      alert("Schedule renamed successfully.");
    } else {
      alert("Rename failed: " + (data.message || "Unknown error."));
    }
  })
  .catch(err => {
    console.error("Rename error:", err);
    alert("Error occurred while renaming.");
  });
}
