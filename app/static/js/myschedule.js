function generateTimetableStructure(scheduleId) {
  const times = [...Array(13)].map((_, i) => 8 + i); // Hours from 8:00 to 20:00
  const days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"];
  const tbody = document.getElementById(`timetable-body-${scheduleId}`);
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
  // Generate timetables for all schedules
  if (typeof scheduleData !== "undefined") {
    scheduleData.forEach((schedule) => {
      generateTimetableStructure(schedule.id);
      renderTimetable(schedule);
    });
  }

  // Delete schedule logic with "no schedule" alert
  if (typeof uploadUnitUrl !== "undefined") {
    document.querySelectorAll('.delete-schedule-btn').forEach(function(btn) {
      btn.addEventListener('click', function() {
        if (!confirm('Are you sure you want to delete this schedule?')) return;
        const scheduleId = this.getAttribute('data-id');
        fetch(`/schedule/delete/${scheduleId}`, {
          method: 'POST',
          headers: {
            'X-Requested-With': 'XMLHttpRequest'
          }
        })
        .then(response => response.json())
        .then(data => {
          if (data.success) {
            document.getElementById(`schedule-${scheduleId}`).remove();
            if (data.no_schedule) {
              const alert = document.createElement('div');
              alert.className = 'alert alert-warning alert-dismissible fade show mt-3';
              alert.role = 'alert';
              alert.innerHTML = `
                You have no schedules left. Please <a href="${uploadUnitUrl}" class="btn btn-sm btn-primary ms-2">Upload Units</a> to generate a new schedule.
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
              `;
              // Insert alert after the h1 title
              const title = document.querySelector('main.container h1');
              if (title && title.parentNode) {
                title.parentNode.insertBefore(alert, title.nextSibling);
              } else {
                document.querySelector('main.container').prepend(alert);
              }
            }
          } else {
            alert(data.message || 'Delete failed.');
          }
        });
      });
    });
  }
});

/* 
  The following functions are for optional features like list view, search, and export.
  If you don't use these features, you can remove them.
*/

function renderListView() {
  const listViewContent = $('#listViewContent');
  listViewContent.empty();
  if (typeof timetableData !== "undefined") {
    timetableData.forEach(slot => {
      listViewContent.append(
        `<li class="list-group-item">${slot.course} - ${slot.type} (${slot.day.charAt(0).toUpperCase() + slot.day.slice(1)} ${slot.time}:00, ${slot.location})</li>`
      );
    });
  }
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
  if (typeof timetableData !== "undefined") {
    timetableData.forEach(slot => {
      doc.text(`${slot.course} - ${slot.type} (${slot.day.charAt(0).toUpperCase() + slot.day.slice(1)} ${slot.time}:00, ${slot.location})`, 10, y);
      y += 10;
    });
  }
  doc.save('timetable.pdf');
});