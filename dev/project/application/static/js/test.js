// Assign test elements to variables
let text = document.getElementById("question");
let progress = document.getElementById("progress-bar");
let label = document.getElementById("progress-label")

// Render first question
let questions = $('#texts').data("texts").sort( () => Math.random() - 0.5);
let qn = 0;
let answers = {};
let id = questions[qn].id;
progress.style.width = 100-(100*qn/questions.length)+"%";
text.innerText = questions[qn].text;

// Triggers when answer given
function next_question(answer) {

    // Store answer, display next question
    answers[id] = answer;
    if (qn+1 < questions.length) {
        qn += 1;
        id = questions[qn].id;
        progress.style.width = 100-(100*qn/questions.length)+"%";
        label.innerText = qn+1 + " / " + "100";
        text.innerText = questions[qn].text;
    
    // Goto form page, pass answers to backend
    } else if (qn+1 == questions.length) {
        $(function () {
            $.ajax({
                type: "POST",
                url: "/test",
                contentType:'application/json',
                data : JSON.stringify({
                    "action": "to_form", 
                    "answers": answers
                }),
                success: function () {
                    window.location = "/form";
                },
                error: function(req, err) {
                    console.log("error: ", err)
                }
            })
        });
    }
}

// Triggers when back button pressed
function prev_question() {

    // Return to instructions if on first question
    if (qn == 0) {
        $(function () {
            $.ajax({
                type: "POST",
                contentType:'application/json',
                data : JSON.stringify({
                    "action": "to_instructions"
                }),
                url: "/test",
                success: function () {
                    window.location = "/instructions";
                },
                error: function(req, err) {
                    console.log("error: ", err)
                }
            })
        });

    // Return to previous question if not on first question
    } else if (qn < questions.length) {
        qn -= 1;
        id = questions[qn].id;
        progress.style.width = 100-(100*qn/questions.length)+"%";
        label.innerText = qn+1 + " / " + "100";
        text.innerText = questions[qn].text;
    }
}