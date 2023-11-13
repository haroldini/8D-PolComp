// Takes user to /instructions
function restart_test() {
    $(function () {
        $.ajax({
            type: "POST",
            url: "/api/to_instructions",
            contentType:"application/json",
            data : JSON.stringify({
                "action": "to_instructions"
            }),
            success: function () {
                window.location = "/instructions";
            },
            error: function(req, err) {
                console.log("error: ", err)
            }
        })
    });
}


function create_matches_chart(closest_matches, axis="overall") {
    // Extract labels and data values
    let num_matches_shown = 8
    let entries = closest_matches[axis].slice(0, num_matches_shown);
    let labels = entries.map(entry => entry[0]);
    let values = entries.map(entry => entry[1]);

    // Get the canvas element
    const ctx_matches = document.getElementById("matches-chart").getContext("2d");

    // Create the bar chart
    let matches_chart = new Chart(ctx_matches, {
        type: "bar",
        plugins: [ChartDataLabels],
        data: {
            labels: labels,
            datasets: [{
                label: "Overall Scores",
                data: values,
                backgroundColor: "#93daf8", 
                borderWidth: 0,
                datalabels: {
                    color: "#f3f3f3",
                    z: 1,
                    anchor: "end",
                    align: "right",
                    font: {
                        family: "Montserrat",
                        weight: 600,
                        size: 12
                    },
                    formatter: function(value, context) {
                        // Multiply the value by 100 and round to an integer
                        return Math.round(value * 100)+"%";
                    }
                }
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            indexAxis: "y",
            scales: {
                x: {
                    display: false,
                    min: 0,
                    max: 1,
                },
                y: {
                    display: true,
                    border: {
                        display: false,
                    },
                    grid: {
                        drawTicks: false,
                        display: false,
                    },
                    ticks: {
                        display: true,
                        autoSkip: false,
                        font: {
                            family: "Montserrat",
                            weight: 600,
                            size: 12
                        },
                        color: "#1d1d1d",
                        mirror: true,
                        showLabelBackdrop: false,
                        z: 1,
                        align: "center",
                        clamp: true,
                    }
                },
            },
            plugins: {
                quadrants: {
                },
                legend: {
                    display: false,
                },
                tooltip: {
                    enabled: false
                },
            },
        }
    });
    return matches_chart
}


// Updates results histogram when an axis is selected
function update_matches(axis, num_matches_shown=8) {
    let closest_matches = $("#matches-data").data("matches")
    let entries = closest_matches[axis].slice(0, num_matches_shown);
    let labels = entries.map(entry => entry[0]);
    let values = entries.map(entry => entry[1]);

    matches_chart.data.labels = labels
    matches_chart.data.datasets[0].data = values
    matches_chart.update()
}

window.onload = function() {
    
    // Creates default histogram & pie chart
    let closest_matches = $("#matches-data").data("matches")
    matches_chart = create_matches_chart(closest_matches)
    
};