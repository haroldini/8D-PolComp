
// Loaded from static/data/samples/scores.json
let key_vals = {};

// Tracks the current selected sample key
let current_key = "recent1000";

// 1000 Recent state
let recent1000_loaded = false;
let recent1000_loading = false;
let recent1000_mean = null;
let recent1000_count = 0;
let recent1000_scores = [];

let samples_expanded = false;

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

function _sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

function _meanFromScores(scores) {
    const out = _zeroAxes();
    const axes = Object.keys(out);
    if (!Array.isArray(scores) || scores.length === 0) {
        return out;
    }

    for (const s of scores) {
        if (!s) {
            continue;
        }
        for (const ax of axes) {
            const v = Number(s[ax]);
            if (!Number.isNaN(v)) {
                out[ax] += v;
            }
        }
    }

    for (const ax of axes) {
        out[ax] = out[ax] / scores.length;
    }
    return out;
}

async function load_sample_scores() {
    try {
        const resp = await fetch("/static/data/samples/scores.json", { cache: "no-store" });
        if (!resp.ok) {
            return;
        }

        const data = await resp.json();
        if (data && typeof data === "object") {
            key_vals = data;
        }
    } catch (e) {
        // ignore
    }

    if (!key_vals || typeof key_vals !== "object") {
        key_vals = {};
    }

    // Ensure recent1000 exists (average will replace after /api/data loads)
    key_vals["recent1000"] = _zeroAxes();
}

load_sample_scores();


// Additional compass quadrants for "The Axes" section.
const quadrants_sample = {
    "upper_left_sample": {
        "x": "society",
        "y": "politics",
        "colors": ["#93daf8", "#afafaf", "#afafaf", "#c9e5bd"],
        "chart": null,
        "data": null
    },
    "upper_right_sample": {
        "x": "economics",
        "y": "state",
        "colors": ["#afafaf", "#93daf8", "#c9e5bd", "#afafaf"],
        "chart": null,
        "data": null
    },
    "lower_left_sample": {
        "x": "diplomacy",
        "y": "government",
        "colors": ["#afafaf", "#c9e5bd", "#93daf8", "#afafaf"],
        "chart": null,
        "data": null
    },
    "lower_right_sample": {
        "x": "technology",
        "y": "religion",
        "colors": ["#c9e5bd", "#afafaf", "#afafaf", "#93daf8"],
        "chart": null,
        "data": null
    }
};

function _findChartDatasetByLabel(chart, label) {
    if (!chart || !chart.data || !Array.isArray(chart.data.datasets)) {
        return null;
    }
    for (const ds of chart.data.datasets) {
        if (ds && ds.label === label) {
            return ds;
        }
    }
    return null;
}

function _updateMarkerForQuadrants(quadrantsObj, axes) {
    if (!axes || typeof axes !== "object") {
        return;
    }

    for (const quadrant in quadrantsObj) {
        const chart = quadrantsObj[quadrant].chart;
        if (!chart) {
            continue;
        }

        const marker = _findChartDatasetByLabel(chart, "Marker");
        if (!marker || !Array.isArray(marker.data) || marker.data.length === 0) {
            continue;
        }

        marker.data[0] = {
            x: axes[quadrantsObj[quadrant].x],
            y: axes[quadrantsObj[quadrant].y]
        };

        if (typeof calc_point_props === "function" && typeof add_transparency === "function") {
            const props = calc_point_props({ count: 501 }, 501);
            const radius = props[1];

            marker.pointRadius = radius;
            marker.pointBackgroundColor = add_transparency("#262626", 1);
            marker.pointBorderWidth = radius / 2;
            marker.pointBorderColor = add_transparency("#262626", 1);
        }

        chart.update();
    }
}

function _setRecentCloudVisible(visible) {
    for (const quadrant in quadrants) {
        const chart = quadrants[quadrant].chart;
        if (!chart) {
            continue;
        }

        const cloud = _findChartDatasetByLabel(chart, "1000 Recent");
        if (!cloud) {
            continue;
        }

        if (!visible) {
            cloud.data = [];
            chart.update();
            continue;
        }

        const xk = quadrants[quadrant].x;
        const yk = quadrants[quadrant].y;

        const vals = [];
        for (const s of recent1000_scores) {
            if (!s) {
                continue;
            }
            vals.push({
                x: s[xk],
                y: s[yk]
            });
        }

        cloud.data = vals;

        if (typeof calc_point_props === "function") {
            const props = calc_point_props({ count: recent1000_count }, recent1000_count);
            const transparency = props[0];
            const radius = props[1];

            cloud.pointRadius = radius / 2;
            cloud.pointBackgroundColor = add_transparency("#0d56b5", transparency);
            cloud.pointBorderWidth = radius / 4;
            cloud.pointBorderColor = add_transparency("#262626", transparency);
        }

        chart.update();
    }
}

function _buildRecent1000Payload() {
    return {
        order: "recent",
        limit: 1000,
        "min-date": "2023-01-01",
        "max-date": new Date().toISOString().substring(0, 10),
        filtersets: [
            {
                label: "1000 Recent",
                "min-age": null,
                "max-age": null,
                "any-all": "any",
                color: "#0d56b5",
                "group-ids": [],
                country: [],
                religion: [],
                ethnicity: [],
                education: [],
                party: [],
                identities: []
            }
        ]
    };
}

function load_recent1000() {
    if (recent1000_loaded || recent1000_loading) {
        return;
    }

    recent1000_loading = true;

    const start = Date.now();
    if (typeof show_spinner === "function") {
        show_spinner();
    }

    $.ajax({
        type: "POST",
        contentType: "application/json",
        data: JSON.stringify({
            action: "apply_filters",
            data: _buildRecent1000Payload()
        }),
        url: "/api/data",
        success: async function (req) {
            try {
                let parsed = req;
                if (typeof parsed === "string") {
                    parsed = JSON.parse(parsed);
                }

                let cds = parsed && parsed.compass_datasets ? parsed.compass_datasets : [];
                if (typeof cds === "string") {
                    cds = JSON.parse(cds);
                }
                if (!Array.isArray(cds)) {
                    cds = [];
                }

                cds = cds.filter(d => !(d && d.name === "your_results"));

                const ds = cds.find(d => d && Array.isArray(d.all_scores));
                if (!ds) {
                    throw new Error("No dataset returned.");
                }

                recent1000_scores = Array.isArray(ds.all_scores) ? ds.all_scores : [];
                recent1000_count = Number(ds.count || recent1000_scores.length || 0);

                const mean = (ds.mean_scores && typeof ds.mean_scores === "object")
                    ? ds.mean_scores
                    : _meanFromScores(recent1000_scores);

                recent1000_mean = mean;

                if (!key_vals || typeof key_vals !== "object") {
                    key_vals = {};
                }
                key_vals["recent1000"] = recent1000_mean;

                recent1000_loaded = true;
                recent1000_loading = false;

                if (current_key === "recent1000") {
                    _setRecentCloudVisible(true);
                    _updateMarkerForQuadrants(quadrants, recent1000_mean);
                    _updateMarkerForQuadrants(quadrants_sample, recent1000_mean);
                } else {
                    _setRecentCloudVisible(false);
                }
            } catch (e) {
                recent1000_loaded = false;
                recent1000_loading = false;
                _setRecentCloudVisible(false);
            }

            const minDuration = 500 + Math.random() * 250;
            const elapsed = Date.now() - start;
            const wait = Math.max(0, minDuration - elapsed);
            await _sleep(wait);

            if (typeof hide_spinner === "function") {
                hide_spinner();
            }
        },
        error: async function () {
            recent1000_loaded = false;
            recent1000_loading = false;
            _setRecentCloudVisible(false);

            const minDuration = 500 + Math.random() * 250;
            const elapsed = Date.now() - start;
            const wait = Math.max(0, minDuration - elapsed);
            await _sleep(wait);

            if (typeof hide_spinner === "function") {
                hide_spinner();
            }
        }
    });
}

function _get_sample_name(key) {
    const btn = document.querySelector(`[data-sample-key="${key}"]`);
    if (!btn) {
        return key;
    }
    return btn.getAttribute("aria-label") || key;
}

function _set_selected_sample_name(key) {
    const el = document.getElementById("samples-selected-name");
    if (!el) {
        return;
    }
    el.innerText = _get_sample_name(key);
}

function _select_icon(event) {
    const icons = document.getElementsByClassName("icon-button");
    for (const icon of icons) {
        icon.classList.remove("icon-selected");
    }

    if (event && event.currentTarget) {
        event.currentTarget.classList.add("icon-selected");
    }
}

function _update_samples_collapsed_height() {
    const list = document.getElementById("samples-list");
    if (!list || !list.classList.contains("samples-collapsed")) {
        return;
    }

    const icons = Array.from(list.querySelectorAll(".icon-button"));
    if (icons.length === 0) {
        return;
    }

    const listRect = list.getBoundingClientRect();

    const pos = [];
    let minTop = Infinity;

    for (const icon of icons) {
        const r = icon.getBoundingClientRect();
        const topRel = r.top - listRect.top;
        const bottomRel = r.bottom - listRect.top;
        pos.push({ topRel, bottomRel });
        if (topRel < minTop) {
            minTop = topRel;
        }
    }

    if (!Number.isFinite(minTop)) {
        return;
    }

    const tol = 1;

    let maxBottomRel = 0;
    for (const p of pos) {
        if (Math.abs(p.topRel - minTop) <= tol) {
            maxBottomRel = Math.max(maxBottomRel, p.bottomRel);
        }
    }

    let secondRowTopRel = Infinity;
    for (const p of pos) {
        if (p.topRel > minTop + tol) {
            secondRowTopRel = Math.min(secondRowTopRel, p.topRel);
        }
    }

    let maxH = list.scrollHeight;

    if (Number.isFinite(secondRowTopRel)) {
        const cs = getComputedStyle(list);
        const padBottom = parseFloat(cs.paddingBottom) || 0;

        const available = Math.max(0, secondRowTopRel - maxBottomRel);
        const extra = Math.min(padBottom, Math.max(0, available - 1));

        maxH = maxBottomRel + extra;
    }

    list.style.maxHeight = maxH + "px";
}

function toggle_samples_more() {
    const list = document.getElementById("samples-list");
    const link = document.getElementById("samples-link");
    if (!list || !link) {
        return;
    }

    const btn = link.firstElementChild;
    if (!btn) {
        return;
    }

    if (!samples_expanded) {
        samples_expanded = true;

        list.classList.remove("samples-labels-shown");
        list.classList.remove("samples-collapsed");
        list.classList.add("samples-labels-shown");

        const onEnd = function (e) {
            if (e && e.propertyName !== "max-height") {
                return;
            }
            list.removeEventListener("transitionend", onEnd);
        };

        list.addEventListener("transitionend", onEnd);

        requestAnimationFrame(() => {
            list.style.maxHeight = list.scrollHeight + "px";
        });

        btn.innerText = "Show less...";
        return;
    }

    samples_expanded = false;

    list.classList.remove("samples-labels-shown");
    list.classList.add("samples-collapsed");

    requestAnimationFrame(() => {
        _update_samples_collapsed_height();
    });

    btn.innerText = "Show more...";
}


// Updates "Sample Compasses" and "The Axes" quadrants when new sample enabled
function update_index_chart(event, key) {
    _select_icon(event);
    _set_selected_sample_name(key);

    current_key = key;

    if (key === "recent1000") {
        if (!recent1000_loaded) {
            load_recent1000();
            return;
        }

        _setRecentCloudVisible(true);

        if (recent1000_mean) {
            _updateMarkerForQuadrants(quadrants, recent1000_mean);
            _updateMarkerForQuadrants(quadrants_sample, recent1000_mean);
        }
        return;
    }

    _setRecentCloudVisible(false);

    if (!key_vals[key] || typeof key_vals[key] !== "object") {
        return;
    }

    _updateMarkerForQuadrants(quadrants, key_vals[key]);
    _updateMarkerForQuadrants(quadrants_sample, key_vals[key]);
}


// Creates quadrants for "The Axes"
function create_axis_clones() {
    if (typeof create_quadrant !== "function") {
        return;
    }
    for (const quadrant_sample in quadrants_sample) {
        create_quadrant(quadrant_sample, quadrants_sample);
    }
}

create_axis_clones();

window.onload = function () {
    current_key = "recent1000";
    _set_selected_sample_name(current_key);

    requestAnimationFrame(() => {
        _update_samples_collapsed_height();
    });

    window.addEventListener("resize", function () {
        const list = document.getElementById("samples-list");
        if (!list) {
            return;
        }

        if (samples_expanded) {
            requestAnimationFrame(() => {
                list.style.maxHeight = list.scrollHeight + "px";
            });
            return;
        }

        requestAnimationFrame(() => {
            _update_samples_collapsed_height();
        });
    });

    _setRecentCloudVisible(false);
    load_recent1000();
};
