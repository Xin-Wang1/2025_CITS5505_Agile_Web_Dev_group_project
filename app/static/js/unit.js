let selectedUnitIds = [];

document.addEventListener('DOMContentLoaded', () => {
  const searchInput = document.getElementById('unit-search');
  const clearBtn = document.getElementById('clear-search');
  const items = Array.from(document.querySelectorAll('#unit-list li'));
  const scheduleForm = document.querySelector('form[action="/schedule/generation"]');

  // Anti-shake function, delay the execution of search filtering
  const debounce = (fn, delay = 200) => {
    let timeout;
    return (...args) => {
      clearTimeout(timeout);
      timeout = setTimeout(() => fn(...args), delay);
    };
  };

  // filter function
  const filterItems = () => {
    const q = searchInput.value.trim().toLowerCase();
    items.forEach(li => {
      const nameElement = li.querySelector('.unit-name');
      if (nameElement) { // check if nameElement exists
        const name = nameElement.textContent.toLowerCase();
        li.style.display = name.includes(q) ? '' : 'none';
      } else {
        li.style.display = 'none'; 
      }
    });
  };

  // 绑定事件
  searchInput.addEventListener('input', debounce(filterItems, 200));
  clearBtn.addEventListener('click', () => {
    searchInput.value = '';
    filterItems();
    searchInput.focus();
  });

  // Form submission validation: Check if a course is selected
  if (scheduleForm) {
    scheduleForm.addEventListener('submit', (event) => {
      if (selectedUnitIds.length === 0) {
        event.preventDefault(); // prevent form submission
        alert('choose at least one unit！');
      }
    });
  }
});

// selectUnit 
function selectUnit(name, id) {
  if (selectedUnitIds.includes(id)) {
    alert(`${name} is choosen already!`);
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
  // add to selectedUnitIds array
  selectedUnitIds.push(id);
  // update hidden input field
  document.getElementById('selected-units-input').value = JSON.stringify(selectedUnitIds);
}

// removeUnit
function removeUnit(id, button) {
  const unitItem = button.parentElement.parentElement;
  unitItem.remove();
  // remove from selectedUnitIds array
  selectedUnitIds = selectedUnitIds.filter(unitId => unitId !== id);
  // update hidden input field
  document.getElementById('selected-units-input').value = JSON.stringify(selectedUnitIds);
}