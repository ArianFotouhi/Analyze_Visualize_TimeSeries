$(document).ready(function() {
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


        var currentDate = new Date();
        var lastUpdate = currentDate.toLocaleString();
        $('#last-update').text('Last Update: a few seconds ago at ' + lastUpdate);

        $.ajax({
            url: '/update_plot',
            type: 'POST',
            data: { client: selectedClient, lounge_name: selectedLounge, airport_name: selectedAirport},

            success: function(response) {
                var traces = response.traces;
                var layouts = response.layouts;
                var errors = response.errors;

                var chartsContainer = $('#charts-container');
                chartsContainer.empty();

                for (var i = 0; i < traces.length; i++) {
                    var chartId = 'chart-' + i;
                    var chartDiv = $('<div>').attr('id', chartId).addClass('plot');
                    if (selectedClient !== '' || selectedLounge !=='' || selectedAirport!== '') {
                        chartDiv.addClass('single');
                    }
                    chartsContainer.append(chartDiv);
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
                        createGradientDefs(svg, gradientId, "rgb(0, 255, 0)", "rgb(255, 0, 0)");
                        linePath[0].style.stroke = "url(#" + gradientId + ")";
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
