
// Access elements
let text = document.getElementById("question");
let progress = document.getElementById("progress-bar");

// Initial question
let qn = 0;
let answers = [];
let id = questions[qn]["id"];
progress.style.width = (100*qn/questions.length)+"%";
text.innerText = questions[qn]["text"];

function next_question(answer) {
    answers.push({"id": id, "answer": answer});
    if (qn+1 < questions.length) {
        qn += 1;
        id = questions[qn]["id"];
        progress.style.width = (100*qn/questions.length)+"%";
        text.innerText = questions[qn]["text"];
        console.log(answers)

    } else if (qn+1 == questions.length) {
        $(function () {
            $.ajax({
                type: "POST",
                url: "/results",
                contentType:'application/json',
                data : JSON.stringify(answers),
                success: function () {
                    window.location = "/test";
                    console.log("123")
                },
                error: function(req, err) {
                    console.log("error ", err)
                }
            })
        });
    }
}

function prev_question() {
    if (qn == 0) {
        $(function () {
            $.ajax({
                type: "POST",
                url: "/instructions",
                success: function () {
                    window.location = "/test";
                }
            })
        });

    } else if (qn < questions.length) {
        qn -= 1;
        id = questions[qn]["id"];
        answers.splice(-1);
        progress.style.width = (100*qn/questions.length)+"%";
        text.innerText = questions[qn]["text"];

    }
}