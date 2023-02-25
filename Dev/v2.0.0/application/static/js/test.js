

// Access elements
let text = document.getElementById("question");
let progress = document.getElementById("progress-bar");

// Initial question
let questions = $('#texts').data("texts").sort( () => Math.random() - 0.5);
let qn = 0;
let answers = {};
let id = questions[qn]["id"];
progress.style.width = (100*qn/questions.length)+"%";
text.innerText = questions[qn]["text"];

function next_question(answer) {

    // Store answer, display next question
    answers[id] = answer;
    if (qn+1 < questions.length) {
        qn += 1;
        id = questions[qn]["id"];
        progress.style.width = (100*qn/questions.length)+"%";
        text.innerText = questions[qn]["text"];
        console.log(answers)
    
    // Goto results page, pass answers to backend
    } else if (qn+1 == questions.length) {
        $(function () {
            $.ajax({
                type: "POST",
                url: "/test",
                contentType:'application/json',
                data : JSON.stringify({"action": "to_results", "answers": answers}),
                success: function () {
                    window.location = "/results";
                },
                error: function(req, err) {
                    console.log("error: ", err)
                }
            })
        });
    }
}

function prev_question() {

    // Return to instructions if on first question
    if (qn == 0) {
        $(function () {
            $.ajax({
                type: "POST",
                contentType:'application/json',
                data : JSON.stringify({"action": "to_instructions"}),
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
        id = questions[qn]["id"];
        answers.splice(-1);
        progress.style.width = (100*qn/questions.length)+"%";
        text.innerText = questions[qn]["text"];
    }
}