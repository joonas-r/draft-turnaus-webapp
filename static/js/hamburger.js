const hamburger = document.querySelector('.hamburger');
const menu = document.querySelector('.menu');
const icon = document.getElementById('hamburger-icon');

hamburger.addEventListener('click', function() {
    menu.classList.toggle('open');
    
    if (menu.classList.contains('open')) {
        icon.src = '/icons/close.png';
    } else {
        icon.src = '/icons/hamburger.png';
    }
});
