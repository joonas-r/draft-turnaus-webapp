/**
 * Toggles visibility between the Team Leaderboard and Player Stats sections
 */
function showSchedule(type) {
    const leaderboard = document.getElementById('section-leaderboard');
    const players = document.getElementById('section-players');
    const leaderboardBtn = document.querySelector('.leaderboard-teams');
    const playersBtn = document.querySelector('.leaderboard-players');

    if (type === 'leaderboard') {
        leaderboard.style.display = 'block';
        players.style.display = 'none';
        leaderboardBtn.classList.add('active');
        playersBtn.classList.remove('active');
    } else {
        leaderboard.style.display = 'none';
        players.style.display = 'block';
        leaderboardBtn.classList.remove('active');
        playersBtn.classList.add('active');
    }
}

/**
 * Tracks sort state independently for each table
 */
let sortState = {
    team: { by: 'points', order: 'desc' },
    player: { by: 'points', order: 'desc' }
};

/**
 * Handles sorting for both Team and Player tables
 */
function handleSort(field, type) {
    const state = sortState[type];
    const sortInputOrder = document.getElementById(`${type}-sort-order`);
    const sortInputBy = document.getElementById(`${type}-sort-by`);

    if (state.by === field) {
        state.order = state.order === 'asc' ? 'desc' : 'asc';
    } else {
        state.by = field;
        // UPDATED LIST: Added 'draws' and 'losses'
        const descFields = [
            'points', 'wins', 'draws', 'losses', 'goals', 'assists', 
            'played_games', 'goals_for', 'goals_against', 'games', 'penalty_min', 
            'age', 'stick', 'primary_pos'
        ];
        state.order = descFields.includes(field) ? 'desc' : 'asc';
    }

    if (sortInputOrder) sortInputOrder.value = state.order;
    if (sortInputBy) sortInputBy.value = state.by;

    updateSortArrows(type);

    const eventName = type === 'team' ? 'teamFilterChanged' : 'playersFilterChanged';
    document.body.dispatchEvent(new Event(eventName));
}

/**
 * Visual updates: Arrows above text and column highlighting
 */
function updateSortArrows(type) {
    const sectionId = type === 'team' ? 'section-leaderboard' : 'section-players';
    const section = document.getElementById(sectionId);
    if (!section) return;

    const state = sortState[type];
    
    // Define fields that start as High-to-Low
    const descFields = [
            'points', 'wins', 'draws', 'losses', 'goals', 'assists', 
            'played_games', 'goals_for', 'goals_against', 'games', 'penalty_min', 
            'age', 'stick', 'primary_pos'
        ];
    const startsDesc = descFields.includes(state.by);

    // 1. Reset all headers in this section
    section.querySelectorAll('.sortable-th').forEach(th => {
        th.classList.remove('active-sort-cell');
        const indicator = th.querySelector('.sort-indicator');
        if (indicator) {
            indicator.textContent = ''; 
            indicator.classList.remove('desc');
        }
    });

    // 2. Apply active states to the current sort column
    const activeHeader = section.querySelector(`#sort-${type}-${state.by}`);
    if (activeHeader) {
        activeHeader.classList.add('active-sort-cell');
        const indicator = activeHeader.querySelector('.sort-indicator');
        
        if (indicator) {
            // Use a single consistent character
            indicator.textContent = '▼';

            // Rotation Logic:
            // If the field starts High-to-Low (desc), it is "unrotated" when order is desc.
            // If the field starts Low-to-High (asc), it is "unrotated" when order is asc.
            if (startsDesc) {
                // Pointing down (unrotated) for the primary 'desc' sort
                state.order === 'asc' ? indicator.classList.add('desc') : indicator.classList.remove('desc');
            } else {
                // Pointing down (unrotated) for the primary 'asc' sort
                state.order === 'desc' ? indicator.classList.add('desc') : indicator.classList.remove('desc');
            }
        }

        // 3. Highlight body column
        const columnIndex = activeHeader.cellIndex;
        const table = activeHeader.closest('table');
        const rows = table.querySelectorAll('tbody tr');
        rows.forEach(row => {
            Array.from(row.cells).forEach(c => c.classList.remove('active-sort-cell'));
            const cell = row.cells[columnIndex];
            if (cell) cell.classList.add('active-sort-cell');
        });
    }
}

// Re-apply highlights after HTMX content swap
document.body.addEventListener('htmx:afterSwap', function(evt) {
    if (evt.detail.target.id === 'leaderboard-tbody') {
        updateSortArrows('team');
    } else if (evt.detail.target.id === 'player-tbody') {
        updateSortArrows('player');
    }
});

// Initial load visuals
document.addEventListener('DOMContentLoaded', () => {
    updateSortArrows('team');
    updateSortArrows('player');
});