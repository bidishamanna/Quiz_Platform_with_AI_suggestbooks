$(document).ready(function () {
    let currentSetId = null;
    let currentAttemptId = null;
    let currentQuestionId = null;
    let score = 0;
    let totalQuestions = 0;
    let userAnswers = [];
    let timer;
    const QUESTION_TIME = 30;

    function startTimer() {
        let timeLeft = QUESTION_TIME;
        $('#timer').text(`⏱ ${timeLeft}s`);
        timer = setInterval(() => {
            timeLeft--;
            $('#timer').text(`⏱ ${timeLeft}s`);
            if (timeLeft <= 0) {
                clearInterval(timer);
                submitAnswer(null);  // auto-submit unanswered
            }
        }, 1000);
    }

    function stopTimer() {
        clearInterval(timer);
        $('#timer').text('');
    }

    // ✅ Start button
    $('#start-btn').click(function () {
        const slug = $("#set-slug").val();

        $('#start-section').addClass('d-none');
        $('#quiz-area').removeClass('d-none');
        $('html, body').animate({ scrollTop: $('#quiz-area').offset().top }, 500);

        $.ajax({
            url: `/questions/init-attempt/${slug}/`,
            type: 'GET',
            success: function (data) {
                if (data.status === 'success') {
                    currentSetId = data.set_id;
                    currentAttemptId = data.attempt_id;

                    $('#start-btn').hide();
                    $('#quiz-area').removeClass('d-none');
                    loadNextQuestion();
                } else {
                    alert(data.message);
                }
            },
            error: function (xhr) {
                console.error("Assignment Error:", xhr.responseText || xhr.statusText);
                alert("Authentication failed or unauthorized access.");
            }
        });
    });

    // ✅ Load next question
    function loadNextQuestion() {
        $.ajax({
            url: '/questions/get-question/',
            type: 'GET',
            cache: false,
            data: { set_id: currentSetId, attempt_id: currentAttemptId },
            success: function (data) {
                if (data.status === 'completed') {
                    stopTimer();
                    showFinalResult();
                    return;
                }

                stopTimer();
                currentQuestionId = data.question_id;
                totalQuestions++;

                $('#question-box').html(`
                    <h5 class="text-white text-center mb-2">
                        Question ${totalQuestions}: ${data.text}
                    </h5>
                    <p class="text-warning">Difficulty: ${data.difficulty}</p>
                `);

                let optionsHtml = '';
                $.each(data.options, function (key, value) {
                    optionsHtml += `
                        <div class="form-check text-white text-start mx-auto" style="max-width: 600px;">
                            <input class="form-check-input" type="radio" name="option" value="${key}" id="opt${key}">
                            <label class="form-check-label" for="opt${key}">${key}: ${value}</label>
                        </div>`;
                });

                $('#options-box').html(optionsHtml);
                startTimer();
            },
            error: function (xhr) {
                console.error("Question Load Error:", xhr.responseText || xhr.statusText);
                alert("Failed to load question.");
            }
        });
    }

    // ✅ Submit answer
    $('#submit-btn').click(function () {
        const selectedOption = $('input[name="option"]:checked').val();
        if (!selectedOption) return alert("Please select an option!");
        submitAnswer(selectedOption);
    });

    function submitAnswer(selectedOption) {
        const csrfToken = $("input[name=csrfmiddlewaretoken]").val();

        $.ajax({
            url: '/questions/submit-answer/',
            type: 'POST',
            data: {
                question_id: currentQuestionId,
                selected_option: selectedOption || "",
                attempt_id: currentAttemptId,
                csrfmiddlewaretoken: csrfToken
            },
            success: function (data) {
                const correct = data.correct_option;
                const isCorrect = selectedOption === correct;
                score += isCorrect ? 1 : 0;

                userAnswers.push({
                    question: data.question,
                    selected: selectedOption,
                    correct: correct,
                    is_correct: isCorrect
                });

                loadNextQuestion();
            },
            error: function (xhr) {
                console.error("Submit error:", xhr.responseText || xhr.statusText);
                alert("Could not submit answer.");
            }
        });
    }

    // ✅ Final Result
    function showFinalResult() {
    $.get(`/questions/result/${currentAttemptId}/`, function (data) {
        // Calculate total wrong answers including unanswered ones
        const totalWrong = data.wrong + data.not_answered;

        // Aggregate wrong answers by subject
        const wrongBySubject = data.wrong_by_subject.map(subject => ({
            ...subject,
            totalWrongAnswers: subject.count  // Assuming 'count' is the number of wrong answers for that subject
        }));

        // Find the maximum wrong answer count across subjects
        const maxCount = Math.max(...wrongBySubject.map(subject => subject.totalWrongAnswers));

        // Filter subjects with the maximum wrong answer count
        const topSubjects = wrongBySubject.filter(subject => subject.totalWrongAnswers === maxCount);

        // Display quiz summary
        let html = `
            <div class="text-center text-white">
                <h4 class="text-success">✅ Test Completed!</h4>
                <p>Total Questions: ${data.total}</p>
                <p>Correct Answers: ${data.correct}</p>
                <p>Wrong Answers (including unanswered): ${totalWrong}</p>
                <p>Unanswered: ${data.not_answered}</p>
                <hr>
        `;

        // If multiple subjects have the same number of wrong answers, show plural "Subjects"
        if (topSubjects.length > 1) {
            html += `<h5>📊 Weakest Subjects (${maxCount} wrong answers):</h5>`;
            // Show all subjects with max wrong answers
            topSubjects.forEach(subject => {
                html += `<p>${subject.question__subject__name} (${subject.totalWrongAnswers} wrong)</p>`;
            });
        } else {
            // If only one subject has the highest wrong answers, show singular "Subject"
            html += `<h5>📊 Weakest Subject: ${topSubjects[0].question__subject__name} (${maxCount} wrong)</h5>`;
        }

        html += `<div id="book-area" class="mt-4"></div>`; // Book suggestions will go here
        html += `</div>`;
        $('#quiz-area').html(html);

        // Fetch book suggestions for each subject with max wrong answers
        topSubjects.forEach(subject => {
            const subjectName = subject.question__subject__name;
            $.get(`/questions/books/suggest/?subject=${encodeURIComponent(subjectName)}`, function(bookHtml) {
                const sectionHtml = `
                    <h6 class="mt-4">📚 Suggested Books for <strong>${subjectName}</strong></h6>
                    <div class="subject-book-table">${bookHtml}</div>
                `;
                $('#book-area').append(sectionHtml);
            });
        });
    });
}


});

