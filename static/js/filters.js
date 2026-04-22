// toggle dropdown open/closed when filter button is clicked
document.querySelectorAll('.filter-btn').forEach(function(btn) {
    btn.addEventListener('click', function(e) {
        e.stopPropagation(); // prevent click from bubbling to document
        const filterName = btn.dataset.filter;
        const dropdown = document.getElementById('filter-' + filterName);

        // close all other dropdowns first
        document.querySelectorAll('.filter-dropdown').forEach(function(d) {
            if (d !== dropdown) d.classList.remove('open');
        });

        dropdown.classList.toggle('open');
    });
});

// close dropdowns when clicking anywhere else on the page
document.addEventListener('click', function() {
    document.querySelectorAll('.filter-dropdown').forEach(function(d) {
        d.classList.remove('open');
    });
});

// when any checkbox changes, update the hidden form and trigger HTMX
document.querySelectorAll('.filter-dropdown input[type="checkbox"]').forEach(function(checkbox) {
    checkbox.addEventListener('change', function() {
        updateFilters();
    });
});

function updateFilters() {
    // for each filter group collect all checked values
    const filters = ['position1', 'position2', 'stick', 'playstyle', 'license', 'invited_by'];

    filters.forEach(function(filterName) {
        const dropdown = document.getElementById('filter-' + filterName);
        const checked = dropdown.querySelectorAll('input:checked');
        const hiddenInput = document.querySelector('#filter-form input[name="' + filterName + '"]');

        // build comma separated list of checked values
        const values = Array.from(checked).map(function(cb) { return cb.value; });
        hiddenInput.value = values.join(',');
    });

    // tell HTMX to re-fetch the table with new filters
    document.body.dispatchEvent(new Event('filterChanged'));
}

// track current sort direction
let sortDirection = 'asc';

document.getElementById('sort-name').addEventListener('click', function() {
    // flip the direction
    sortDirection = sortDirection === 'asc' ? 'desc' : 'asc';

    // update the hidden input
    document.getElementById('sort-input').value = sortDirection;

    // update the arrow indicator
    const indicator = document.querySelector('#sort-name .sort-indicator');
    indicator.textContent = sortDirection === 'asc' ? '▲' : '▼';

    // trigger HTMX to re-fetch
    document.body.dispatchEvent(new Event('filterChanged'));
});