// Get URL parameters

const queryString = window.location.search;
const urlParams = new URLSearchParams(queryString);

// Search query
var search = urlParams.get('search');
document.getElementById('search').value = search;

// Min and max price
var minPrice = urlParams.get('min_price');
if (minPrice) {
document.getElementById('min_price').value = minPrice;
}
var maxPrice = urlParams.get('max_price');
if (maxPrice) {
document.getElementById('max_price').value = maxPrice;
}
// Min and max rating
var minRating = urlParams.get('min_rating');
if (minRating) {
document.getElementById('min_rating').value = minRating;
}
var maxRating = urlParams.get('max_rating');
if (maxRating) {
document.getElementById('max_rating').value = maxRating;
}
// Brand
var brand = urlParams.get('brand');
if (brand) {
document.getElementById('brand').value = brand;
}

// Function to send AJAX request to get products list
var data = {
    'filters': {
        'search': search,
        'min_price': minPrice,
        'max_price': maxPrice,
        'min_rating': minRating,
        'max_rating': maxRating,
        'brand': brand,
        'page': urlParams.get('page') ? urlParams.get('page') : 1
    }
}

var newQueryString = Object.keys(data.filters)
    .filter(key => data.filters[key] !== null && data.filters[key] !== undefined && data.filters[key] !== '')
    .map(key => key + '=' + data.filters[key])
    .join('&');

var xmr = new XMLHttpRequest();

xmr.open('GET', '/api/products?' + newQueryString, true);
xmr.setRequestHeader('Content-Type', 'application/json');

xmr.onload = function() {
    if (xmr.status == 200) {
        var response = JSON.parse(xmr.responseText);
        total_pages = response.total_pages;
        products = response.products;
        html = '<div class="flex-container" style="display:flex;">';
        len = products.length;
        for (i = 0; i < len; i++) {
            product = products[i];
            productsHTML = `
            <div class="card shadow" style="width: 30%; margin: 10px auto; border-radius: 25px; text-align: center;">
            <a href="${product.url}" style="text-decoration: none; color: black; ">
                <img src="${product.image}" class="card-img-top" alt="..." style="border-radius: 25px 25px 0px 0px; padding-top: 25px;" onload="scaleImage(this);">
                <div class="card-body">
                    <h1 class="card-title product-title" style="height: 30%">
                        ${product.title.length > 100 ? product.title.substring(0, 100) + '...' : product.title}
                    </h1>
                    <p class="card-text" style="padding: 10px; ">Price: ${product.price} ${product.currency}</p>
                    <p class="card-text" style="padding: 10px; ">Domain: ${product.domain}</p>
                    <p class="card-text" style="padding: 10px;">Rating: ${product.rating} (${product.amount_of_ratings})</p>
                    <p class="card-text" style="padding: 10px;">Category: ${product.item_class}</p>
                </a>
                    ${ is_authenticated ? `
                    <div style="margin-top: 10px;">
                        ${ product.tracked ? `
                        <button type="button" class="btn track-button tracked" id="${product.id}" data-tracked="True" onclick="track('${product.id}')">Tracked</button>
                        ` : `
                        <button type="button" class="btn track-button track" id="${product.id}" data-tracked="False" onclick="track('${product.id}')">Track</button>
                        ` }
                    </div>
                    ` : `
                    <div style="margin-top: 10px;">
                        <a href="/login" class="btn track-button btn-light btn-sm">Login to track</a>
                    </div>
                    ` }
                </div>
            </div>`
            html += productsHTML;
            if (i % 3 == 2 || i == len - 1) {
                html += `</div><div class="flex-container" style="display:flex;">`;
            }
        }
        document.getElementById('products').innerHTML = html;

        // Pagination                        
        var total_pages = response.total_pages; 
        var current_page = response.current_page;  

        var pagination = document.getElementById('pagination');

        var ul = document.createElement('ul');
        ul.className = 'pagination justify-content-center mx-auto mt-5';

        if (total_pages > 1) {
            if (total_pages > 8) {
                if (current_page < 4) {
                    for (i = 1; i <= 5; i++) {
                        var li = document.createElement('li');
                        li.className = 'page-item';
                        var a = document.createElement('a');
                        a.className = 'page-link';
                        a.href = '/search?page=' + i + '&' + newQueryString;
                        a.innerHTML = i;
                        if (i == current_page) {
                            li.classList.add('active');
                        }
                        li.appendChild(a);
                        ul.appendChild(li);
                    }
                    var li = document.createElement('li');
                    li.className = 'page-item';
                    var a = document.createElement('a');
                    a.className = 'page-link';
                    a.disabled = true;
                    a.innerHTML = '...';
                    li.appendChild(a);
                    ul.appendChild(li);
                    for (i = total_pages - 1; i <= total_pages; i++) {
                        var li = document.createElement('li');
                        li.className = 'page-item';
                        var a = document.createElement('a');
                        a.className = 'page-link';
                        a.href = '/search?page=' + i + '&' + newQueryString;
                        a.innerHTML = i;
                        li.appendChild(a);
                        ul.appendChild(li);
                    }
                }
                else if (current_page > total_pages - 3) {
                    for (i = 1; i <= 2; i++) {
                        var li = document.createElement('li');
                        li.className = 'page-item';
                        var a = document.createElement('a');
                        a.className = 'page-link';
                        a.href = '/search?page=' + i + '&' + newQueryString;
                        a.innerHTML = i;
                        li.appendChild(a);
                        ul.appendChild(li);
                    }
                    var li = document.createElement('li');
                    li.className = 'page-item';
                    var a = document.createElement('a');
                    a.className = 'page-link';
                    a.disabled = true;
                    a.innerHTML = '...';
                    li.appendChild(a);
                    ul.appendChild(li);
                    for (i = total_pages - 4; i <= total_pages; i++) {
                        var li = document.createElement('li');
                        li.className = 'page-item';
                        var a = document.createElement('a');
                        a.className = 'page-link';
                        a.href = '/search?page=' + i + '&' + newQueryString;
                        a.innerHTML = i;
                        if (i == current_page) {
                            li.classList.add('active');
                        }
                        li.appendChild(a);
                        ul.appendChild(li);
                    }
                }
                else {
                    for (i = 1; i <= 2; i++) {
                        var li = document.createElement('li');
                        li.className = 'page-item';
                        var a = document.createElement('a');
                        a.className = 'page-link';
                        a.href = '/search?page=' + i + '&' + newQueryString;
                        a.innerHTML = i;
                        li.appendChild(a);
                        ul.appendChild(li);
                    }
                    var li = document.createElement('li');
                    li.className = 'page-item';
                    var a = document.createElement('a');
                    a.className = 'page-link';
                    a.disabled = true;
                    a.innerHTML = '...';
                    li.appendChild(a);
                    ul.appendChild(li);
                    for (i = current_page - 1; i <= current_page + 1; i++) {
                        var li = document.createElement('li');
                        li.className = 'page-item';
                        var a = document.createElement('a');
                        a.className = 'page-link';
                        a.href = '/search?page=' + i + '&' + newQueryString;
                        a.innerHTML = i;
                        if (i == current_page) {
                            li.classList.add('active');
                        }
                        li.appendChild(a);
                        ul.appendChild(li);
                    }
                    var li = document.createElement('li');
                    li.className = 'page-item';
                    var a = document.createElement('a');
                    a.className = 'page-link';
                    a.disabled = true;
                    a.innerHTML = '...';
                    li.appendChild(a);
                    ul.appendChild(li);
                    for (i = total_pages - 1; i <= total_pages; i++) {
                        var li = document.createElement('li');
                        li.className = 'page-item';
                        var a = document.createElement('a');
                        a.className = 'page-link';
                        a.href = '/search?page=' + i + '&' + newQueryString;
                        a.innerHTML = i;
                        li.appendChild(a);
                        ul.appendChild(li);
                        }
                    }
                }
                else {
                    for (i = 1; i <= total_pages; i++) {
                        var li = document.createElement('li');
                        li.className = 'page-item';
                        var a = document.createElement('a');
                        a.className = 'page-link';
                        a.href = '/search?page=' + i + '&' + newQueryString; 
                        a.innerHTML = i;
                        if (i == current_page) {
                            li.classList.add('active');
                        }
                        li.appendChild(a);
                        ul.appendChild(li);
                }
            }
            pagination.appendChild(ul);
        }
        else {
            if (document.querySelectorAll('.card').length > 0) {
                var li = document.createElement('li');
                li.className = 'page-item';
                var a = document.createElement('a');
                a.className = 'page-link active';
                a.disabled = true;
                a.innerHTML = '1';
                li.appendChild(a);
                ul.appendChild(li);
                document.getElementById('pagination').appendChild(ul);
            }
        }
    }
}

if (urlParams.size > 0) {
    xmr.send();
}
else {
    document.getElementById('products').innerHTML = `
    <div class="donate-div">
        <h3>Your contribution to the development and improvement of our project will be highly appreciated!</h3> 
        <a href="${donation_link}">
            <div class="btn btn-primary" style="margin-top: 20px;">Buy me a coffee</div>      
        </a>
    </div>
    `;
}