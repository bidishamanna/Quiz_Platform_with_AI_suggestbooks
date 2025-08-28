// static/js/category.js
$(document).ready(function () {
    console.log("AJAX Script loaded");

   
    $('.view-subjects-btn').click(function () {
    const btn = $(this);
    const categoryId = btn.data('category-id');
    const container = $('#subjects-' + categoryId);
    const subjectList = container.find('ul');
    const loader = $('#loader-' + categoryId);

    if (container.hasClass('d-none')) {
    container.removeClass('d-none');
    loader.show();

    // Only load once
    if (subjectList.children().length === 0) {
        $.ajax({
        url: '/subject/by-category/' + categoryId + '/',
        type: 'GET',
        success: function (data) {
            loader.hide();
            if (data.subjects.length > 0) {
            $.each(data.subjects, function (index, subject) {
                subjectList.append('<li class="list-group-item bg-light text-dark">' + subject.name + '</li>');
            });
            } else {
            subjectList.append('<li class="list-group-item bg-light text-muted">No subjects found.</li>');
            }
        },
        error: function () {
            loader.hide();
            subjectList.append('<li class="list-group-item bg-danger text-white">Error loading subjects.</li>');
        }
        });
    }
    } else {
    container.addClass('d-none');
    }
    });

    $("#add_question_btn").click(function (event) {
        event.preventDefault();

        const data = {
            category: $("#category").val(),
            subject: $("#subject").val(),
            set: $("#set").val(),
            question_text: $("#question_text").val().trim(),
            option_a: $("#option_a").val().trim(),
            option_b: $("#option_b").val().trim(),
            option_c: $("#option_c").val().trim(),
            option_d: $("#option_d").val().trim(),
            correct_option: $("#correct_option").val(),
            csrfmiddlewaretoken: $("input[name='csrfmiddlewaretoken']").val()
        };

        // Client-side validation
        if (Object.values(data).some(val => val === "")) {
            $("#question_acknowledge")
                .removeClass("d-none alert-success")
                .addClass("alert-danger")
                .text("All fields are required.");
            return;
        }

        $.ajax({
            url: "/questions/add_questions/",
            method: "POST",
            data: data,
            success: function (response) {
                $("#question_acknowledge")
                    .removeClass("d-none alert-danger")
                    .addClass("alert-success")
                    .text(response.message);

                // Reset form
                $("#add-question-form")[0].reset();
                $("#subject").html('<option value="">--Choose Subject--</option>').prop("disabled", true);
                $("#set").html('<option value="">--Choose Set--</option>').prop("disabled", true);

                // Refresh table rows
                $.get("/questions/get_rows/", function (data) {
                    $("#question-table-body").html(data.html);
                });
            },
            error: function (error) {
                const message = error.responseJSON?.message || "Something went wrong.";
                $("#question_acknowledge")
                    .removeClass("d-none alert-success")
                    .addClass("alert-danger")
                    .text(message);
            }
        });
    });
    
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

    $(document).ready(function () {
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

});







