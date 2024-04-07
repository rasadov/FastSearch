// This file is used to handle the profile page
document.querySelector('footer').remove()

if (cart.children.length === 0) {
    document.querySelector('#empty').classList.remove('hidden');
}

var btn = document.querySelectorAll('.remove');


function is_empty() {
    if (document.querySelectorAll('.product').length === 0) {
        document.querySelector('#empty').classList.remove('hidden');
    }
}

is_empty();

function track(product_id) {
    let button = document.getElementById(product_id);
    button.parentElement.parentElement.parentElement.remove();
    is_empty();

    var xhr = new XMLHttpRequest();

    xhr.open('POST', '/cart/add', true);

    xhr.setRequestHeader('Content-Type', 'application/json');

    xhr.send(JSON.stringify({
        product_id: product_id,
        action: 'remove'
    }));
}

