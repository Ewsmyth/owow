function addIngredient() {
  const container = document.getElementById('ingredients-container');
  const div = document.createElement('div');
  div.className = 'ingredient-row';
  div.innerHTML = `
    <div class="one-ing-wrap">
      <input class="one-ing-input" type="text" name="ingredient[]" placeholder="Ingredient" list="ingredient-options" required>
      <input class="one-amount-input" type="number" name="amount[]" placeholder="#" required>
      <select class="one-select-input" name="unit[]">
        <option value="cups">cups</option>
        <option value="oz">oz</option>
        <option value="tbsp">tbsp</option>
        <option value="tsp">tsp</option>
        <option value="grams">grams</option>
        <option value="ml">ml</option>
        <option value="liters">liters</option>
        <option value="pieces">pieces</option>
        <option value="lbs">lbs</option>
      </select>
    </div>
  `;
  container.appendChild(div);
}

// variables for the custom cuisine, allows user to make their own that is not listed
const selectEl = document.getElementById("cuisine");
const customInput = document.getElementById("custom-cuisine");

selectEl.addEventListener("change", () => {
  if (selectEl.value === "other") {
    customInput.style.display = "block";
    customInput.required = true;
  } else {
    customInput.style.display = "none";
    customInput.required = false;
    customInput.value = ""; // Clear if previously used
  }
});


// Function for the prep time and cook time inputs that auto formats the time
function formatTimeInput(input) {
  input.addEventListener('input', () => {
    let val = input.value.replace(/[^\d]/g, '').slice(0, 4);
    if (val.length >= 3) {
      input.value = val.slice(0, 2) + ':' + val.slice(2);
    } else if (val.length >= 1) {
      input.value = val;
    }
  });

  input.addEventListener('blur', () => {
    const [h, m] = input.value.split(':');
    const hours = Math.min(23, Math.max(0, parseInt(h || '0')));
    const minutes = Math.min(59, Math.max(0, parseInt(m || '0')));
    input.value = `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}`;
  });
}

formatTimeInput(document.getElementById('prepTimeInput'));
formatTimeInput(document.getElementById('cookTimeInput'));