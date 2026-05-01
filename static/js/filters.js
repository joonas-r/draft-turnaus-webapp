// filters_7.js

// 1. Toggle Menu Logic
const mainFilterBtn = document.getElementById('main-filter-btn');
const mainFilterPanel = document.getElementById('main-filter-panel');

if (mainFilterBtn && mainFilterPanel) {
    mainFilterBtn.addEventListener('click', (e) => {
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

    // Close on Escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            mainFilterPanel.classList.remove('open');
        }
    });
}

// 2. Clear Filters Button Listener
document.getElementById('clear-filters-btn')?.addEventListener('click', () => {
    document.querySelectorAll('#main-filter-panel input[type="checkbox"]').forEach(cb => cb.checked = false);
    updateFilters(); // Reset the hidden form values
    mainFilterPanel.classList.remove('open');
});

// 3. Apply Filters Button Listener
document.getElementById('apply-filters-btn')?.addEventListener('click', () => {
    updateFilters(); // Sync data to form and trigger HTMX request
    mainFilterPanel.classList.remove('open');
});

// 4. Sorting State & Listeners
let currentSortBy = 'team_id';
let currentSortOrder = 'asc';

const sortableFields = [
    'name', 'shirt_number', 'team_id', 'primary_pos', 'secondary_pos', 
    'stick', 'age', 'experience', 'playstyle', 'licenced', 'recruiter'
];

sortableFields.forEach(field => {
    document.getElementById('sort-' + field)?.addEventListener('click', () => handleSort(field));
});

/**
 * Syncs checkbox states to the hidden HTMX filter form
 */
function updateFilters() {
    const filters = ['team_id', 'position1', 'position2', 'stick', 'playstyle', 'licenced', 'recruiter'];
    filters.forEach(filterName => {
        const group = document.getElementById('filter-' + filterName); 
        const checked = group?.querySelectorAll('input:checked');
        const hiddenInput = document.querySelector(`#filter-form input[name="${filterName}"]`);
        
        if (hiddenInput) {
            hiddenInput.value = checked ? Array.from(checked).map(cb => cb.value).join(',') : '';
        }
    });
    // Trigger the hx-get request on the form
    document.body.dispatchEvent(new Event('filterChanged'));
}

/**
 * Handles sort logic and updates hidden sort inputs
 */
function handleSort(field) {
    const sortInputOrder = document.getElementById('sort-input');
    const sortInputBy = document.getElementById('sort-by-input');

    if (currentSortBy === field) {
        currentSortOrder = currentSortOrder === 'asc' ? 'desc' : 'asc';
    } else {
        currentSortBy = field;
        
        // NEW: Define which fields should start as Descending (High-to-Low)
        const descFields = ['age', 'experience', 'shirt_number'];
        currentSortOrder = descFields.includes(field) ? 'desc' : 'asc';
    }

    if (sortInputOrder) sortInputOrder.value = currentSortOrder;
    if (sortInputBy) sortInputBy.value = currentSortBy;

    updateSortArrows();
    document.body.dispatchEvent(new Event('filterChanged'));
}

/**
 * Manages the vertical UI (Arrow above text and column highlighting)
 */
function updateSortArrows() {
    const table = document.querySelector('.player-table');
    if (!table) return;

    table.querySelectorAll('.sortable-th').forEach(th => {
        th.classList.remove('active-sort-cell');
        const indicator = th.querySelector('.sort-indicator');
        if (indicator) {
            indicator.textContent = ''; // Clear text if you're switching to icons
            indicator.classList.remove('desc'); // Reset rotation
        }
    });

    const activeHeader = document.getElementById('sort-' + currentSortBy);
    if (activeHeader) {
        activeHeader.classList.add('active-sort-cell');
        const activeIndicator = activeHeader.querySelector('.sort-indicator');
        
        if (activeIndicator) {
            // Use a consistent arrow character
            activeIndicator.textContent = '▼'; 

            // Logic to determine if it should be rotated
            // If the current order is 'desc', add the class to trigger the 180deg rotation
            if (currentSortOrder === 'desc') {
                activeIndicator.classList.add('desc');
            } else {
                activeIndicator.classList.remove('desc');
            }
        }

        // 2. Highlight the specific body column
        const columnIndex = activeHeader.cellIndex;
        const rows = table.querySelectorAll('tbody tr');
        rows.forEach(row => {
            Array.from(row.cells).forEach(c => c.classList.remove('active-sort-cell'));
            const cell = row.cells[columnIndex];
            if (cell) cell.classList.add('active-sort-cell');
        });
    }
}

// Initialize visuals on load
document.addEventListener('DOMContentLoaded', () => {
    updateSortArrows();
});

// Re-apply column highlighting after HTMX content swap
document.body.addEventListener('htmx:afterSwap', function(evt) {
    if (evt.detail.target.id === 'player-tbody') {
        updateSortArrows();
    }
});