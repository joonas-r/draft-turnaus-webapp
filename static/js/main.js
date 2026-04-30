function showSchedule(type) {
    const lohkot = document.getElementById('section-lohkot');
    const jatko = document.getElementById('section-jatko');
    const lohkoBtn = document.querySelector('.leaderboard-division');
    const jatkoBtn = document.querySelector('.leaderboard-league');

    if (type === 'lohkot') {
        lohkot.style.display = 'block';
        jatko.style.display = 'none';
        lohkoBtn.classList.add('active');
        jatkoBtn.classList.remove('active');
    } else {
        lohkot.style.display = 'none';
        jatko.style.display = 'block';
        lohkoBtn.classList.remove('active');
        jatkoBtn.classList.add('active');
    }
}
