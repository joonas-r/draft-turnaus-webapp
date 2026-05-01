const hamburger = document.querySelector('.hamburger');
const menu = document.querySelector('.menu');
const icon = document.getElementById('hamburger-icon');
const overlay = document.getElementById('menu-overlay');

function openMenu() {
    menu.classList.add('open');
    // Check if overlay exists before trying to use it
    if (overlay) overlay.classList.add('open');
    icon.src = '/icons/close.png';
}

function closeMenu() {
    menu.classList.remove('open');
    // Check if overlay exists before trying to use it
    if (overlay) overlay.classList.remove('open');
    icon.src = '/icons/hamburger.png';
}

hamburger.addEventListener('click', function() {
    if (menu.classList.contains('open')) {
        closeMenu();
    } else {
        openMenu();
    }
});

// Only add the listener if the overlay actually exists on the page
if (overlay) {
    overlay.addEventListener('click', function() {
        closeMenu();
    });
}