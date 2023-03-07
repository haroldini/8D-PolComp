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
    "recent": $('#compass-data').data("compass")
}
function update_chart_data(event, key) {
    const icons = document.getElementsByClassName("icon-button")
    for (icon of icons) {
        icon.classList.remove("icon-selected")
    }
    event.target.classList.add("icon-selected")

    for (quadrant in quadrants) {
        let chart = quadrants[quadrant]["chart"]
        chart.data.datasets[0].data[0] = {x: key_vals[key][quadrants[quadrant]["x"]], y: key_vals[key][quadrants[quadrant]["y"]]}
        chart.update()
    }
}

