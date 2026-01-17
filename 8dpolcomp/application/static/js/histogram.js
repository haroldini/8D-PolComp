
// Get list of result values for target axis
function get_axis_datavalues(axis_name) {
    let invert_axes = ["diplomacy", "government", "religion", "society"];

    let axis_data = {};

    for (dataset of datasets) {
        let dataset_axis_data = [];
        for (data of dataset.all_scores) {
            if (invert_axes.includes(axis_name)) {
                dataset_axis_data.push(-data[axis_name]);
            } else {
                dataset_axis_data.push(data[axis_name]);
            }
        }
        axis_data[dataset.label] = dataset_axis_data;
    }
    return axis_data;
}

// Bin the above values
function get_binned_datasets(values) {
    let hist_datasets = [];
    let hist_labels = [-1];
    let labels_generated = false;

    let propsByFilterset = {};
    let globalMaxProp = 0;

    for (const filterset in values) {
        const hist_generator = d3.bin().domain([-1, 1]).thresholds(20);
        const bins = hist_generator(values[filterset] || []);

        let counts = [];
        for (const bin of bins) {
            if (!labels_generated) {
                hist_labels.push(bin.x1);
            }
            counts.push(bin.length);
        }
        labels_generated = true;

        const total = counts.reduce((a, b) => a + b, 0);
        const props = total > 0 ? counts.map(c => c / total) : counts.map(() => 0);

        propsByFilterset[filterset] = props;

        const meta = datasets.find(x => x.label === filterset);
        const isYourResults = meta && meta.name === "your_results";

        if (!isYourResults) {
            const localMax = Math.max(...props, 0);
            if (localMax > globalMaxProp) globalMaxProp = localMax;
        }
    }

    const denom = globalMaxProp || 1;

    for (const filterset in propsByFilterset) {
        const meta = datasets.find(x => x.label === filterset);
        const isYourResults = meta && meta.name === "your_results";
        const color = meta ? meta.color : "#afafaf";

        const scaled = isYourResults
            ? propsByFilterset[filterset]                // keep raw proportions for your_results
            : propsByFilterset[filterset].map(v => v / denom);

        hist_datasets.push({
            label: filterset.replace("_", " "),
            borderWidth: 1,
            data: scaled,
            backgroundColor: color
        });
    }

    return [hist_labels, hist_datasets];
}



const axis_labels = {
    society: ["Progressivism", "Conservatism"],
    politics: ["Radicalism", "Moderatism"],
    economics: ["Socialism", "Capitalism"],
    state: ["Liberty", "Authority"],
    diplomacy: ["Cosmopolitanism", "Nationalism"],
    government: ["Democracy", "Autocracy"],
    technology: ["Transhumanism", "Primitivism"],
    religion: ["Secularism", "Theocracy"]
};

// Create results histogram chart from binned counts for each axis.
function create_histogram(axis_name) {

    document.getElementById("hist-label-l").textContent = axis_labels[axis_name][0];
    document.getElementById("hist-label-r").textContent = axis_labels[axis_name][1];

    const ctx = document.getElementById('histogram-canvas').getContext("2d");
    let axis_values = get_axis_datavalues(axis_name);
    let [hist_labels, hist_datasets] = get_binned_datasets(axis_values);

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
            scales: {
                x: {
                    display: true,
                    border: { display: false },
                    grid: { drawTicks: false, display: false },
                    ticks: { display: false },
                    min: -1,
                    max: 1,
                },
                y: {
                    display: true,
                    border: { display: false },
                    grid: {
                        color: "#9e9e9e",
                        drawTicks: false,
                        display: true
                    },
                    ticks: {
                        stepSize: 1,
                        autoSkip: true,
                        maxTicksLimit: 10,
                        font: { family: "Montserrat", weight: 600, size: 16 },
                        color: "#f3f3f3",
                        display: false,
                    },
                    min: 0,
                    max: 1
                }
            },
            plugins: {
                quadrants: {},
                legend: {
                    display: true,
                    labels: {
                        color: '#f3f3f3',
                        useBorderRadius: true,
                        boxWidth: 28,
                        borderRadius: 4,
                        padding: 20,
                        font: { family: "Montserrat", weight: 600, size: 14 },
                    }
                },
                tooltip: { enabled: false }
            }
        }
    });

    return histogram;
}

// Updates results histogram when an axis is selected
function update_histogram(axis_name) {
    let axis_values = get_axis_datavalues(axis_name);
    let [hist_labels, hist_datasets] = get_binned_datasets(axis_values);

    document.getElementById("hist-label-l").textContent = axis_labels[axis_name][0];
    document.getElementById("hist-label-r").textContent = axis_labels[axis_name][1];

    histogram.data = {
        labels: hist_labels,
        datasets: hist_datasets
    };
    histogram.update();
}
