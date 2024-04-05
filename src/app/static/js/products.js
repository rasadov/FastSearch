// Get URL parameters

const queryString = window.location.search;
const urlParams = new URLSearchParams(queryString);

// Search query
var search = urlParams.get('search');
document.getElementById('search').value = search;

// Min and max price
var minPrice = urlParams.get('max_price');
if (minPrice) {
document.getElementById('min_price').value = minPrice;
}
var maxPrice = urlParams.get('min_price');
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
        'brand': brand
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
        console.log("success")
        var response = JSON.parse(xmr.responseText);
        console.log(response);

        if (response.content == "products") {
        total_pages = response.total_pages;
        products = response.products;
        html = '<div style="display:flex;">';
        for (i = 0; i < products.length; i++) {
            product = products[i];
            console.log(product);
            productsHTML = `
            <div class="card shadow" style="width: 30%; margin: 10px auto; border-radius: 25px; text-align: center;">
            <a href="${products[i].url}" style="text-decoration: none; color: black; ">
                <img src="${products[i].image}" class="card-img-top" alt="..." style="border-radius: 25px 25px 0px 0px; padding-top: 25px;" onload="scaleImage(this);">
                <div class="card-body">
                    <h1 class="card-title product-title">
                        ${products[i].title.length > 100 ? products[i].title.substring(0, 100) + '...' : products[i].title}
                    </h1>
                    <p class="card-text" style="padding: 10px; ">Price: ${products[i].price}</p>
                    <p class="card-text" style="padding: 10px; ">Domain: ${products[i].domain}</p>
                    <p class="card-text" style="padding: 10px;">Rating: ${products[i].rating} (${products[i].amount_of_ratings})</p>
                    <p class="card-text" style="padding: 10px;">Category: ${products[i].item_class}</p>
                </a>
                        ${ is_authenticated ? `
                        <div style="margin-top: 10px;">
                            <form>
                                <button type="button" class="btn track-button" id="${products[i].id}" data-tracked="${products[i].tracked}" onclick="track('${products[i].id}')">Tracked</button>
                            </form>
                        </div>
                        ` : `
                        <div style="margin-top: 10px;">
                            <a href="/login" class="btn btn-light btn-sm">Login to track</a>
                        </div>
                        ` }
                    </div>
                </div>`
                html += productsHTML;
                if (i % 3 == 2 || i == products.length - 1) {
                    html += `</div><div style="display:flex;">`;
                }
            }
        document.getElementById('products').innerHTML = html;
        }
    }
}
xmr.send();
