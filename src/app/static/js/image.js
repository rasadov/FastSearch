function scaleImage() {
    var images = document.querySelectorAll('.card-img-top');
    images.forEach(function(image) {
        var width = image.naturalWidth;
        var height = image.naturalHeight;
        var aspectRatio = width / height;
        var containerWidth = 300;
        var containerHeight = 300;

        if (height < containerHeight) {
                var margin = (containerHeight - height) / 2;
                console.log(margin);
                console.log(containerHeight);
                console.log(image);   
                image.style.marginTop = margin + "px";
                image.style.marginBottom = margin + "px";
            }
        
        if (aspectRatio > 1) {
            image.style.width = containerWidth + 'px';
            image.style.height = containerWidth / aspectRatio + 'px';
        } else {
            image.style.width = containerHeight * aspectRatio + 'px';
            image.style.height = containerHeight + 'px';                
        }
    });
}

window.addEventListener('load', scaleImage);
window.addEventListener('resize', scaleImage);