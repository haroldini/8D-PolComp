
// Defaults for selected axis and number of matches shown
let selected_axis = "overall";
let selected_num_matches_shown = 8;

function _getClosestMatches() {
    try {
        let raw = $("#matches-data").data("matches");
        if (typeof raw === "string") {
            return JSON.parse(raw);
        }
        if (raw && typeof raw === "object") {
            return raw;
        }
    } catch (e) {
        // ignore
    }

    try {
        const attr = $("#matches-data").attr("data-matches");
        if (attr) return JSON.parse(attr);
    } catch (e) {
        // ignore
    }

    return { overall: [] };
}

// Takes user to /instructions
function restart_test() {
    $(function () {
        $.ajax({
            type: "POST",
            url: "/api/to_instructions",
            contentType: "application/json",
            data: JSON.stringify({
                "action": "to_instructions"
            }),
            success: function () {
                window.location = "/instructions";
            },
            error: function (xhr) {
                const msg =
                    (xhr.responseJSON && xhr.responseJSON.status) ||
                    ("Request failed (" + xhr.status + "). Please refresh and try again.");
                alert(msg);
            }
        });
    });
}

function create_matches_chart(closest_matches, axis = "overall", num_matches_shown = 8) {
    let axis_data = closest_matches[axis] || [];
    let entries = axis_data.slice(0, num_matches_shown);
    let labels = entries.map(entry => entry[0]);
    let values = entries.map(entry => entry[1]);

    const ctx_matches = document.getElementById("matches-chart").getContext("2d");

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
                    formatter: function (value) {
                        return Math.round(value * 100) + "%";
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
                    max: 1.2,
                },
                y: {
                    display: true,
                    border: { display: false },
                    grid: { drawTicks: false, display: false },
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
                legend: { display: false },
                tooltip: { enabled: false },
            },
        }
    });

    return matches_chart;
}

// Updates results when an axis is selected
function update_matches(axis = "overall", num_matches_shown = 8) {
    let closest_matches = _getClosestMatches();

    if (axis != null) {
        selected_axis = axis;
    }
    if (num_matches_shown != null) {
        selected_num_matches_shown = num_matches_shown;
    }

    let axis_data = closest_matches[selected_axis] || [];
    let entries = axis_data.slice(0, selected_num_matches_shown);
    let labels = entries.map(entry => entry[0]);
    let values = entries.map(entry => entry[1]);

    if (!matches_chart) {
        return;
    }

    matches_chart.data.labels = labels;
    matches_chart.data.datasets[0].data = values;
    matches_chart.update();
}

// Updates results when number of matches shown is changed
function swap_num_matches(btn) {
    let state = btn.innerHTML;
    if (state === "-" && selected_num_matches_shown > 1) {
        selected_num_matches_shown = 8;
        btn.innerHTML = "+";
    } else if (state === "+") {
        selected_num_matches_shown = 15;
        btn.innerHTML = "-";
    }
    update_matches(null, selected_num_matches_shown);
}

window.onload = function () {
    let closest_matches = _getClosestMatches();
    matches_chart = create_matches_chart(closest_matches);
};
