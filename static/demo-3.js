document.addEventListener("DOMContentLoaded", function () {
    // Get the current URL
    const currentUrl = window.location.href;

    // Extract the ID using regex
    const match = currentUrl.match(/\/pet\/([^\/]+)\/view/);
    const petId = match ? match[1] : null;

    // Get the button element
    const aiChatIcon = document.getElementById('ai-chat-icon');

    // Dynamically set the href based on petId
    if (aiChatIcon) {
        const newHref = '/pet/1a4b3d72/prompt';
        aiChatIcon.setAttribute('data-href', newHref); // Set a data-href attribute
        aiChatIcon.addEventListener("click", function () {
            window.location.href = newHref; // Perform navigation on click
        });
    }
});