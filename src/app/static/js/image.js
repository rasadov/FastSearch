function scaleImage(element) {
    var width = element.naturalWidth;
    var height = element.naturalHeight;
    var aspectRatio = width / height;
    var containerWidth = 280;
    var containerHeight = 280;

    if (aspectRatio > 1) {
        // Image is wider than it is tall
        element.style.width = containerWidth + "px";
        element.style.height = containerWidth / aspectRatio + "px";
        element.style.marginTop = (containerHeight - containerWidth / aspectRatio) / 2 + "px";
        element.style.marginBottom = (containerHeight - containerWidth / aspectRatio) / 2 + "px";
    } else {
        // Image is taller than it is wide
        element.style.width = containerHeight * aspectRatio + "px";
        element.style.height = containerHeight + "px";
    }
}