
let num_filtersets = 1;
let current_legacy_card = 0;

// Self explanatory
function add_filterset(event) {
    let new_filterset = document.getElementById("filterset" + (num_filtersets + 1));
    new_filterset.classList.remove("hidden");

    if (num_filtersets === 3) {
        event.target.classList.add("disabled");
        event.target.disabled = true;
    }
    if (num_filtersets === 1) {
        let rm_btn = document.getElementById("rmfiltersetbtn");
        rm_btn.classList.remove("disabled");
        rm_btn.disabled = false;
    }

    num_filtersets += 1;
}

// Self explanatory
function remove_filterset(event) {
    let add_btn = document.getElementById("addfiltersetbtn");
    add_btn.classList.remove("disabled");
    add_btn.disabled = false;

    let filterset = document.getElementById("filterset" + (num_filtersets));
    document.getElementById("count_" + num_filtersets).innerText = 0;
    filterset.classList.add("hidden");

    if (num_filtersets === 2) {
        event.target.classList.add("disabled");
        event.target.disabled = true;
    }

    num_filtersets -= 1;
}

function _coerceSelectList(val) {
    if (Array.isArray(val)) return val;
    if (val === null || val === undefined || val === "") return [];
    return [val];
}

// Applies filtersets, retrieves relevant data and updates the charts.
function apply_filters() {

    scroll_to("results-section");

    let filterset_divs = [];
    for (let i = 1; i < num_filtersets + 1; i++) {
        filterset_divs.push(document.getElementById("filterset" + i));
    }

    let filtersets = [];
    let select_names = ["country", "religion", "ethnicity", "education", "party", "identities"];

    $(function () {
        show_spinner();

        let j = 0;
        let data = {};

        data.order = document.querySelector("input[name='sorting']:checked").value;
        data.limit = Number(document.querySelector("input[name='sample-size']").value || 1000);
        data["min-date"] = document.querySelector("input[name='min-date']").value || "2023-01-01";
        data["max-date"] = document.querySelector("input[name='max-date']").value || new Date().toISOString().substring(0, 10);

        for (filterset_div of filterset_divs) {
            j += 1;
            let filterset = {};

            // Changes default age entries from "0" to null
            const minAgeRaw = filterset_div.querySelector("input[name='min-age']").value;
            const maxAgeRaw = filterset_div.querySelector("input[name='max-age']").value;

            filterset["min-age"] = (minAgeRaw === "" || Number(minAgeRaw) === 0) ? null : Number(minAgeRaw);
            filterset["max-age"] = (maxAgeRaw === "" || Number(maxAgeRaw) === 0) ? null : Number(maxAgeRaw);

            // Gets other filterset data
            filterset["any-all"] = filterset_div.querySelector("input[name='any-all" + String(j) + "']:checked").value;

            let label = filterset_div.querySelector("input[name='label']").value;
            if (!label || !label.trim()) {
                label = "Filterset " + j;
                filterset_div.querySelector("input[name='label']").value = label;
            }
            filterset["label"] = label;

            filterset["color"] = document.getElementById(`color_${String(j)}`).value;

            for (select_name of select_names) {
                let selects_data = $('#' + filterset_div.id).find('select[name=' + select_name + ']').val();
                filterset[select_name] = _coerceSelectList(selects_data);
            }

            filtersets.push(filterset);
        }

        // Requests data
        data.filtersets = filtersets;

        $.ajax({
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify({
                "action": "apply_filters",
                "data": data
            }),
            url: "/api/data",
            success: async function (req) {
                await sleep(Math.random() * 250 + 500);

                datasets = JSON.parse(req).compass_datasets;

                let hist_axis = $(document).find("#select-histogram").find(":selected").val();
                update_chart_data();
                update_histogram(hist_axis);
                update_pie(question_id, question_id);
                update_counts();
                hide_spinner();
            },
            error: function (xhr) {
                const msg = (xhr.responseText && JSON.parse(xhr.responseText).status) || "Error loading data, try again.";
                show_polcomp_error(msg);
            }
        });
    });
}

// Updates counts shown below filtersets after query complete.
function update_counts() {
    for (dataset of datasets) {
        if (dataset.custom_dataset === true) {
            let dataset_id = dataset.custom_id + 1;
            document.getElementById("count_" + dataset_id).innerText = dataset.count;
        }
    }
}

// Applies new color to all charts
function set_filterset_color(event) {
    let target_id = event.target.id.split("_")[1] - 1;
    let target_label = datasets.filter(x => x.custom_id === target_id)[0].label;

    for (quadrant in quadrants) {
        let chart = quadrants[quadrant].chart;
        for (chart_dataset of chart.data.datasets) {
            if (chart_dataset.label.includes(target_label)) {
                chart_dataset.pointBackgroundColor = add_transparency(event.target.value, 0.5);
            }
        }
        chart.update();
    }

    for (dataset of datasets) {
        if (dataset.custom_id === target_id) {
            dataset.color = event.target.value;
        }
    }

    let hist_axis = document.getElementById("select-histogram").value;
    update_histogram(hist_axis);
    update_pie(question_id, question_id);
}

// Applies new filterset label to all charts
function set_filterset_label(event) {
    let target_id = event.target.id.split("_")[1] - 1;
    let new_target_label = event.target.value;

    for (quadrant in quadrants) {
        let chart = quadrants[quadrant].chart;
        for (chart_dataset of chart.data.datasets) {
            if (chart_dataset.dataset_id === target_id) {
                chart_dataset.label = new_target_label;
            }
        }
        chart.update();
    }

    for (dataset of datasets) {
        if (dataset.custom_id === target_id) {
            dataset.label = new_target_label;
        }
    }

    let hist_axis = document.getElementById("select-histogram").value;
    update_histogram(hist_axis);
    update_pie(question_id, question_id);
}

// Applies new question to pie chart
function select_table_row(event) {
    prev_question_id = question_id;
    question_id = Number(event.currentTarget.id.split('_')[1]);
    update_pie(question_id, prev_question_id);
}

// Function executed when export all data button pressed. Retrieves full results table as json
function get_all_results(event) {
    disable_button(event, "Downloading...");
    $(function () {
        $.ajax({
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify({
                "action": "get_all_results",
            }),
            url: "/api/data",
            success: async function (req) {
                await sleep(Math.random() * 1500 + 500);
                all_results = JSON.parse(req).all_results;
                enable_button(event, "Export All Data");
                var save_file = new Blob([JSON.stringify(all_results, undefined, 4)], {
                    type: 'application/json'
                });
                saveAs(save_file, "8DPolComp-All-Data.json");
            },
            error: function (req, err) {
                console.log("error: ", err);
            }
        });
    });
}

// Sends legacy data to user
function get_legacy_data(event) {
    disable_button(event, "Downloading...");
    $(function () {
        $.ajax({
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify({
                "action": "get_legacy_results",
            }),
            url: "/api/data",
            success: async function (req) {
                await sleep(Math.random() * 1500 + 500);
                legacy_results = JSON.parse(req).legacy_results;

                let link = document.getElementById('download-legacy-csv');
                link.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(legacy_results));
                link.setAttribute('download', '8DPolComp-Legacy-Data.csv');
                document.body.appendChild(link);
                document.querySelector('#download-legacy-csv').click();
                enable_button(event, "Export Legacy Data");
            },
            error: function (req, err) {
                console.log("error: ", req);
            }
        });
    });
}

// Change legacy card
function change_legacy_card(direction) {
    let legacy_filenames = [
        "2500 Submissions",
        "90 Republicans 90 Democrats",
        "350 Capitalists 350 Communists",
        "400 Voters 400 Non-Voters",
        "450 Conservatives 450 Progressives",
        "500 Non-Degree 500 Degree",
        "850 Religious 850 Non-Religious",
    ];

    if (direction === "prev") {
        current_legacy_card = (current_legacy_card === 0) ? (legacy_filenames.length - 1) : (current_legacy_card - 1);
    } else if (direction === "next") {
        current_legacy_card = (current_legacy_card === legacy_filenames.length - 1) ? 0 : (current_legacy_card + 1);
    }

    document.getElementById("legacy-img").src = `static/images/legacy-data/${legacy_filenames[current_legacy_card]}.png`;
}

function get_updated_count(ele) {
    let dataset_id = ele.id;
    let filtersets = [];
    let select_names = ["country", "religion", "ethnicity", "education", "party", "identities"];
    let filterset_div = document.getElementById("filterset" + dataset_id);

    $(function () {

        let spinner = document.getElementById("count_spinner_" + dataset_id);
        spinner.classList.add("spin-fa-icon");
        ele.classList.add("disabled-text");

        let data = {};
        data.order = document.querySelector("input[name='sorting']:checked").value;
        data.limit = Number(document.querySelector("input[name='sample-size']").value || 1000);
        data["min-date"] = document.querySelector("input[name='min-date']").value || "2023-01-01";
        data["max-date"] = document.querySelector("input[name='max-date']").value || new Date().toISOString().substring(0, 10);

        let filterset = {};

        const minAgeRaw = filterset_div.querySelector("input[name='min-age']").value;
        const maxAgeRaw = filterset_div.querySelector("input[name='max-age']").value;

        filterset["min-age"] = (minAgeRaw === "" || Number(minAgeRaw) === 0) ? null : Number(minAgeRaw);
        filterset["max-age"] = (maxAgeRaw === "" || Number(maxAgeRaw) === 0) ? null : Number(maxAgeRaw);

        filterset["any-all"] = filterset_div.querySelector("input[name='any-all" + String(dataset_id) + "']:checked").value;

        let label = filterset_div.querySelector("input[name='label']").value;
        if (!label || !label.trim()) {
            label = "Filterset " + dataset_id;
            filterset_div.querySelector("input[name='label']").value = label;
        }
        filterset["label"] = label;

        filterset["color"] = document.getElementById(`color_${String(dataset_id)}`).value;

        for (select_name of select_names) {
            let selects_data = $('#' + filterset_div.id).find('select[name=' + select_name + ']').val();
            filterset[select_name] = _coerceSelectList(selects_data);
        }
        filtersets.push(filterset);

        data.filtersets = filtersets;

        $.ajax({
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify({
                "action": "get_filterset_count",
                "data": data
            }),
            url: "/api/get_filterset_count",
            success: async function (req) {
                let counts = JSON.parse(req).counts[0];
                document.getElementById("count_" + dataset_id).innerText = counts;
                ele.classList.remove("disabled-text");
                spinner.classList.remove("spin-fa-icon");
            },
            error: function (xhr) {
                const msg = (xhr.responseText && JSON.parse(xhr.responseText).status) || "Error loading count, try again.";
                show_polcomp_error(msg);
                ele.classList.remove("disabled-text");
                spinner.classList.remove("spin-fa-icon");
            }
        });
    });
}

window.onload = function () {

    // Initialises jquery tablesorter
    $(function () {
        $("#questions-table").tablesorter();
    });

    // Adds today's date to date fields
    let date = new Date().toISOString().substring(0, 10);
    document.getElementById("todays-date").value = date;
    document.getElementById("todays-date").max = date;

    // Creaetes default histogram & pie chart
    histogram = create_histogram("society");
    question_id = 1;
    pie = create_pie(question_id);
    document.getElementById("qid_" + question_id).classList.add("row-selected");
    document.getElementById("question_text").innerText = document.getElementById("qid_" + question_id).getElementsByTagName("td")[1].textContent;
    document.getElementById("count_1").innerText = datasets.filter(x => x.custom_id === 0)[0].count;
};
