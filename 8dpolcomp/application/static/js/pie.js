let prev_question_id = 1

// Pie datasets contain counts for each answer for each question
function get_pie_datasets(question_id) {
    let pie_datasets = []
    for (dataset of datasets) {
        pie_datasets.push({
                label: dataset.label,
                backgroundColor: dataset.color,
                data: dataset.answer_counts[question_id],
                borderWidth: 1
            })
    }
    return pie_datasets
}

// Creates question explorer chart from pie_datasets
function create_pie(question_id) {
    const pie_ctx = document.getElementById('pie-canvas');
    pie_datasets = get_pie_datasets(question_id)

    let pie = new Chart(pie_ctx, {
        type: 'bar',
        data: {
            labels: ["Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree"],
            datasets: pie_datasets
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
                        font: {
                            family: "Montserrat",
                            weight: 600,
                            size: 12
                        },
                        maxRotation: 90,
                        minRotation: 90,
                        padding: 5,
                        color: "#f3f3f3",
                        display: true,
                    }
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
    return pie
}

// Triggered when new question selected from question table
function update_pie(question_id, prev_question_id) {
    document.getElementById("qid_"+prev_question_id).classList.remove("row-selected")
    document.getElementById("qid_"+question_id).classList.add("row-selected")
    document.getElementById("question_text").innerText = document.getElementById("qid_"+question_id).getElementsByTagName("td")[1].textContent

    let pie_datasets = get_pie_datasets(question_id)
    pie.data = {
        labels: ["Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree"],
        datasets: pie_datasets
    }
    pie.update()
}

// Triggered when arrow buttons pressed to cycle through questions
function change_selected_question(direction) {
    prev_question_id = question_id
    if (direction == "prev") {
        if (question_id == 1) {
            question_id = 100
        } else {
            question_id -= 1
        } 
    } else if (direction == "next") {
        if (question_id < 100) {
            question_id += 1
        } else {
            question_id = 1
        }
    }
    update_pie(question_id, prev_question_id)
}