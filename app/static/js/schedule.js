const scheduleData = {{ schedule_data | tojson | safe }};
console.log(scheduleData+"dddddddddddddddd");  // inspect if valid
 
scheduleData.forEach(item => {
  const day = item.day_of_week.toLowerCase();
  const start = parseInt(item.start_time.split(":")[0]);
  const end = parseInt(item.end_time.split(":")[0]);
  const span = end - start;

  // Target the first cell and insert the content
  const firstCell = document.getElementById(`${day}-${start}`);
  if (firstCell) {
    firstCell.innerHTML = `
      <div class="course-cell">
        <strong>${item.unit_name}</strong><br>
        ${item.type}<br>
        ${item.start_time} - ${item.end_time}
      </div>
    `;
    firstCell.rowSpan = span;

    // Remove the following cells that are spanned over
    for (let h = start + 1; h < start + span; h++) {
      const nextCell = document.getElementById(`${day}-${h}`);
      if (nextCell) {
        nextCell.remove();  // remove merged cells to avoid duplicate display
      }
    }
  }
});
 
