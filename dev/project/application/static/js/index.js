// Axis values for each sample compass
let key_vals = {
    "chomsky": {
        "diplomacy": 0.75,
        "economics": -0.6,
        "government": 0.7,
        "politics": -0.5,
        "religion": 0.4,
        "society": 0.6,
        "state": -0.7,
        "technology": -0.5
    },
    "gandhi": {
        "diplomacy": -0.5,
        "economics": -0.4,
        "government": 0.7,
        "politics": -0.5,
        "religion": 0.5,
        "society": -0.3,
        "state": -0.7,
        "technology": 0.1
    },
    "hitler": {
        "diplomacy": -0.7,
        "economics": 0.3,
        "government": -0.9,
        "politics": -0.8,
        "religion": -0.7,
        "society": -0.6,
        "state": 0.9,
        "technology": -0.7
    },
    "rand": {
        "diplomacy": 0.2,
        "economics": 0.7,
        "government": -0.3,
        "politics": 0.4,
        "religion": 0.7,
        "society": 0.3,
        "state": -0.5,
        "technology": -0.65
    },
    "reagan": {
        "diplomacy": -0.55,
        "economics": 0.75,
        "government": 0.2,
        "politics": 0.6,
        "religion": -0.2,
        "society": -0.5,
        "state": 0.6,
        "technology": -0.3
    },
    "stalin": {
        "diplomacy": 0.3,
        "economics": -0.8,
        "government": -0.85,
        "politics": -0.8,
        "religion": 0.8,
        "society": -0.4,
        "state": 0.65,
        "technology": -0.6
    },
    "recent": $('#compass-data').data("compass")[0].all_scores[0]
}

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
}

// Updates 'The Axes' quadrants when new sample compass enabled
function update_index_chart(event, key) {
    const icons = document.getElementsByClassName("icon-button")
    for (icon of icons) {
        icon.classList.remove("icon-selected")
    }
    event.target.classList.add("icon-selected")

    for (quadrant in quadrants) {
        let chart = quadrants[quadrant].chart
        chart.data.datasets[0].data[0] = {x: key_vals[key][quadrants[quadrant].x], y: key_vals[key][quadrants[quadrant].y]}
        chart.update()
    }

    for (quadrant in quadrants_sample) {
        let chart = quadrants_sample[quadrant].chart
        chart.data.datasets[0].data[0] = {x: key_vals[key][quadrants_sample[quadrant].x], y: key_vals[key][quadrants_sample[quadrant].y]}
        chart.update()
    }
}

// Creates quadrants for 'The Axes' 
function create_axis_clones() {
    for (const quadrant_sample in quadrants_sample) {
        create_quadrant(quadrant_sample, quadrants_sample)
    }
}

create_axis_clones()