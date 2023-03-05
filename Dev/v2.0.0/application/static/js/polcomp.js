let vals = $('#results').data("results")

const quadrants = {
    "upper_left": {
        "x": vals["society"],
        "y": vals["politics"],
        "colors": ["#93daf8", "#afafaf", "#afafaf", "#c9e5bd"]
    }, 
    "upper_right": {
        "x": vals["economics"],
        "y": vals["state"],
        "colors": ["#afafaf", "#93daf8", "#c9e5bd", "#afafaf"]
    }, 
    "lower_left": {
        "x": vals["diplomacy"],
        "y": vals["government"],
        "colors": ["#afafaf", "#c9e5bd", "#93daf8", "#afafaf"]
    }, 
    "lower_right": {
        "x": vals["technology"],
        "y": vals["religion"],
        "colors": ["#c9e5bd", "#afafaf", "#afafaf", "#93daf8"]
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
    new Chart(quadrant, {
        type: "scatter",
        data: {
            datasets: [{
                pointRadius: 4,
                pointBackgroundColor: "rgba(0,0,255,1)",
                data: [{x: quadrants[quadrant]["x"], y: quadrants[quadrant]["y"]}],
                borderWidth: 2,
                borderWidth: {
                    bottom: 0,
                    top: 1,
                    left: 1,
                    right: 1
                }
          }]
        },
        options:{
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
        },
        plugins: [quadrants_plugin]
    });
}

function save_image(div_id) {
    var element = document.getElementById(div_id);
    html2canvas(element).then(function(canvas) {
        canvas.toBlob(function(blob) {
            window.saveAs(blob, "8dpolcomp.png");
        });
    });
}