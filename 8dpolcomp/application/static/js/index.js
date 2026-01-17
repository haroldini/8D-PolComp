
// Loaded from static/data/samples/scores.json
let key_vals = {};

// Axis values fallback
function _zeroAxes() {
    return {
        diplomacy: 0,
        economics: 0,
        government: 0,
        politics: 0,
        religion: 0,
        society: 0,
        state: 0,
        technology: 0
    };
}

function set_recent_vals() {
    try {
        let raw = $('#compass-data').data("compass");
        if (typeof raw === "string") {
            raw = JSON.parse(raw);
        }
        if (Array.isArray(raw) && raw.length > 0 && raw[0].all_scores && raw[0].all_scores.length > 0) {
            key_vals["recent"] = raw[0].all_scores[0];
            return;
        }
    } catch (e) {
        // ignore
    }
    key_vals["recent"] = _zeroAxes();
}

async function load_sample_scores() {
    // Always ensure recent exists
    key_vals["recent"] = _zeroAxes();

    try {
        const resp = await fetch("/static/data/samples/scores.json", { cache: "no-store" });
        if (!resp.ok) {
            set_recent_vals();
            return;
        }

        const data = await resp.json();
        if (data && typeof data === "object") {
            key_vals = data;
        }
    } catch (e) {
        // ignore
    }

    set_recent_vals();
}

load_sample_scores();


// Additional compass quadrants for 'The Axes' section.
const quadrants_sample = {
    "upper_left_sample": {
        "x": "society",
        "y": "politics",
        "colors": ["#93daf8", "#afafaf", "#afafaf", "#c9e5bd"],
        "chart": null,
        "data": null,
    },
    "upper_right_sample": {
        "x": "economics",
        "y": "state",
        "colors": ["#afafaf", "#93daf8", "#c9e5bd", "#afafaf"],
        "chart": null,
        "data": null,
    },
    "lower_left_sample": {
        "x": "diplomacy",
        "y": "government",
        "colors": ["#afafaf", "#c9e5bd", "#93daf8", "#afafaf"],
        "chart": null,
        "data": null,
    },
    "lower_right_sample": {
        "x": "technology",
        "y": "religion",
        "colors": ["#c9e5bd", "#afafaf", "#afafaf", "#93daf8"],
        "chart": null,
        "data": null,
    }
};


// Updates 'The Axes' quadrants when new sample compass enabled
function update_index_chart(event, key) {
    const icons = document.getElementsByClassName("icon-button");
    for (const icon of icons) {
        icon.classList.remove("icon-selected");
    }
    event.target.classList.add("icon-selected");

    if (!key_vals[key] || typeof key_vals[key] !== "object") {
        return;
    }

    for (const quadrant in quadrants) {
        let chart = quadrants[quadrant].chart;
        if (!chart || !chart.data || !chart.data.datasets || !chart.data.datasets[0]) {
            continue;
        }
        chart.data.datasets[0].data[0] = {
            x: key_vals[key][quadrants[quadrant].x],
            y: key_vals[key][quadrants[quadrant].y]
        };
        chart.update();
    }

    for (const quadrant in quadrants_sample) {
        let chart = quadrants_sample[quadrant].chart;
        if (!chart || !chart.data || !chart.data.datasets || !chart.data.datasets[0]) {
            continue;
        }
        chart.data.datasets[0].data[0] = {
            x: key_vals[key][quadrants_sample[quadrant].x],
            y: key_vals[key][quadrants_sample[quadrant].y]
        };
        chart.update();
    }
}


// Creates quadrants for 'The Axes'
function create_axis_clones() {
    if (typeof create_quadrant !== "function") {
        return;
    }
    for (const quadrant_sample in quadrants_sample) {
        create_quadrant(quadrant_sample, quadrants_sample);
    }
}

create_axis_clones();
