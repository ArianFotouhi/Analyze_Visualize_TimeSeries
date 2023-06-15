$(document).ready(function() {
    // Check if the button has the 'blink' class initially
    if ($('.blink_inthub').length > 0) {
        // Check if the button was previously clicked and stored in localStorage
        var isClicked = localStorage.getItem('buttonClicked');
        
        if (!isClicked) {
            // Start the blinking animation
            var blinkInterval = setInterval(function() {
                $('.blink_inthub').toggleClass('bg-danger');
            }, 1000);
        } else {
            // Remove the blinking class if the button was clicked
            $('.blink_inthub').removeClass('bg-danger');
        }
    }

    // Add a click event listener to the button
    $('.blink_inthub').on('click', function() {
        // Stop the blinking animation
        clearInterval(blinkInterval);
        
        // Store the button click status in localStorage
        localStorage.setItem('buttonClicked', true);
    });
    
    // Check if the value of stats[1] changes
    var previousValue_cr = "{{stats[7]['very_crowded']}}"; // Replace with the actual value from your backend

    var previousValue_op = "{{stats[7]['open_to_accept']}}"; // Replace with the actual value from your backend
    
    setInterval(function() {
        // Get the updated value of stats[1] from the backend
        var updatedValue_cr = "{{stats[7]['very_crowded']}}"; // Replace with the actual value from your backend
        var updatedValue_op = "{{stats[7]['open_to_accept']}}"; // Replace with the actual value from your backend
        
        if (updatedValue_cr !== previousValue_cr || updatedValue_op!== previousValue_op) {
            // Update the previousValue and start blinking
            previousValue_cr = updatedValue_cr;
            previousValue_op = updatedValue_op;
            $('.blink_inthub').addClass('bg-danger');
        }
    }, 4000); // Check every 5 seconds
});
