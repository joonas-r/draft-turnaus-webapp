// 1. Toggle Menu
const mainFilterBtn = document.getElementById('main-filter-btn');
const mainFilterPanel = document.getElementById('main-filter-panel');

// 1. Toggle Menu
mainFilterBtn?.addEventListener('click', (e) => {
    // Simple toggle
    mainFilterPanel.classList.toggle('open');
});

// Close when clicking outside
document.addEventListener('click', (e) => {
    const isClickInsidePanel = mainFilterPanel.contains(e.target);
    const isClickOnButton = mainFilterBtn.contains(e.target);

    if (!isClickInsidePanel && !isClickOnButton) {
        mainFilterPanel.classList.remove('open');
    }
});

document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        mainFilterPanel.classList.remove('open');
    }
});

// 2. Clear Filters Button Listener
document.getElementById('clear-filters-btn')?.addEventListener('click', () => {
    document.querySelectorAll('#main-filter-panel input[type="checkbox"]').forEach(cb => cb.checked = false);
    updateFilters(); // Reset the hidden form
    mainFilterPanel.classList.remove('open');
});

// 3. Apply Filters Button Listener
document.getElementById('apply-filters-btn')?.addEventListener('click', () => {
    updateFilters(); // Collect data and trigger HTMX
    mainFilterPanel.classList.remove('open');
});

// 4. Sorting Listeners (The "event listener portion" for headers)
const sortableFields = [
    'name', 'shirt_number', 'team_id', 'primary_pos', 'secondary_pos', 
    'stick', 'age', 'experience', 'playstyle', 'licenced', 'recruiter'];
sortableFields.forEach(field => {
    document.getElementById('sort-' + field)?.addEventListener('click', () => handleSort(field));
});

function updateFilters() {
    const filters = ['team_id', 'position1', 'position2', 'stick', 'playstyle', 'licenced', 'recruiter'];
    filters.forEach(filterName => {
        // Updated to search within the new single panel structure
        const group = document.getElementById('filter-' + filterName); 
        const checked = group?.querySelectorAll('input:checked');
        const hiddenInput = document.querySelector(`#filter-form input[name="${filterName}"]`);
        
        if (hiddenInput && checked) {
            hiddenInput.value = Array.from(checked).map(cb => cb.value).join(',');
        }
    });
    // This triggers the HTMX request in the form
    document.body.dispatchEvent(new Event('filterChanged'));
}

// track current sort direction
let currentSortBy = 'name';
let currentSortOrder = 'asc';

function handleSort(field) {
    const sortInputOrder = document.getElementById('sort-input');
    const sortInputBy = document.getElementById('sort-by-input');

    if (currentSortBy === field) {
        currentSortOrder = currentSortOrder === 'asc' ? 'desc' : 'asc';
    } else {
        currentSortBy = field;
        currentSortOrder = 'asc';
    }

    sortInputOrder.value = currentSortOrder;
    sortInputBy.value = currentSortBy;

    updateSortArrows();

    document.body.dispatchEvent(new Event('filterChanged'));
}

function updateSortArrows() {
    // reset all arrows
    document.querySelectorAll('.sort-indicator').forEach(el => el.textContent = '⇅');

    // set active arrow
    const activeIndicator = document.querySelector(`#sort-${currentSortBy} .sort-indicator`)
    if (activeIndicator) {
        activeIndicator.textContent = currentSortOrder === 'asc' ? '↓' : '↑';
    }
}




// sortableFields.forEach(field => {
//     const headerElement = document.getElementById('sort-' + field);
//     if (headerElement) {
//         headerElement.addEventListener('click', () => handleSort(field));
//     }
// });
