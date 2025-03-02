function expandImage(element) {
    // Remove 'expanded' class from all images
    document.querySelectorAll('.image').forEach(img => img.classList.remove('expanded'));
    
    // Add 'expanded' class to the clicked image
    element.classList.add('expanded');



    const description = element.getAttribute('data-description');

    // Update the description container
    const descriptionContainer = document.getElementById('description-container');
    const descriptionText = document.getElementById('description-text');

    if (description) {
        descriptionText.textContent = description;

        setTimeout(() => {
            const rect = element.getBoundingClientRect();
            const topPosition = rect.bottom + window.scrollY + 10; // Position below the image
            const leftPosition = rect.left + window.scrollX; // Align with the left edge of the image

            // Position the description container
            descriptionContainer.style.top = `${topPosition}px`;
            descriptionContainer.style.left = `${leftPosition}px`;

            // Show the description container
            const formattedDescription = description.replace(/\n/g, '<br>');
            console.log("Formatted Description:", formattedDescription); // Debugging: Check formatted description

            descriptionText.innerHTML = formattedDescription;
            descriptionContainer.style.display = 'block';
        }, 400);  
    }
    else {
        // Hide the description container if no description exists
        descriptionContainer.style.display = 'none';
    }
}
