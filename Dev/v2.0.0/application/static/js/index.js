let key_vals = {
    "chomsky": {
        "diplomacy": 0.5,
        "economics": 0.5,
        "government": -0.1578947368421,
        "politics": 0,
        "religion": -0.3333333333333,
        "society": 0.04278688524590164,
        "state": -0.691358024691357,
        "technology": 1
    },
    "gandhi": {
        "diplomacy": 0.2,
        "economics": -0.5,
        "government": -0.8421,
        "politics": 1,
        "religion": -0.3333333333333,
        "society": 0.04278688524590164,
        "state": -0.691358024691357,
        "technology": -1
    }
}
function update_chart_data(key) {
    for (quadrant in quadrants) {
        let chart = quadrants[quadrant]["chart"]
        chart.data.datasets[0].data[0] = {x: key_vals[key][quadrants[quadrant]["x"]], y: key_vals[key][quadrants[quadrant]["y"]]}
        chart.update()
    }
}

