const timetableData = [
  { day: 'mon', time: 8, course: 'COMP101', type: 'lecture', location: 'Room 101' },
  { day: 'tue', time: 9, course: 'MATH201', type: 'tutorial', location: 'Room 202' },
  { day: 'wed', time: 10, course: 'PHYS301', type: 'lab', location: 'Lab A' },
  { day: 'thu', time: 11, course: 'COMP101', type: 'tutorial', location: 'Room 103' },
  { day: 'fri', time: 14, course: 'MATH201', type: 'lecture', location: 'Room 204' }
];

function generateTimetableStructure() {
  const times = [...Array(10)].map((_, i) => 8 + i);
  const days = ['mon', 'tue', 'wed', 'thu', 'fri'];
  const tbody = document.getElementById('timetable-body');
  times.forEach(t => {
    const row = document.createElement('tr');
    const timeCell = document.createElement('td');
    timeCell.textContent = `${t}:00`;
    row.appendChild(timeCell);
    days.forEach(d => {
      const cell = document.createElement('td');
      cell.id = `${d}-${t}`;
      row.appendChild(cell);
    });
    tbody.appendChild(row);
  });
}

function renderTimetable() {
  timetableData.forEach(slot => {
    $(`#${slot.day}-${slot.time}`).html(
      `<div class="slot slot-${slot.type}">${slot.course} - ${slot.type}<br>Location: ${slot.location}</div>`
    );
  });
}

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

$(document).ready(function () {
  generateTimetableStructure();
  renderTimetable();
});
