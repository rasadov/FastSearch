// This file is used to handle the profile page
document.querySelector('footer').remove()

cart = document.querySelector('.flex-container');

if (cart.children.length === 0) {
    document.querySelector('#empty').classList.remove('hidden');
}

var btn = document.querySelectorAll('.remove');





function track(product_id) {
    let button = document.getElementById(product_id);
    button.parentElement.parentElement.parentElement.parentElement.remove();

    if (cart.children.length === 0) {
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

