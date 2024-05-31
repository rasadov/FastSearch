window.dataLayer = window.dataLayer || [];
function gtag(){dataLayer.push(arguments);}
gtag('js', new Date());

gtag('config', 'G-JR49X8W548');

let flashClose = document.querySelectorAll('.flash-close');
let message = document.querySelector('.alert');
flashClose.forEach((close) => {
    close.addEventListener('click', () => {
        message.parentElement.style.display = 'none';
    });
});

let navbarToggle = document.querySelector('.navbar-toggler');
let navbarCollapse = document.querySelector('.navbar-collapse');

navbarToggle.addEventListener('click', () => {
    navbarCollapse.classList.toggle('show');
});


function close(element) {
    element.parentElement.style.display = 'none';
}