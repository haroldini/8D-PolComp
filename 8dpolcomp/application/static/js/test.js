
// DOM refs
const text = document.getElementById("question");
const progress = document.getElementById("progress-bar");
const label = document.getElementById("progress-label");

// Load questions from JSON <script> tag
function loadQuestions() {
    const el = document.getElementById("texts-data");
    if (!el) return [];

    try {
        const parsed = JSON.parse(el.textContent || "[]");
        return Array.isArray(parsed) ? parsed : [];
    } catch (e) {
        console.error("Failed to parse questions JSON:", e);
        return [];
    }
}

// Questions + state
let questions = loadQuestions();
if (!questions.length) {
    if (text) text.innerText = "Failed to load questions. Please refresh and try again.";
    throw new Error("No questions loaded");
}

// Randomise order
questions = questions.sort(() => Math.random() - 0.5);

let qn = 0;
let answers = {};
let id = questions[qn].id;
const total = questions.length;

// Render first question
progress.style.width = 100 - (100 * qn / total) + "%";
label.innerText = "1 / " + total;
text.innerText = questions[qn].text;

// Record answer and move forward
function next_question(answer) {
    answers[id] = answer;

    // Next question
    if (qn + 1 < total) {
        qn += 1;
        id = questions[qn].id;

        progress.style.width = 100 - (100 * qn / total) + "%";
        label.innerText = (qn + 1) + " / " + total;
        text.innerText = questions[qn].text;
        return;
    }

    // Submit answers to backend
    $.ajax({
        type: "POST",
        url: "/api/to_form",
        contentType: "application/json",
        data: JSON.stringify({
            answers: answers
        }),
        success: function () {
            window.location = "/form";
        },
        error: function (xhr) {
            const msg =
                (xhr.responseJSON && xhr.responseJSON.status) ||
                ("Request failed (" + xhr.status + "). Please try again.");
            alert(msg);
        }
    });
}

// Go back one question, or exit to instructions
function prev_question() {
    // Exit to instructions
    if (qn === 0) {
        $.ajax({
            type: "POST",
            url: "/api/to_instructions",
            contentType: "application/json",
            data: JSON.stringify({
                action: "to_instructions"
            }),
            success: function () {
                window.location = "/instructions";
            },
            error: function (req, err) {
                console.log("error: ", err);
            }
        });
        return;
    }

    // Previous question
    qn -= 1;
    id = questions[qn].id;

    progress.style.width = 100 - (100 * qn / total) + "%";
    label.innerText = (qn + 1) + " / " + total;
    text.innerText = questions[qn].text;
}
