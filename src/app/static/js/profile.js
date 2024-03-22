// body = document.querySelector('body');
// body.style.backgroundColor = 'rgb(47, 47, 47)';
// console.log(document.querySelector('nav'));
// document.querySelector('nav').style.backgroundColor = 'transparent';
// document.querySelector('nav').classList.remove('bg-dark')
document.querySelector('footer').remove()

cart = document.querySelector('.flex-container');

function track(product_id) {
    let button = document.getElementById(product_id);
    button.parentElement.parentElement.parentElement.parentElement.remove();
    if (cart.children.length == 0) {
        document.querySelector('#empty').classList.remove('hidden');
    }


    var xhr = new XMLHttpRequest();

    xhr.open('POST', '/cart/add', true);

    xhr.setRequestHeader('Content-Type', 'application/json');

    xhr.send(JSON.stringify({
        product_id: product_id,
        action: 'remove'
    }));
}

