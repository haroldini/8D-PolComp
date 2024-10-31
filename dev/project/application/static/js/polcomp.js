let datasets = $('#compass-data').data("compass")

// Props for each quadrant
const quadrants = {
    "upper_left": {
        "x": "society",
        "y": "politics",
        "colors": ["#93daf8", "#afafaf", "#afafaf", "#c9e5bd"],
        "chart": null,
        "data": null,
    }, 
    "upper_right": {
        "x": "economics",
        "y": "state",
        "colors": ["#afafaf", "#93daf8", "#c9e5bd", "#afafaf"],
        "chart": null,
        "data": null,
    }, 
    "lower_left": {
        "x": "diplomacy",
        "y": "government",
        "colors": ["#afafaf", "#c9e5bd", "#93daf8", "#afafaf"],
        "chart": null,
        "data": null,
    }, 
    "lower_right": {
        "x": "technology",
        "y": "religion",
        "colors": ["#c9e5bd", "#afafaf", "#afafaf", "#93daf8"],
        "chart": null,
        "data": null,
    }
}

// Colours four corners of each quadrant
const quadrants_plugin = {
    id: 'quadrants',
    beforeDraw(chart, args, options) {
      const {ctx, chartArea: {left, top, right, bottom}, scales: {x, y}} = chart;
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

function create_polcomp(quadrants) {
    for(const quadrant in quadrants) {
        create_quadrant(quadrant, quadrants)
    }
}

// Determines point radius and transparency based on number of points.
function calc_point_props(dataset, count) {
    if ("point_props" in dataset) {
        return dataset.point_props
    }
    if (count > 10000) {
        return [0.3, 2.5]
    } else if ( count > 3300 ) {
        return [0.325, 2.75]
    } else if ( count > 1000 ) {
        return [0.35, 3]
    } else if ( count > 500 ) {
        return [0.375, 3.25]
    } else if ( count > 250 ) {
        return [0.4, 3.5]
    } else if ( count > 100 ) {
        return [0.425, 3.75]
    } else if ( count > 5 ) {
        return [0.45, 4]
    } else {
        return [0.65, 5]
    }
}

// Create list of datasets to display on chart
// Separate datasets for averages created after
function get_pc_data(quadrant, quadrants) {
    let pc_data = {
        datasets: []
    }

    // Add user results on top
    for (dataset of datasets) {
        if (dataset.name == "your_results") {
            let data_values= []
            let [transparency, radius] = calc_point_props(dataset, dataset.count)
            for (score_set of dataset.all_scores) {
                data_values.push({
                    x: score_set[quadrants[quadrant].x],
                    y: score_set[quadrants[quadrant].y]
                })
            }
            pc_data.datasets.push({
                pointRadius: radius/2,
                pointBackgroundColor: add_transparency(dataset.color, transparency),
                pointStyle: 'circle',
                pointBorderWidth: radius/4,
                pointBorderColor: add_transparency("#262626", transparency),
                data: data_values,
                label: dataset.label,
                filterset_id: null,
                borderWidth: {
                    bottom: 0,
                    top: 1,
                    left: 1,
                    right: 1
                }
            })
        }
    }

    // Then add averages
    for (dataset of datasets) {
        let [transparency, radius] = calc_point_props(dataset, dataset.count)

        // Average scores displayed on top
        if (dataset["count"] > 1) {
            if ("mean_scores" in dataset) {
                mean_vals = [{
                    x: dataset.mean_scores[quadrants[quadrant].x],
                    y: dataset.mean_scores[quadrants[quadrant].y]
                }]
                pc_data.datasets.push({
                    pointRadius: radius,
                    pointBackgroundColor: add_transparency(dataset.color, transparency),
                    pointStyle: 'circle',
                    pointBorderWidth: radius/2,
                    pointBorderColor: add_transparency("#262626", transparency),
                    data: mean_vals,
                    label: dataset.label+" Average",
                    tooltipEnabled: false,
                    borderWidth: {
                        bottom: 0,
                        top: 1,
                        left: 1,
                        right: 1
                    }
                })
            }
        }
    }

    // All scores displayed under
    for (dataset of datasets) {
        let data_values = []
        let [transparency, radius] = calc_point_props(dataset, dataset.count)
        for (score_set of dataset.all_scores) {
            data_values.push({
                x: score_set[quadrants[quadrant].x],
                y: score_set[quadrants[quadrant].y]
            })
        }
        pc_data.datasets.push({
            pointRadius: radius/2,
            pointBackgroundColor: add_transparency(dataset.color, transparency),
            pointStyle: 'circle',
            pointBorderWidth: radius/4,
            pointBorderColor: add_transparency("#262626", transparency),
            data: data_values,
            label: dataset.label,
            filterset_id: null,
            borderWidth: {
                bottom: 0,
                top: 1,
                left: 1,
                right: 1
            }
        })
    }
    return pc_data
}

// Each quadrant an individual chartjs object
function create_quadrant(quadrant, quadrants) {

    let pc_data = get_pc_data(quadrant, quadrants)
    let pc_options = {
        aspectRatio: 1, 
        responsive: true,
        maintainAspectRatio: true,
        layout: {
            padding: 0,
            autoPadding: false,
        },
        scales:{
            x: {
                display: false,
                grid: {
                    drawTicks: false,
                    display: false,
                },
                ticks: {
                    display: false
                },
                min: -1,
                max: 1,
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
                max: 1,
            }
        },
        plugins: {
            quadrants: {
            },
            legend: {
                display: false
            },
            tooltip: {
                enabled: false
            }
        }
    }

    pc_options.plugins.quadrants = {
        topLeft: quadrants[quadrant].colors[0],
        topRight: quadrants[quadrant].colors[1],
        bottomLeft: quadrants[quadrant].colors[2],
        bottomRight: quadrants[quadrant].colors[3],
    }
    
    quadrants[quadrant].chart = new Chart(quadrant, {
        type: "scatter",
        data: pc_data,
        options: pc_options,
        plugins: [quadrants_plugin]
    });
    quadrants[quadrant].data = pc_data
    quadrants[quadrant].options = pc_options
}

// Updates each quadrant when filtersets applied
function update_chart_data() {

    for (quadrant in quadrants) {
        pc_data = get_pc_data(quadrant, quadrants)
        let chart = quadrants[quadrant].chart
        chart.data = pc_data
        chart.update()
    }
}

// Converts datasets to csv string
function get_csv(datasets) {
    lst = []
    i = 0
    for (dataset in datasets) {
        for (row in datasets[dataset]["all_scores"]) {
            lst.push(datasets[dataset]["all_scores"][row])
            lst[i].dataset = Number(dataset)+Number(1)
            i++
        }
    }
    let topLine = Object.keys(lst[0]).join(",");
    lines = lst.reduce( (acc, val) => 
    acc.concat( Object.values(val).join(`,`) ), [] );
    csv = topLine.concat(`\n${lines.join(`\n`)}`);
    return csv
}

// Saves data from chart to device
async function export_csv(tar) {

    csv = get_csv(datasets)
    disable_button(tar)
    await sleep(Math.random()*1500+500)

    let link = document.getElementById('download-csv')
    link.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(csv));
    link.setAttribute('download', '8DPolComp-Data.csv');
    document.body.appendChild(link)
    document.querySelector('#download-csv').click()
    enable_button(tar, "Export CSV")

}

function show_spinner() {
    let polcomp = document.getElementById("polcomp")
    let savebtns = document.getElementById("savebtns")
    let spinner = document.getElementById("spinner")
    let statusmsg = document.getElementById("statusmsg")
    let applyfilters = document.getElementById("applyfilters")

    polcomp.style.display = "none"
    savebtns.style.display = "none"
    spinner.style.display = "flex"
    spinner.style.visibility = "visible"
    statusmsg.style.display = "flex"
    statusmsg.innerText = "Loading..."
    statusmsg.style.webkitTextFillColor = "transparent"

    if (applyfilters) {
        applyfilters.classList.add("disabled")
        applyfilters.disabled = true
    }
}
function hide_spinner() {
    let polcomp = document.getElementById("polcomp")
    let savebtns = document.getElementById("savebtns")
    let spinner = document.getElementById("spinner")
    let statusmsg = document.getElementById("statusmsg")
    let applyfilters = document.getElementById("applyfilters")

    polcomp.style.display = "flex"
    savebtns.style.display = "flex"
    spinner.style.display = "none"
    statusmsg.style.display = "none"
    
    if (applyfilters) {
        applyfilters.classList.remove("disabled")
        applyfilters.disabled = false
    }
}

function show_polcomp_error(e_msg="Error loading data, try again.") {
    let spinner = document.getElementById("spinner")
    let statusmsg = document.getElementById("statusmsg")
    let applyfilters = document.getElementById("applyfilters")

    spinner.style.visibility = "hidden"
    statusmsg.innerText = e_msg
    statusmsg.style.webkitTextFillColor = "salmon"

    if (applyfilters) {
        applyfilters.classList.remove("disabled")
        applyfilters.disabled = false
    }
}

create_polcomp(quadrants)