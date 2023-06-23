document.addEventListener('DOMContentLoaded', function() {
    flatpickr("#date-range", {
        mode: "range",
        dateFormat: "Y-m-d",
        onChange: function(selectedDates, dateStr, instance) {
            // Retrieve the start and end dates
            const startDate = selectedDates[0];
            const endDate = selectedDates[selectedDates.length - 1];

            // Use the start and end dates in your code
            // For example:
            console.log("Start Date:", startDate);
            console.log("End Date:", endDate);
        }
    });
});
