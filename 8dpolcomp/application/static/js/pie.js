
let prev_question_id = 1;

const ANSWER_ORDER = [
    "Strongly Disagree",
    "Disagree",
    "Neutral",
    "Agree",
    "Strongly Agree"
];

function _getRawCounts(dataset, question_id) {
    const qKey = String(question_id);

    // Preferred: raw counts from backend datasets
    if (dataset.raw_answer_counts && dataset.raw_answer_counts[qKey]) {
        const src = dataset.raw_answer_counts[qKey];
        return ANSWER_ORDER.map(k => src[k] || 0);
    }

    // Fallback: your_results uses "answer_counts" as raw (0/1) counts
    if (dataset.answer_counts && dataset.answer_counts[qKey]) {
        const src = dataset.answer_counts[qKey];
        return ANSWER_ORDER.map(k => src[k] || 0);
    }

    return ANSWER_ORDER.map(() => 0);
}

// Pie datasets contain counts for each answer for each question
function get_pie_datasets(question_id) {
    const rows = datasets.map(ds => {
        const counts = _getRawCounts(ds, question_id);
        const total = counts.reduce((a, b) => a + b, 0);
        const props = total > 0 ? counts.map(c => c / total) : counts.map(() => 0);
        return { ds, props };
    });

    const nonUserMax = Math.max(
        0,
        ...rows
            .filter(r => r.ds.name !== "your_results")
            .flatMap(r => r.props)
    );

    const denom = nonUserMax || 1;

    return rows.map(({ ds, props }) => ({
        label: ds.label,
        backgroundColor: ds.color,
        data: ds.name === "your_results"
            ? props
            : props.map(v => v / denom),
        borderWidth: 1
    }));
}


// Creates question explorer chart from pie_datasets
function create_pie(question_id) {
    const pie_ctx = document.getElementById('pie-canvas');
    pie_datasets = get_pie_datasets(question_id);

    let pie = new Chart(pie_ctx, {
        type: 'bar',
        data: {
            labels: ANSWER_ORDER,
            datasets: pie_datasets
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
                    ticks: {
                        font: { family: "Montserrat", weight: 600, size: 12 },
                        maxRotation: 90,
                        minRotation: 90,
                        padding: 5,
                        color: "#f3f3f3",
                        display: true,
                    }
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

    return pie;
}

// Triggered when new question selected from question table
function update_pie(question_id, prev_question_id) {
    document.getElementById("qid_" + prev_question_id).classList.remove("row-selected");
    document.getElementById("qid_" + question_id).classList.add("row-selected");
    document.getElementById("question_text").innerText = document.getElementById("qid_" + question_id).getElementsByTagName("td")[1].textContent;

    let pie_datasets = get_pie_datasets(question_id);

    pie.data = {
        labels: ANSWER_ORDER,
        datasets: pie_datasets
    };
    pie.update();
}

// Triggered when arrow buttons pressed to cycle through questions
function change_selected_question(direction) {
    prev_question_id = question_id;

    if (direction === "prev") {
        question_id = (question_id === 1) ? 100 : (question_id - 1);
    } else if (direction === "next") {
        question_id = (question_id < 100) ? (question_id + 1) : 1;
    }

    update_pie(question_id, prev_question_id);
}
