$(document).ready(function() {

    function calculatePlotsPerRow() {
        var windowWidth = window.innerWidth;
        var plotWidth = 350; // Width of each plot in pixels
        var margin = 20; // Margin between plots in pixels
      
        // Calculate the number of plots per row
        var plotsPerRow = Math.floor((windowWidth - margin) / (plotWidth + margin));
      
        return plotsPerRow;
    }
      
    // Usage example
    

    function createGradientDefs(svg, gradientId, startColor, endColor) {
        var gradient = svg.append("linearGradient")
            .attr("id", gradientId)
            .attr("gradientUnits", "userSpaceOnUse")
            .attr("x1", "0%")
            .attr("y1", "0%")
            .attr("x2", "0%")
            .attr("y2", "100%");

        gradient.append("stop")
            .attr("offset", "0%")
            .attr("stop-color", startColor)
            .attr("stop-opacity", 1);

        gradient.append("stop")
            .attr("offset", "100%")
            .attr("stop-color", endColor)
            .attr("stop-opacity", 1);
    }

    function updatePlot() {
        var selectedClient = $('#client').val();
        var selectedLounge = $('#lounge_name').val();
        var selectedAirport = $('#airport_name').val();
        var selectedCity = $('#city_name').val();
        var selectedCountry = $('#country_name').val();
        var timeAlert = $('#time_alert').val();
        var plotInterval = $('#plt_interval').val();
        var clientOrder = $('#client_order').val();
    
        var currentDate = new Date();
        var lastUpdate = currentDate.toLocaleString();
        $('#last-update').text('Last Update: seconds ago at ' + lastUpdate);
        
        var startDate = $('#startDate').val();
        var endDate = $('#endDate').val();

        $.ajax({
            url: '/update_plot',
            type: 'POST',
            data: {
                client: selectedClient,
                lounge_name: selectedLounge,
                airport_name: selectedAirport,
                city_name: selectedCity,
                country_name: selectedCountry,
                time_alert: timeAlert,
                plt_interval: plotInterval,
                start_date: startDate, // Send the selected start date to the server
                end_date: endDate, // Send the selected end date to the server
                client_order: clientOrder,
            },

            success: function(response) {
                var traces = response.traces;
                var layouts = response.layouts;
                var errors = response.errors;

                var lounge_act_num = response.lounge_act_num;
                var lounge_inact_num = response.lounge_inact_num
                $('#act-lounge').text(lounge_act_num);
                $('#lounge-total').text(lounge_act_num + lounge_inact_num);
                $('#progress_bar_lounge').css('width', (lounge_act_num * 100 / (lounge_act_num + lounge_inact_num)) + '%');
                $('#progress_bar_lounge strong').text((lounge_act_num * 100 / (lounge_act_num + lounge_inact_num)).toFixed(2) + '%');

                var vol_curr = response.vol_curr;
                var vol_prev = response.vol_prev
                $('#vol_curr').text(formatNumberWithCommas(vol_curr));
                $('#vol_prev').text(formatNumberWithCommas(vol_prev));
                
                function formatNumberWithCommas(number) {
                    return number.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
                }


                $('#progress_bar_vol').css('width', (vol_curr * 100 / (vol_prev)) + '%');
                $('#progress_bar_vol strong').text((vol_curr * 100 / (vol_prev)).toFixed(2) + '%');

                var active_clients_num = response.active_clients_num;
                var inactive_clients_num = response.inactive_clients_num
                $('#act-client').text(active_clients_num);
                $('#total-client').text(active_clients_num + inactive_clients_num);
                $('#progress_bar_client').css('width', (active_clients_num * 100 / (active_clients_num + inactive_clients_num)) + '%');
                $('#progress_bar_client strong').text((active_clients_num * 100 / (active_clients_num + inactive_clients_num)).toFixed(2) + '%');

                var chartsContainer = $('#charts-container');
                chartsContainer.empty();
                var plotsPerRow = calculatePlotsPerRow();

                for (var j = 0; j < Math.ceil(traces.length / plotsPerRow); j++) {
                    // Create a new row for each set of plots
                    var rowDiv = $('<div>').addClass('row');
                    chartsContainer.append(rowDiv);
                    
                    // var paragraph = $('<p>').text("hey you!");
                    // chartsContainer.append(paragraph);

                    //each slide of carousel for 


                
                    // Calculate the start and end index for the current row
                    var startIndex = j * plotsPerRow;
                    var endIndex = Math.min(startIndex + plotsPerRow, traces.length);

                    // Loop through the plots within the current row range
                    for (var i = startIndex; i < endIndex; i++) {

                        var chartId = 'chart-' + i;
                        var chartDiv = $('<div>').attr('id', chartId).addClass('plot');
                
                        if (selectedClient !== '' || selectedLounge !== '' || selectedAirport !== '' || selectedCity !== '' || selectedCountry !== '') {
                            chartDiv.addClass('single');
                        }
                
                        rowDiv.append(chartDiv);
                
                        var data = [traces[i]];
                        var layout = layouts[i];
                        Plotly.newPlot(chartId, data, layout);

                        var arrowDiv = $('<div>').addClass('arrow');
                        var arrowIcon = '';

                        if (errors[i]) {
                            var errorMessageDiv = $('<div>').addClass('error-message').text(errors[i]);
                            chartDiv.append(errorMessageDiv);
                            chartDiv.css('position', 'relative');
                            chartDiv.css('background-color', 'white');
                        } else {
                            var lastRecord = data[0].y[data[0].y.length - 1];
                            var prevRecord = data[0].y[data[0].y.length - 2];
                            var growthPercentage = ((lastRecord - prevRecord) / prevRecord) * 100;

                            if (growthPercentage > 0) {
                                arrowIcon = $('<i>').addClass('up-arrow').text('▲');
                                chartDiv.css('background-color', 'white');
                            } else if (growthPercentage < 0) {
                                arrowIcon = $('<i>').addClass('down-arrow').text('▼');
                                chartDiv.css('background-color', 'white');
                            }

                            arrowDiv.append(arrowIcon);
                            arrowDiv.append('<br>');
                            arrowDiv.append(growthPercentage.toFixed(2) + '%');
                        }

                        chartDiv.append(arrowDiv);

                        var chartElement = document.getElementById(chartId);
                        var linePath = chartElement.getElementsByClassName('js-line');
                        if (linePath.length > 0) {
                            var svg = d3.select(linePath[0].parentNode);
                            var gradientId = "gradient-" + i;
                            createGradientDefs(svg, gradientId, "rgb(97, 255, 123)", "rgb(255, 0, 0)");
                            linePath[0].style.stroke = "url(#" + gradientId + ")";
                        }
                    }
                }
            }
        });
    }


    function updateResults() {
        updatePlot();
    }

    setInterval(updateResults, 60000);

    $('#update-btn').on('click', function() {
        updateResults();
    });

    updatePlot();
});
