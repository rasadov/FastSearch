window.dataLayer = window.dataLayer || [];
function gtag(){dataLayer.push(arguments);}
gtag('js', new Date());

gtag('config', 'G-JR49X8W548');

let navbarToggle = document.querySelector('.navbar-toggler');
let navbarCollapse = document.querySelector('.navbar-collapse');

navbarToggle.addEventListener('click', () => {
    navbarCollapse.classList.toggle('show');
});

var aboutDiv = document.getElementById('about-text');
var aboutP = document.createElement('p');
aboutP.setAttribute('class', 'lead');

aboutP.innerHTML = `
                  Abyssara is a price tracking service that allows users
                  to track prices of products on different marketplaces.
                  There are a lot of marketplaces currently and it takes a significant 
                  amount of time to research the market to find a good deal.
                  Good deals could be found on different marketplaces, and
                  it is hard to track prices of all products on all marketplaces manually.
                  Meanwhile, a good deal could save up to thousands of dollars.
                  That's why we decided to create an application that
                  would allow users to find the best deal and save time.
                  Abyssara's main goal is to put an end to this problem.
                  Since its launch, Abyssara has been helping users find 
                  the best deals on the market and save money.`;

aboutDiv.appendChild(aboutP);
