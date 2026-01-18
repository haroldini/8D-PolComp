
// Defaults for selected axis and number of matches shown
let selected_axis = "overall";
let selected_num_matches_shown = 8;

// ensure global exists
let matches_chart = null;

function _isUUID(s) {
    const v = String(s || "").trim();
    return /^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-5][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$/.test(v);
}

function _getGroupIdFromMeta() {
    const meta = document.getElementById("group-data");
    if (!meta) return "";
    return String(meta.getAttribute("data-group") || "").trim();
}

async function copy_group_invite_link(tar, btn_text = "Copy Invite Link") {
    if (!tar) return;

    const gid = _getGroupIdFromMeta();
    if (!gid || !_isUUID(gid)) return;

    // uses ui.js helpers
    disable_button(tar, "Copied");

    const link = window.location.origin + "/instructions?g=" + encodeURIComponent(gid);

    try {
        await navigator.clipboard.writeText(link);
    } catch (e) {
        // fallback
        const tmp = document.createElement("textarea");
        tmp.value = link;
        document.body.appendChild(tmp);
        tmp.select();
        document.execCommand("copy");
        document.body.removeChild(tmp);
    }

    setTimeout(function () {
        enable_button(tar, btn_text);
    }, 2500);
}

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

function create_matches_chart(closest_matches, axis = "overall", num_matches_shown = 8) {
    let axis_data = closest_matches[axis] || [];
    let entries = axis_data.slice(0, num_matches_shown);
    let labels = entries.map(entry => entry[0]);
    let values = entries.map(entry => entry[1]);

    const ctx_matches = document.getElementById("matches-chart").getContext("2d");

    let chart = new Chart(ctx_matches, {
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

    return chart;
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

    if (!matches_chart) return;

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
