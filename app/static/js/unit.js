let selectedUnitIds = [];

function filterUnits() {
  const searchInput = document.getElementById('search').value.toLowerCase();
  const unitList = document.getElementById('unit-list').getElementsByTagName('li');
  for (let i = 0; i < unitList.length; i++) {
    const unitName = unitList[i].getElementsByTagName('span')[0].innerText.toLowerCase();
    unitList[i].style.display = unitName.includes(searchInput) ? '' : 'none';
  }
}

function selectUnit(name,id) {
  const selectedUnits = document.getElementById('selected-units');
  const unitItem = document.createElement('li');
  unitItem.className = 'list-group-item';
  unitItem.innerHTML = `
    <div>
      <strong>${name}</strong>
      <button class="btn btn-sm btn-danger float-end" onclick="removeUnit(${id}, this)">Remove</button>
    </div>
    
  `;
  selectedUnits.appendChild(unitItem);
    // Add the unit ID to the selectedUnitIds array
  selectedUnitIds.push(id);
    // Update the hidden input field with the selected unit IDs
  document.getElementById('selected-units-input').value = JSON.stringify(selectedUnitIds);
}
function removeUnit(button) {
  const unitItem = button.parentElement.parentElement;
  unitItem.remove();

  // Remove the unit ID from the selectedUnitIds array
  selectedUnitIds = selectedUnitIds.filter(unitId => unitId !== id);

  // Update the hidden input field with the selected unit IDs
  document.getElementById('selected-units-input').value = JSON.stringify(selectedUnitIds);
}