$(document).ready(function() {
    // Check if the button has the 'blink' class initially
    if ($('.blink_dorm').length > 0) {
        // Check if the button was previously clicked and stored in localStorage
        var isClicked = localStorage.getItem('buttonClicked');
        
        if (!isClicked) {
            // Start the blinking animation
            var blinkInterval = setInterval(function() {
                $('.blink_dorm').toggleClass('bg-danger');
            }, 1000);
        } else {
            // Remove the blinking class if the button was clicked
            $('.blink_dorm').removeClass('bg-danger');
        }
    }

    // Add a click event listener to the button
    $('.blink_dorm').on('click', function() {
        // Stop the blinking animation
        clearInterval(blinkInterval);
        
        // Store the button click status in localStorage
        localStorage.setItem('buttonClicked', true);
    });
    
    // Check if the value of stats[1] changes
    var previousValue = '{{ stats[1] }}'; // Replace with the actual value from your backend
    setInterval(function() {
        // Get the updated value of stats[1] from the backend
        var updatedValue = '{{ stats[1] }}'; // Replace with the actual value from your backend
        
        if (updatedValue !== previousValue && updatedValue!== 0) {
            // Update the previousValue and start blinking
            previousValue = updatedValue;
            $('.blink_dorm').addClass('bg-danger');
        }
    }, 4000); // Check every 5 seconds
});
