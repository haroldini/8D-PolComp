

let vals = $('#compass-data').data("compass")
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

for(const quadrant in quadrants) {
    let data = {
        datasets: [{
            pointRadius: 4,
            pointBackgroundColor: "rgba(0,0,255,1)",
            data: [{x: vals[quadrants[quadrant]["x"]], y: vals[quadrants[quadrant]["y"]]}],
            borderWidth: 2,
            borderWidth: {
                bottom: 0,
                top: 1,
                left: 1,
                right: 1
            }
        }]
    }
    let options = {
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
              topLeft: quadrants[quadrant]["colors"][0],
              topRight: quadrants[quadrant]["colors"][1],
              bottomLeft: quadrants[quadrant]["colors"][2],
              bottomRight: quadrants[quadrant]["colors"][3],
            },
            legend: {
                display: false
            }
        }
    }

    quadrants[quadrant]["chart"] = new Chart(quadrant, {
        type: "scatter",
        data: data,
        options: options,
        plugins: [quadrants_plugin]
    });
    quadrants[quadrant]["data"] = data
    quadrants[quadrant]["options"] = options
}
console.log(quadrants)
function save_image(div_id) {
    let scale = 10;
    let domNode = document.getElementById(div_id)
    domtoimage.toBlob(domNode, {
        width: domNode.clientWidth * scale,
        height: domNode.clientHeight * scale,
        style: {
        transform: 'scale('+scale+')',
        transformOrigin: 'top left'
        }
    })
    .then(function (blob) {
        window.saveAs(blob, '8dpolcomp.png');
    });
}
