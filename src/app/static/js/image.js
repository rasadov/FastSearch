function scaleImage(element) {
    var width = element.naturalWidth;
    var height = element.naturalHeight;
    var aspectRatio = width / height;
    var containerWidth = 280;
    var containerHeight = 280;
    

    if (height < containerHeight) {
            var margin = (containerHeight - height) / 2 ;
            element.style.marginTop = (margin + 20) + "px";
            element.style.marginBottom = margin + "px";
        }
    
    if (aspectRatio > 1) {
        element.style.width = containerWidth + 'px';
        element.style.height = containerWidth / aspectRatio + 'px';
    } else {
        element.style.width = containerHeight * aspectRatio + 'px';
        element.style.height = containerHeight + 'px';                
    }
}