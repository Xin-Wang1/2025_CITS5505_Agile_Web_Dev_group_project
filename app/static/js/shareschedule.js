function generateTimetableStructure(scheduleId) {
  const times = [...Array(13)].map((_, i) => 8 + i); // 8:00 to 20:00
  const days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"];
  const tbody = document.getElementById(`timetable-body-${scheduleId}`);
  if (!tbody) return;
  tbody.innerHTML = ""; // 清空旧表格，避免重复

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

document.addEventListener("DOMContentLoaded", function () {
  if (typeof scheduleDataMap === "undefined") return;

  messageScheduleMap.forEach(entry => {
    const sched = scheduleDataMap[entry.scheduleId];
    if (!sched) return;

    const clonedSchedule = JSON.parse(JSON.stringify(sched)); // 深拷贝防止引用复用
    clonedSchedule.id = `message-${entry.messageId}`; // 重定义 id 以确保唯一性

    generateTimetableStructure(clonedSchedule.id);
    renderTimetable(clonedSchedule);
  });
});
