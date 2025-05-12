let selectedUnitIds = [];

document.addEventListener('DOMContentLoaded', () => {
  const searchInput = document.getElementById('unit-search');
  const clearBtn = document.getElementById('clear-search');
  const items = Array.from(document.querySelectorAll('#unit-list li'));

  // debounce helper
  const debounce = (fn, delay = 200) => {
    let timeout;
    return (...args) => {
      clearTimeout(timeout);
      timeout = setTimeout(() => fn(...args), delay);
    };
  };

  // actual filter logic
  const filterItems = () => {
  const q = searchInput.value.trim().toLowerCase();
  items.forEach(li => {
    const nameElement = li.querySelector('.unit-name');
    if (nameElement) { // Check if the .unit-name element exists
      const name = nameElement.textContent.toLowerCase();
      li.style.display = name.includes(q) ? '' : 'none';
    } else {
      li.style.display = 'none'; // Hide items without a .unit-name element
    }
  });
};

  // wire up events
  searchInput.addEventListener('input', debounce(filterItems, 200));
  clearBtn.addEventListener('click', () => {
    searchInput.value = '';
    filterItems();
    searchInput.focus();
  });
});


function selectUnit(name,id) {
  if (selectedUnitIds.includes(id)) {
    alert(`${name} is already selected.`);
    return;
  }
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
function removeUnit(id,button) {
  const unitItem = button.parentElement.parentElement;
  unitItem.remove();

  // Remove the unit ID from the selectedUnitIds array
  selectedUnitIds = selectedUnitIds.filter(unitId => unitId !== id);

  // Update the hidden input field with the selected unit IDs
  document.getElementById('selected-units-input').value = JSON.stringify(selectedUnitIds);
}