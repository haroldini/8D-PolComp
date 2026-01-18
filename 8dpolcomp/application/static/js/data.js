
let num_filtersets = 1;
let preset_data = null;

let _initialPresetApplied = false;
let _applyXHR = null;

function _escapeHtml(s) {
    return String(s || "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}

function _isUUID(s) {
    const v = String(s || "").trim();
    return /^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-5][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$/.test(v);
}

function _getUrlGroupId() {
    try {
        const u = new URL(window.location.href);
        const g = (u.searchParams.get("g") || "").trim();
        if (g && _isUUID(g)) return g;
    } catch (e) {
        // ignore
    }
    return "";
}

function _getMetaGroupId() {
    const meta = document.getElementById("group-data");
    if (!meta) return "";
    const g = (meta.getAttribute("data-group") || "").trim();
    return (g && _isUUID(g)) ? g : "";
}

function _getActiveGroupId() {
    return _getUrlGroupId() || _getMetaGroupId() || "";
}

function showPresetStatus(msg) {
    const el = document.getElementById("preset-status");
    if (!el) return;
    el.innerText = msg || "";
}

function showPresetDesc(presetOrMsg) {
    const el = document.getElementById("preset-desc");
    if (!el) return;

    if (!presetOrMsg) {
        el.innerHTML = "";
        return;
    }

    if (typeof presetOrMsg === "string") {
        el.innerHTML = _escapeHtml(presetOrMsg);
        return;
    }

    const preset = presetOrMsg;
    const desc = preset.description ? _escapeHtml(preset.description) : "";

    let legend = [];
    if (Array.isArray(preset.legend)) {
        legend = preset.legend
            .filter(x => x && x.label && x.color)
            .map(x => ({ label: String(x.label), color: String(x.color) }));
    } else if (preset.filter_data && Array.isArray(preset.filter_data.filtersets)) {
        legend = preset.filter_data.filtersets
            .filter(fs => fs && fs.label && fs.color)
            .map(fs => ({ label: String(fs.label), color: String(fs.color) }));
    }

    let keyHtml = "";
    if (legend.length > 0) {
        const parts = legend.map(x =>
            `<span style="font-weight:700;color:${_escapeHtml(x.color)};">${_escapeHtml(x.label)}</span>`
        );
        keyHtml = `<span style="display:block;margin-top:6px;opacity:0.95;">
            <span style="opacity:0.85;">Key:</span> ${parts.join(` <span style="opacity:0.85;">vs</span> `)}
        </span>`;
    }

    el.innerHTML = desc + keyHtml;
}

function _todayISO() {
    return new Date().toISOString().substring(0, 10);
}

function _get_all_party_values() {
    const sel = document.querySelector("#filterset1 select[name='party']");
    if (!sel) return [];
    const vals = [];
    for (const opt of sel.options) {
        if (opt && opt.value) vals.push(opt.value);
    }
    return [...new Set(vals)];
}

function _expand_party_tokens(partyArr) {
    if (!Array.isArray(partyArr)) return [];
    if (!partyArr.includes("__VOTERS__")) return partyArr;

    const exclude = new Set([
        "Other-I cannot vote",
        "Other-I do not vote",
        "Other-My party is not here",
        "Other-My country is not here"
    ]);

    return _get_all_party_values().filter(v => v && !exclude.has(v));
}

function _emptyFilterset(label, color, groupIdOrEmpty) {
    return {
        label: label,
        "min-age": null,
        "max-age": null,
        "any-all": "any",
        color: color,
        "group-ids": groupIdOrEmpty ? [groupIdOrEmpty] : [],
        country: [],
        religion: [],
        ethnicity: [],
        education: [],
        party: [],
        identities: []
    };
}

function _injectGroupPresets() {
    const gid = _getActiveGroupId();
    if (!gid) return { groupOnly: null, groupVsAll: null };

    if (!preset_data || typeof preset_data !== "object") preset_data = {};
    if (!Array.isArray(preset_data.presets)) preset_data.presets = [];

    // Remove any older injected group presets (avoid clutter)
    preset_data.presets = preset_data.presets.filter(p => {
        const k = p && p.key ? String(p.key) : "";
        return !(k.startsWith("group_only_") || k.startsWith("group_vs_all_"));
    });

    const keyOnly = "group_only_" + gid;
    const keyVs = "group_vs_all_" + gid;

    const groupOnlyPreset = {
        key: keyOnly,
        label: "Group",
        description: "Only show results from this group.",
        filter_data: {
            order: "random",
            limit: 1000,
            "min-date": "2023-01-01",
            "max-date": "today",
            filtersets: [
                _emptyFilterset("Group", "#0db52e", gid)
            ]
        }
    };

    const groupVsAllPreset = {
        key: keyVs,
        label: "Group vs All Users",
        description: "Compare this group vs all users.",
        filter_data: {
            order: "random",
            limit: 1000,
            "min-date": "2023-01-01",
            "max-date": "today",
            filtersets: [
                _emptyFilterset("Group", "#0db52e", gid),
                _emptyFilterset("All Users", "#0d56b5", "")
            ]
        }
    };

    // Put both at the top, group-only first
    preset_data.presets.unshift(groupVsAllPreset);
    preset_data.presets.unshift(groupOnlyPreset);

    return { groupOnly: keyOnly, groupVsAll: keyVs };
}

async function load_presets() {
    try {
        const resp = await fetch("/static/data/samples/filtersets.json", { cache: "no-store" });
        if (!resp.ok) return;

        const data = await resp.json();
        if (!data || typeof data !== "object") return;

        preset_data = data;

        _injectGroupPresets();
        render_preset_dropdown();
    } catch (e) {
        // ignore
    }
}

function render_preset_dropdown() {
    const sel = document.getElementById("preset-select");
    if (!sel) return;

    const presets = preset_data && Array.isArray(preset_data.presets) ? preset_data.presets : [];
    if (presets.length === 0) return;

    const injected = _injectGroupPresets();
    const hasGroup = !!injected.groupOnly;

    sel.innerHTML = "";
    for (const preset of presets) {
        const opt = document.createElement("option");
        opt.value = preset.key;
        opt.textContent = preset.label || preset.key;
        sel.appendChild(opt);
    }

    // Default selection:
    // - if group is active -> Group ONLY
    // - else -> all_users (or first available)
    const preferredKey = hasGroup ? injected.groupOnly : "all_users";
    const hasPreferred = presets.some(p => p && p.key === preferredKey);

    sel.value = hasPreferred ? preferredKey : (presets[0].key || "all_users");
    sel.disabled = false;

    const active = presets.find(p => p.key === sel.value);
    showPresetStatus("");
    showPresetDesc(active || "");

    if (!_initialPresetApplied) {
        _initialPresetApplied = true;
        apply_preset(sel.value);
    }
}

function _set_num_filtersets(n) {
    n = Math.max(1, Math.min(4, Number(n || 1)));

    for (let i = 2; i <= 4; i++) {
        const div = document.getElementById("filterset" + i);
        if (!div) continue;

        if (i <= n) {
            div.classList.remove("hidden");
        } else {
            div.classList.add("hidden");
            const countEl = document.getElementById("count_" + i);
            if (countEl) countEl.innerText = 0;
        }
    }

    const addBtn = document.getElementById("addfiltersetbtn");
    const rmBtn = document.getElementById("rmfiltersetbtn");

    if (addBtn) {
        if (n >= 4) {
            addBtn.classList.add("disabled");
            addBtn.disabled = true;
        } else {
            addBtn.classList.remove("disabled");
            addBtn.disabled = false;
        }
    }

    if (rmBtn) {
        if (n <= 1) {
            rmBtn.classList.add("disabled");
            rmBtn.disabled = true;
        } else {
            rmBtn.classList.remove("disabled");
            rmBtn.disabled = false;
        }
    }

    num_filtersets = n;
}

function _apply_filterset_to_div(filterset_div, filterset_obj, idx) {
    if (!filterset_div || !filterset_obj) return;

    const labelEl = filterset_div.querySelector("input[name='label']");
    if (labelEl) labelEl.value = filterset_obj.label || ("Filterset " + idx);

    const groupEl = filterset_div.querySelector("input[name='group-id']");
    const gids = Array.isArray(filterset_obj["group-ids"]) ? filterset_obj["group-ids"] : [];
    if (groupEl) groupEl.value = gids[0] || "";

    const minAgeEl = filterset_div.querySelector("input[name='min-age']");
    const maxAgeEl = filterset_div.querySelector("input[name='max-age']");
    if (minAgeEl) minAgeEl.value = (filterset_obj["min-age"] === null || filterset_obj["min-age"] === undefined) ? "" : String(filterset_obj["min-age"]);
    if (maxAgeEl) maxAgeEl.value = (filterset_obj["max-age"] === null || filterset_obj["max-age"] === undefined) ? "" : String(filterset_obj["max-age"]);

    const mode = filterset_obj["any-all"] || "any";
    const radio = filterset_div.querySelector("input[name='any-all" + String(idx) + "'][value='" + mode + "']");
    if (radio) radio.checked = true;

    const colorEl = document.getElementById("color_" + String(idx));
    if (colorEl && filterset_obj.color) colorEl.value = filterset_obj.color;

    const select_names = ["country", "religion", "ethnicity", "education", "party", "identities"];
    for (const name of select_names) {
        const vals = Array.isArray(filterset_obj[name]) ? filterset_obj[name] : [];
        const $sel = $('#' + filterset_div.id).find('select[name=' + name + ']');
        if ($sel && $sel.length > 0) {
            $sel.val(vals);
            if (typeof $sel.selectpicker === "function") {
                $sel.selectpicker("refresh");
            }
        }
    }
}

function apply_preset(preset_key) {
    showPresetStatus("");

    const presets = preset_data && Array.isArray(preset_data.presets) ? preset_data.presets : [];
    const preset = presets.find(p => p.key === preset_key);
    if (!preset || !preset.filter_data) {
        showPresetStatus("Preset not found.");
        return;
    }

    showPresetDesc(preset);

    const fd = preset.filter_data;

    const limitEl = document.querySelector("input[name='sample-size']");
    if (limitEl) limitEl.value = String(fd.limit || 1000);

    const order = fd.order === "recent" ? "recent" : "random";
    const radio = document.querySelector("input[name='sorting'][value='" + order + "']");
    if (radio) radio.checked = true;

    const minDateEl = document.querySelector("input[name='min-date']");
    const maxDateEl = document.querySelector("input[name='max-date']");
    if (minDateEl) minDateEl.value = fd["min-date"] || "2023-01-01";

    let maxD = fd["max-date"] || "today";
    if (maxD === "today") maxD = _todayISO();
    if (maxDateEl) maxDateEl.value = maxD;

    const filtersets_raw = Array.isArray(fd.filtersets) ? fd.filtersets : [];
    if (filtersets_raw.length === 0) {
        showPresetStatus("Preset has no filtersets.");
        return;
    }

    const filtersets = filtersets_raw.map(fs => {
        const c = JSON.parse(JSON.stringify(fs));
        if (!Array.isArray(c["group-ids"])) c["group-ids"] = [];
        if (Array.isArray(c.party)) c.party = _expand_party_tokens(c.party);
        return c;
    });

    _set_num_filtersets(filtersets.length);

    for (let i = 1; i <= num_filtersets; i++) {
        const div = document.getElementById("filterset" + i);
        _apply_filterset_to_div(div, filtersets[i - 1], i);
    }

    apply_filters_silent();
}

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

function _readGroupIds(filterset_div) {
    const el = filterset_div.querySelector("input[name='group-id']");
    if (!el) return [];
    const v = String(el.value || "").trim();
    if (!v) return [];
    if (!_isUUID(v)) return null; // invalid
    return [v];
}

function _build_filter_payload() {
    let filterset_divs = [];
    for (let i = 1; i < num_filtersets + 1; i++) {
        filterset_divs.push(document.getElementById("filterset" + i));
    }

    let filtersets = [];
    let select_names = ["country", "religion", "ethnicity", "education", "party", "identities"];

    let j = 0;
    let data = {};

    data.order = document.querySelector("input[name='sorting']:checked").value;
    data.limit = Number(document.querySelector("input[name='sample-size']").value || 1000);
    data["min-date"] = document.querySelector("input[name='min-date']").value || "2023-01-01";
    data["max-date"] = document.querySelector("input[name='max-date']").value || new Date().toISOString().substring(0, 10);

    for (const filterset_div of filterset_divs) {
        j += 1;
        let filterset = {};

        const groupIds = _readGroupIds(filterset_div);
        if (groupIds === null) {
            if (typeof show_polcomp_error === "function") {
                show_polcomp_error("Invalid Group ID (must be a UUID).");
            }
            return null;
        }
        filterset["group-ids"] = groupIds;

        const minAgeRaw = filterset_div.querySelector("input[name='min-age']").value;
        const maxAgeRaw = filterset_div.querySelector("input[name='max-age']").value;

        filterset["min-age"] = (minAgeRaw === "" || Number(minAgeRaw) === 0) ? null : Number(minAgeRaw);
        filterset["max-age"] = (maxAgeRaw === "" || Number(maxAgeRaw) === 0) ? null : Number(maxAgeRaw);

        filterset["any-all"] = filterset_div.querySelector("input[name='any-all" + String(j) + "']:checked").value;

        let label = filterset_div.querySelector("input[name='label']").value;
        if (!label || !label.trim()) {
            label = "Filterset " + j;
            filterset_div.querySelector("input[name='label']").value = label;
        }
        filterset["label"] = label;

        filterset["color"] = document.getElementById(`color_${String(j)}`).value;

        for (const select_name of select_names) {
            let selects_data = $('#' + filterset_div.id).find('select[name=' + select_name + ']').val();
            filterset[select_name] = _coerceSelectList(selects_data);
        }

        filtersets.push(filterset);
    }

    data.filtersets = filtersets;
    return data;
}

function _run_apply_filters(data) {
    if (!data) return;

    if (_applyXHR && _applyXHR.readyState !== 4) {
        _applyXHR.abort();
    }

    show_spinner();

    _applyXHR = $.ajax({
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
            if (xhr && xhr.statusText === "abort") return;

            let msg = "Error loading data, try again.";
            try {
                msg = (xhr.responseText && JSON.parse(xhr.responseText).status) || msg;
            } catch (e) {
                // ignore
            }
            if (typeof show_polcomp_error === "function") {
                show_polcomp_error(msg);
            }
        }
    });
}

function apply_filters() {
    scroll_to("results-section");
    const data = _build_filter_payload();
    _run_apply_filters(data);
}

function apply_filters_silent() {
    const data = _build_filter_payload();
    _run_apply_filters(data);
}

function update_counts() {
    for (const dataset of datasets) {
        if (dataset.custom_dataset === true) {
            let dataset_id = dataset.custom_id + 1;
            document.getElementById("count_" + dataset_id).innerText = dataset.count;
        }
    }
}

function set_filterset_color(event) {
    let target_id = event.target.id.split("_")[1] - 1;
    let target_label = datasets.filter(x => x.custom_id === target_id)[0].label;

    for (const quadrant in quadrants) {
        let chart = quadrants[quadrant].chart;
        for (const chart_dataset of chart.data.datasets) {
            if (chart_dataset.label.includes(target_label)) {
                chart_dataset.pointBackgroundColor = add_transparency(event.target.value, 0.5);
            }
        }
        chart.update();
    }

    for (const dataset of datasets) {
        if (dataset.custom_id === target_id) {
            dataset.color = event.target.value;
        }
    }

    let hist_axis = document.getElementById("select-histogram").value;
    update_histogram(hist_axis);
    update_pie(question_id, question_id);
}

function set_filterset_label(event) {
    let target_id = event.target.id.split("_")[1] - 1;
    let new_target_label = event.target.value;

    for (const quadrant in quadrants) {
        let chart = quadrants[quadrant].chart;
        for (const chart_dataset of chart.data.datasets) {
            if (chart_dataset.dataset_id === target_id) {
                chart_dataset.label = new_target_label;
            }
        }
        chart.update();
    }

    for (const dataset of datasets) {
        if (dataset.custom_id === target_id) {
            dataset.label = new_target_label;
        }
    }

    let hist_axis = document.getElementById("select-histogram").value;
    update_histogram(hist_axis);
    update_pie(question_id, question_id);
}

function select_table_row(event) {
    prev_question_id = question_id;
    question_id = Number(event.currentTarget.id.split('_')[1]);
    update_pie(question_id, prev_question_id);
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

        const groupIds = _readGroupIds(filterset_div);
        if (groupIds === null) {
            if (typeof show_polcomp_error === "function") {
                show_polcomp_error("Invalid Group ID (must be a UUID).");
            }
            ele.classList.remove("disabled-text");
            spinner.classList.remove("spin-fa-icon");
            return;
        }
        filterset["group-ids"] = groupIds;

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

        for (const select_name of select_names) {
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
                let msg = "Error loading count, try again.";
                try {
                    msg = (xhr.responseText && JSON.parse(xhr.responseText).status) || msg;
                } catch (e) {
                    // ignore
                }
                if (typeof show_polcomp_error === "function") {
                    show_polcomp_error(msg);
                }
                ele.classList.remove("disabled-text");
                spinner.classList.remove("spin-fa-icon");
            }
        });
    });
}

window.onload = function () {
    load_presets();

    $(function () {
        $("#questions-table").tablesorter();
    });

    let date = new Date().toISOString().substring(0, 10);
    document.getElementById("todays-date").value = date;
    document.getElementById("todays-date").max = date;

    histogram = create_histogram("society");
    question_id = 1;
    pie = create_pie(question_id);
    document.getElementById("qid_" + question_id).classList.add("row-selected");
    document.getElementById("question_text").innerText =
        document.getElementById("qid_" + question_id).getElementsByTagName("td")[1].textContent;

    const d0 = Array.isArray(datasets) ? datasets.find(x => x.custom_id === 0) : null;
    document.getElementById("count_1").innerText = d0 ? d0.count : 0;
};
