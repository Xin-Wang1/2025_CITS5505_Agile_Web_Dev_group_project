const scheduleData = [
  { course: "Introduction to Programming", day: "Monday", time: "9:00 - 10:30", credits: 3 },
  { course: "Data Structures", day: "Tuesday", time: "11:00 - 12:30", credits: 3 },
  { course: "Software Engineering", day: "Wednesday", time: "14:00 - 15:30", credits: 4 },
];

scheduleData.forEach(item => {
  const [startHour] = item.time.split(" - ").map(t => parseInt(t.split(":")[0]));
  const cell = document.getElementById(`${item.day.toLowerCase()}-${startHour}`);
  if (cell) {
    cell.innerHTML = `
      <div class="course-cell">
        <strong>${item.course}</strong><br>
        Credits: ${item.credits}<br>
        ${item.time}<br>
        ${item.day}
      </div>
    `;
  }
});