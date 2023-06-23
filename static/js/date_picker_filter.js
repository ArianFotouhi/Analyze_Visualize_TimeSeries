var startDateInput = document.getElementById('startDate');
var endDateInput = document.getElementById('endDate');

// Add an event listener for changes in the start date input field
startDateInput.addEventListener('change', function() {
  // Get the selected date from the start date input field
  var selectedStartDate = startDateInput.value;

  // Set the value of the start date input field to the selected date
  startDateInput.value = selectedStartDate;

  // Get the selected date from the end date input field
  var selectedEndDate = endDateInput.value;

  // Set the minDate option of the end date picker to the selected start date
  flatpickr("#endDate", {
    dateFormat: "Y-m-d",
    minDate: selectedStartDate,
    // Add more options and configurations as needed
  });

  // Set the value of the end date input field to the selected end date
  endDateInput.value = selectedEndDate;
});

// Add an event listener for changes in the end date input field
endDateInput.addEventListener('change', function() {
  // Get the selected date from the end date input field
  var selectedEndDate = endDateInput.value;

  // Set the value of the end date input field to the selected date
  endDateInput.value = selectedEndDate;
});

// Initialize Flatpickr for the start date picker
flatpickr("#startDate", {
  dateFormat: "Y-m-d",
  // Add more options and configurations as needed
});

// Initialize Flatpickr for the end date picker
flatpickr("#endDate", {
  dateFormat: "Y-m-d",
  // Add more options and configurations as needed
});
