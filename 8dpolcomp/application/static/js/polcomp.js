
let datasets = $("#compass-data").data("compass");

if (typeof datasets === "string") {
    try {
        datasets = JSON.parse(datasets);
    } catch (e) {
        datasets = [];
    }
}
if (!Array.isArray(datasets)) {
    datasets = [];
}

// Props for each quadrant
const quadrants = {
    "upper_left": {
        "x": "society",
        "y": "politics",
        "colors": ["#93daf8", "#afafaf", "#afafaf", "#c9e5bd"],
        "chart": null,
        "data": null
    },
    "upper_right": {
        "x": "economics",
        "y": "state",
        "colors": ["#afafaf", "#93daf8", "#c9e5bd", "#afafaf"],
        "chart": null,
        "data": null
    },
    "lower_left": {
        "x": "diplomacy",
        "y": "government",
        "colors": ["#afafaf", "#c9e5bd", "#93daf8", "#afafaf"],
        "chart": null,
        "data": null
    },
    "lower_right": {
        "x": "technology",
        "y": "religion",
        "colors": ["#c9e5bd", "#afafaf", "#afafaf", "#93daf8"],
        "chart": null,
        "data": null
    }
};

// Colours four corners of each quadrant
const quadrants_plugin = {
    id: "quadrants",
    beforeDraw(chart, args, options) {
        const { ctx, chartArea: { left, top, right, bottom }, scales: { x, y } } = chart;
        const midX = x.getPixelForValue(0);
        const midY = y.getPixelForValue(0);
        ctx.save();
        ctx.fillStyle = options.topLeft;
        ctx.fillRect(left, top, midX - left, midY - top);
        ctx.fillStyle = options.topRight;
        ctx.fillRect(midX, top, right - midX, midY - top);
        ctx.fillStyle = options.bottomRight;
        ctx.fillRect(midX, midY, right - midX, bottom - midY);
        ctx.fillStyle = options.bottomLeft;
        ctx.fillRect(left, midY, midX - left, bottom - midY);
        ctx.restore();
    }
};

function create_polcomp(quadrants_obj) {
    for (const quadrant in quadrants_obj) {
        create_quadrant(quadrant, quadrants_obj);
    }
}

// Determines point radius and transparency based on number of points.
function calc_point_props(dataset, count) {
    if ("point_props" in dataset) {
        return dataset.point_props;
    }
    if (count > 10000) {
        return [0.3, 2.5];
    } else if (count > 3300) {
        return [0.325, 2.75];
    } else if (count > 1000) {
        return [0.35, 3];
    } else if (count > 500) {
        return [0.375, 3.25];
    } else if (count > 250) {
        return [0.4, 3.5];
    } else if (count > 100) {
        return [0.425, 3.75];
    } else if (count > 5) {
        return [0.45, 4];
    } else {
        return [0.65, 5];
    }
}

function _dataset_count(ds) {
    if (!ds) {
        return 0;
    }
    if (typeof ds.count === "number") {
        return ds.count;
    }
    if (Array.isArray(ds.all_scores)) {
        return ds.all_scores.length;
    }
    return 0;
}

// Create list of datasets to display on chart
function get_pc_data(quadrant, quadrants_obj) {
    let pc_data = {
        datasets: []
    };

    const user_datasets = datasets.filter(d => d && d.name === "your_results");
    const other_datasets = datasets.filter(d => d && d.name !== "your_results");

    const sorted_other = [...other_datasets].sort((a, b) => _dataset_count(a) - _dataset_count(b));
    const sorted_all = [...datasets].sort((a, b) => _dataset_count(a) - _dataset_count(b));

    for (const dataset of user_datasets) {
        let data_values = [];
        const count = _dataset_count(dataset);
        let [transparency, radius] = calc_point_props(dataset, count);

        for (const score_set of dataset.all_scores) {
            data_values.push({
                x: score_set[quadrants_obj[quadrant].x],
                y: score_set[quadrants_obj[quadrant].y]
            });
        }

        pc_data.datasets.push({
            pointRadius: radius / 2,
            pointBackgroundColor: add_transparency(dataset.color, transparency),
            pointStyle: "circle",
            pointBorderWidth: radius / 4,
            pointBorderColor: add_transparency("#262626", transparency),
            data: data_values,
            label: dataset.label,
            dataset_id: null,
            borderWidth: { bottom: 0, top: 1, left: 1, right: 1 }
        });
    }

    for (const dataset of sorted_other) {
        const count = _dataset_count(dataset);
        let [transparency, radius] = calc_point_props(dataset, count);

        if (count > 1 && "mean_scores" in dataset && dataset.mean_scores) {
            const mean_vals = [{
                x: dataset.mean_scores[quadrants_obj[quadrant].x],
                y: dataset.mean_scores[quadrants_obj[quadrant].y]
            }];

            pc_data.datasets.push({
                pointRadius: radius,
                pointBackgroundColor: add_transparency(dataset.color, 1),
                pointStyle: "circle",
                pointBorderWidth: radius / 2,
                pointBorderColor: add_transparency("#262626", 1),
                data: mean_vals,
                label: dataset.label + " Average",
                tooltipEnabled: false,
                dataset_id: (dataset.custom_dataset === true) ? dataset.custom_id : null,
                borderWidth: { bottom: 0, top: 1, left: 1, right: 1 }
            });
        }
    }

    // All scores displayed under
    for (const dataset of sorted_all) {
        let data_values = [];
        const count = _dataset_count(dataset);
        let [transparency, radius] = calc_point_props(dataset, count);

        for (const score_set of dataset.all_scores) {
            data_values.push({
                x: score_set[quadrants_obj[quadrant].x],
                y: score_set[quadrants_obj[quadrant].y]
            });
        }

        pc_data.datasets.push({
            pointRadius: radius / 2,
            pointBackgroundColor: add_transparency(dataset.color, transparency),
            pointStyle: "circle",
            pointBorderWidth: radius / 4,
            pointBorderColor: add_transparency("#262626", transparency),
            data: data_values,
            label: dataset.label,
            dataset_id: (dataset.custom_dataset === true) ? dataset.custom_id : null,
            borderWidth: { bottom: 0, top: 1, left: 1, right: 1 }
        });
    }

    return pc_data;
}

// Each quadrant an individual chartjs object
function create_quadrant(quadrant, quadrants_obj) {
    let pc_data = get_pc_data(quadrant, quadrants_obj);
    let pc_options = {
        aspectRatio: 1,
        responsive: true,
        maintainAspectRatio: true,
        layout: {
            padding: 0,
            autoPadding: false
        },
        scales: {
            x: {
                display: false,
                grid: {
                    drawTicks: false,
                    display: false
                },
                ticks: {
                    display: false
                },
                min: -1,
                max: 1
            },
            y: {
                display: true,
                grid: {
                    drawTicks: false,
                    display: false
                },
                ticks: {
                    display: false
                },
                min: -1,
                max: 1
            }
        },
        plugins: {
            quadrants: {},
            legend: {
                display: false
            },
            tooltip: {
                enabled: false
            }
        }
    };

    pc_options.plugins.quadrants = {
        topLeft: quadrants_obj[quadrant].colors[0],
        topRight: quadrants_obj[quadrant].colors[1],
        bottomLeft: quadrants_obj[quadrant].colors[2],
        bottomRight: quadrants_obj[quadrant].colors[3]
    };

    quadrants_obj[quadrant].chart = new Chart(quadrant, {
        type: "scatter",
        data: pc_data,
        options: pc_options,
        plugins: [quadrants_plugin]
    });

    quadrants_obj[quadrant].data = pc_data;
    quadrants_obj[quadrant].options = pc_options;
}

// Updates each quadrant when filtersets applied
function update_chart_data() {
    for (const quadrant in quadrants) {
        const pc_data = get_pc_data(quadrant, quadrants);
        let chart = quadrants[quadrant].chart;
        chart.data = pc_data;
        chart.update();
    }
}

// Converts datasets to csv string
function get_csv(datasets_obj) {
    let lst = [];
    let i = 0;
    for (const dataset in datasets_obj) {
        for (const row in datasets_obj[dataset]["all_scores"]) {
            lst.push(datasets_obj[dataset]["all_scores"][row]);
            lst[i].dataset = Number(dataset) + Number(1);
            i++;
        }
    }
    let topLine = Object.keys(lst[0]).join(",");
    let lines = lst.reduce((acc, val) => acc.concat(Object.values(val).join(",")), []);
    let csv = topLine.concat("\n" + lines.join("\n"));
    return csv;
}

// Saves data from chart to device
async function export_csv(tar) {
    let csv = get_csv(datasets);
    disable_button(tar);
    await sleep(Math.random() * 1500 + 500);

    let link = document.getElementById("download-csv");
    link.setAttribute("href", "data:text/plain;charset=utf-8," + encodeURIComponent(csv));
    link.setAttribute("download", "8DPolComp-Data.csv");
    document.body.appendChild(link);
    document.querySelector("#download-csv").click();
    enable_button(tar, "Export CSV");
}

function show_spinner() {
    let polcomp = document.getElementById("polcomp");
    let savebtns = document.getElementById("savebtns");
    let spinner = document.getElementById("spinner");
    let statusmsg = document.getElementById("statusmsg");
    let applyfilters = document.getElementById("applyfilters");

    if (polcomp) polcomp.style.display = "none";
    if (savebtns) savebtns.style.display = "none";
    if (spinner) {
        spinner.style.display = "flex";
        spinner.style.visibility = "visible";
    }
    if (statusmsg) {
        statusmsg.style.display = "flex";
        statusmsg.innerText = "Loading...";
        statusmsg.style.webkitTextFillColor = "transparent";
    }

    if (applyfilters) {
        applyfilters.classList.add("disabled");
        applyfilters.disabled = true;
    }
}

function hide_spinner() {
    let polcomp = document.getElementById("polcomp");
    let savebtns = document.getElementById("savebtns");
    let spinner = document.getElementById("spinner");
    let statusmsg = document.getElementById("statusmsg");
    let applyfilters = document.getElementById("applyfilters");

    if (polcomp) polcomp.style.display = "flex";
    if (savebtns) savebtns.style.display = "flex";
    if (spinner) spinner.style.display = "none";
    if (statusmsg) statusmsg.style.display = "none";

    // IMPORTANT: force Chart.js to recompute size after being hidden
    for (const quadrant in quadrants) {
        const chart = quadrants[quadrant].chart;
        if (chart && typeof chart.resize === "function") {
            chart.resize();
        }
    }

    if (applyfilters) {
        applyfilters.classList.remove("disabled");
        applyfilters.disabled = false;
    }
}

function show_polcomp_error(e_msg = "Error loading data, try again.") {
    let spinner = document.getElementById("spinner");
    let statusmsg = document.getElementById("statusmsg");
    let applyfilters = document.getElementById("applyfilters");

    if (spinner) spinner.style.visibility = "hidden";
    if (statusmsg) {
        statusmsg.innerText = e_msg;
        statusmsg.style.webkitTextFillColor = "salmon";
    }

    if (applyfilters) {
        applyfilters.classList.remove("disabled");
        applyfilters.disabled = false;
    }
}

create_polcomp(quadrants);
