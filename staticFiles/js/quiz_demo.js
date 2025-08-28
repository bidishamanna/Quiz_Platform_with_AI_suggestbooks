$(document).ready(function () {
    console.log("AJAX Script loaded");
    let questions = [];
    let currentIndex = 0;
    let correctCount = 0;
    let wrongCount = 0;

    function renderQuestion() {
        if (!questions || questions.length === 0) {
            $("#q-text").text("No questions available.");
            return;
        }

        if (currentIndex >= questions.length) {
            $("#quiz-area").addClass("d-none");  //// #quiz-area invisible হয়ে যাবে।
            $("#score-area").removeClass("d-none");
            $("#total-q").text(questions.length);
            $("#correct-q").text(correctCount);
            $("#wrong-q").text(wrongCount);
            return;
        }

        const q = questions[currentIndex];
        $("#q-header").text(`Question ${currentIndex + 1}:`);
        $("#q-text").text(q.text).css("color", "white"); // (q.text)---const q ...current question ,showing in white colour 

        const optionsDiv = $("#options-container");
        optionsDiv.empty();

        for (let i = 1; i <= 4; i++) {
            optionsDiv.append(`
                <div class="form-check text-white">
                    <input class="form-check-input" type="radio" name="selected_option" value="${i}" required>
                    <label class="form-check-label">${q["option" + i]}</label>
                </div>
            `);
        }
    }

    
    $.ajax({
        url: "/quiz/get_questions/",
        method: "GET",
        success: function (data) {
            if (data.questions && data.questions.length > 0) {
                questions = data.questions; // all questions stored in one go
                renderQuestion();
            } else {
                $("#q-text").text("No questions received from server.");
            }
        },
        error: function () {
            $("#q-text").text("Failed to load questions.");
        }
    });

    $("#answer-form").submit(function (e) {
        e.preventDefault();

        const selected = $('input[name="selected_option"]:checked');  //checked'-- check which radio button user select 
        if (!selected.length) return;

        const payload = {
            question_id: questions[currentIndex].id,  //const payload = {
            selected_option: selected.val()                         //   question_id: 5,
                                                                    //   selected_option: "2"
                                                                    // };

        };

    $.ajax({
        url: "/quiz/submit_answer/",
        method: "POST",
        headers: {
            "X-CSRFToken": $("input[name='csrfmiddlewaretoken']").val()
        },
        contentType: "application/json", //application/json means → "I’m sending JSON data"
        data: JSON.stringify(payload),//It converts a JavaScript object → into a JSON-formatted string.
                                                                        // '{"question_id":5,"selected_option":"2"}'

        success: function (data) {
            if (data.is_correct) {
                correctCount++;
            } else {
                wrongCount++;
            }
            currentIndex++;
            renderQuestion();
        },
        error: function () {
            alert("Something went wrong while submitting your answer.");
        }
        });
    });
});


