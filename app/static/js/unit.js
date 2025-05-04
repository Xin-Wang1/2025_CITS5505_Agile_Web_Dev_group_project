function filterUnits() {
  const searchInput = document.getElementById('search').value.toLowerCase();
  const unitList = document.getElementById('unit-list').getElementsByTagName('li');
  for (let i = 0; i < unitList.length; i++) {
    const unitName = unitList[i].getElementsByTagName('span')[0].innerText.toLowerCase();
    unitList[i].style.display = unitName.includes(searchInput) ? '' : 'none';
  }
}

function selectUnit(name, credits, timeSlots) {
  const selectedUnits = document.getElementById('selected-units');
  const unitItem = document.createElement('li');
  unitItem.className = 'list-group-item';
  unitItem.innerHTML = `
    <div>
      <strong>${name}</strong>
      <button class="btn btn-sm btn-link text-decoration-none" onclick="toggleDetails(this)">Show Details</button>
      <button class="btn btn-sm btn-danger float-end" onclick="removeUnit(this)">Remove</button>
    </div>
    <div class="details">
      <p>Credits: ${credits}</p>
      <p>Time Slots:</p>
      <ul>
        ${timeSlots.map(slot => `<li>${slot}</li>`).join('')}
      </ul>
    </div>
  `;
  selectedUnits.appendChild(unitItem);
}

function toggleDetails(button) {
  const details = button.parentElement.nextElementSibling;
  if (details.style.display === 'none') {
    details.style.display = 'block';
    button.innerText = 'Hide Details';
  } else {
    details.style.display = 'none';
    button.innerText = 'Show Details';
  }
}

function removeUnit(button) {
  const unitItem = button.parentElement.parentElement;
  unitItem.remove();
}