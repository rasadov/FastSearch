document.querySelector('form').addEventListener('submit', function(e) {
    e.preventDefault();
    var search = document.getElementById('search').value;
    var min_price = document.getElementById('min_price').value;
    var max_price = document.getElementById('max_price').value;
    var brand = document.getElementById('brand').value;
    var min_rating = document.getElementById('min_rating').value;
    var max_rating = document.getElementById('max_rating').value;
    
    var url = '/search?';
    if (search) {
        url += 'search=' + search;
    }
    if (min_price) {
        url += '&min_price=' + min_price;
    }
    if (max_price) {
        url += '&max_price=' + max_price;
    }
    if (brand) {
        url += '&brand=' + brand;
    }
    if (min_rating) {
        url += '&min_rating=' + min_rating;
    }
    if (max_rating) {
        url += '&max_rating=' + max_rating;
    }
    window.location.href = url;
});