function generateTimetableStructure() {
    const times = [...Array(10)].map((_, i) => 8 + i);
    const days = ['mon', 'tue', 'wed', 'thu', 'fri'];
    const tbody = $('#timetable-body');
    times.forEach(t => {
        const row = $('<tr></tr>');
        const timeCell = $('<td></td>').text(`${t}:00`);
        row.append(timeCell);
        days.forEach(d => {
            const cell = $('<td></td>').attr('id', `${d}-${t}`);
            row.append(cell);
        });
        tbody.append(row);
    });
}

function renderTimetable(data) {
    data.forEach(slot => {
        $(`#${slot.day}-${slot.time}`).html(
            `<div class="slot slot-${slot.type}">${slot.course} - ${slot.type}<br>Location: ${slot.location}</div>`
        );
    });
}

function renderListView(data) {
    const listViewContent = $('#listViewContent');
    listViewContent.empty();
    data.forEach(slot => {
        listViewContent.append(
            `<li class="list-group-item">${slot.course} - ${slot.type} (${slot.day.charAt(0).toUpperCase() + slot.day.slice(1)} ${slot.time}:00, ${slot.location})</li>`
        );
    });
}

function loadSchedule(scheduleId) {
    const url = scheduleId ? `/api/schedule/${scheduleId}` : '/api/schedule';
    $.get(url, function(data) {
        renderTimetable(data);
        if (!$('#listView').hasClass('d-none')) {
            renderListView(data);
        }
    }).fail(function() {
        $('#timetable-body').html('<tr><td colspan="6">Error loading schedule</td></tr>');
    });
}

$('#toggleView').click(function() {
    const isListView = $('#listView').hasClass('d-none');
    $('#listView').toggleClass('d-none', !isListView);
    $('#timetable').toggleClass('d-none', isListView);
    $(this).text(isListView ? 'Switch to Calendar View' : 'Switch to List View');
    if (isListView) {
        const scheduleId = window.scheduleId || null;
        loadSchedule(scheduleId);
    }
});

$('#exportPDF').click(function() {
    const scheduleId = window.scheduleId || null;
    $.get(scheduleId ? `/api/schedule/${scheduleId}` : '/api/schedule', function(data) {
        const { jsPDF } = window.jspdf;
        const doc = new jsPDF();
        doc.text('My Schedule', 10, 10);
        let y = 20;
        data.forEach(slot => {
            doc.text(`${slot.course} - ${slot.type} (${slot.day.charAt(0).toUpperCase() + slot.day.slice(1)} ${slot.time}:00, ${slot.location})`, 10, y);
            y += 10;
        });
        doc.save('timetable.pdf');
    });
});

$(document).ready(function() {
    generateTimetableStructure();
    const scheduleId = window.scheduleId || null;
    loadSchedule(scheduleId);
});