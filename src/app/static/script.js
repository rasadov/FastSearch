// Get the nav element
const nav = document.querySelector('nav');

// Add a class to the nav element when the page is scrolled
window.addEventListener('scroll', () => {
    if (window.scrollY > 0) {
        nav.classList.add('scrolled');
    } else {
        nav.classList.remove('scrolled');
    }
});