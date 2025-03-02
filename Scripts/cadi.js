function expandImage(element) {
    // Remove 'expanded' class from all images
    document.querySelectorAll('.image').forEach(img => img.classList.remove('expanded'));
    
    // Add 'expanded' class to the clicked image
    element.classList.add('expanded');
}
