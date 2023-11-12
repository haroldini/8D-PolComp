// Max scale a list of values to 1
function maxScale(array) {
    let max = Math.max(...array);
    let scaled_array = array.map(function (value) {
        return value / max;
    });

    return scaled_array;
}

// Get list of result values for target axis
function get_axis_datavalues(axis_name) {
    let invert_axes = ["economics", "state", "politics", "technology"]

    let axis_data = {}
    
    for (dataset of datasets) {
        let dataset_axis_data = []
        for (data of dataset.all_scores) {
            if (invert_axes.includes(axis_name)) {
                dataset_axis_data.push(-data[axis_name])
            } else {
                dataset_axis_data.push(data[axis_name])
            }
        }
        axis_data[dataset.name] = dataset_axis_data
    }    
    return axis_data
}

// Bin the above values 
function get_binned_datasets(values) {

    hist_datasets = []
    hist_labels = [-1]
    labels_generated = false
    for (filterset in values) {
        let color = datasets.filter(x => x.name === filterset)[0].color
        
        const hist_generator = d3.bin().domain([-1,1]).thresholds(20);
        let bins = hist_generator(values[filterset])
        
        hist_data = []
        for (bin of bins) {
            if (!labels_generated) {
                hist_labels.push(bin.x1)
            }
            hist_data.push(bin.length)
        }
        scaled_hist_data = maxScale(hist_data)
        labels_generated = true
        
        hist_datasets.push({
            label: filterset.replace("_", " "),
            borderWidth: 1,
            data: scaled_hist_data,
            backgroundColor: color
        })
    }
    return [hist_labels, hist_datasets]
}

const axis_labels = {
    society: ["Conservatism", "Progressivism"],
    politics: ["Moderatism", "Radicalism"],
    economics: ["Capitalism", "Socialism"],
    state: ["Authority", "Liberty"],
    diplomacy: ["Nationalism", "Cosmopolitanism"],
    government: ["Autocracy", "Democracy"],
    technology: ["Primitivism", "Transhumanism"],
    religion: ["Theocracy", "Secularism"]
}

// Create results histogram chart from binned counts for each axis.
function create_histogram(axis_name) {

    document.getElementById("hist-label-l").textContent = axis_labels[axis_name][0]
    document.getElementById("hist-label-r").textContent = axis_labels[axis_name][1]

    const ctx = document.getElementById('histogram-canvas').getContext("2d");
    let axis_values = get_axis_datavalues(axis_name)
    let [hist_labels, hist_datasets] = get_binned_datasets(axis_values)
    
    let histogram = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: hist_labels,
            datasets: hist_datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            layout: {
                padding: 0,
                autoPadding: false,
            },
            scales:{
                x: {
                    display: true,
                    border: {
                        display: false,
                    },
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
                    border: {
                        display: false,
                    },
                    grid: {
                        color: "#9e9e9e",
                        drawTicks: false,
                        display: true
                      },
                    ticks: {
                        stepSize: 1,
                        autoSkip: true,
                        maxTicksLimit: 10,
                        font: {
                            family: "Montserrat",
                            weight: 600,
                            size: 16
                        },
                        color: "#f3f3f3",
                        display: false,
                    },
                    min: 0,
                }
            },
            plugins: {
                quadrants: {
                },
                legend: {
                    display: true,
                    labels: {
                        color: '#f3f3f3',
                        useBorderRadius: true,
                        boxWidth: 28,
                        borderRadius: 4,
                        padding: 20,
                        font: {
                            family: "Montserrat",
                            weight: 600,
                            size: 14
                        },
                    }
                },
                tooltip: {
                    enabled: false
                }
            }
        }
    });
    return histogram
}

// Updates results histogram when an axis is selected
function update_histogram(axis_name) {
    let axis_values = get_axis_datavalues(axis_name)
    let [hist_labels, hist_datasets] = get_binned_datasets(axis_values)
    document.getElementById("hist-label-l").textContent = axis_labels[axis_name][0]
    document.getElementById("hist-label-r").textContent = axis_labels[axis_name][1]
    histogram.data = {
        labels: hist_labels,
        datasets: hist_datasets
    }
    histogram.update()
}

