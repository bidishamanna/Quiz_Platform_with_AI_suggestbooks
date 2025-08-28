$(document).ready(function () {
    console.log("📘 Question JS Loaded");

    // 🔁 When category changes
    $("#category").off("change").on("change", function () {
        const categoryId = $(this).val();

        // Load subjects
        $("#subject").html('<option value="">Loading...</option>');
        if (!categoryId) {
            $("#subject").html('<option value="">-- Select Subject --</option>');
        } else {
            $.get(`/questions/get_subjects/${categoryId}/`, function (data) {
                let options = '<option value="">-- Select Subject --</option>';
                data.subjects.forEach(subject => {
                    options += `<option value="${subject.id}">${subject.name}</option>`;
                });
                $("#subject").html(options);
            });
        }

        // Load sets for this category
        $("#set").html('<option value="">Loading...</option>');
        if (!categoryId) {
            $("#set").html('<option value="">-- Select Set --</option>');
        } else {
            $.get(`/questions/get_sets/${categoryId}/`, function (data) {
                let options = '<option value="">-- Select Set --</option>';
                data.sets.forEach(set => {
                    options += `<option value="${set.id}">${set.name}</option>`;
                });
                $("#set").html(options);
            });
        }
    });

    // 🔁 Submit Question Form (Add/Edit)
    $("#add-question-form").submit(function (e) {
        e.preventDefault();
        const formData = $(this).serialize();
        const questionId = $("#question_id").val();
        const url = questionId ? `/questions/edit/${questionId}/` : `/questions/add/`;

        $.ajax({
            type: "POST",
            url: url,
            data: formData,
            success: function (response) {
                $("#acknowledge").text(response.message)
                    .css("color", "green").fadeIn().delay(2000).fadeOut();

                // Reset form
                $("#add-question-form")[0].reset();
                $("#question_id").val("");
                $("#add-question-btn").text("Add Question");

                // Refresh table
                $.get("/questions/get_rows/", function(response) {
                    $("#question-table-body").html(response.html);
                });

                $(".text-danger").html(""); // Clear errors
            },
            error: function (xhr) {
                const errors = xhr.responseJSON || {};
                $(".text-danger").html("");
                for (const field in errors) {
                    $(`#error-${field}`).html(errors[field]);
                }
            }
        });
    });

    // 🔄 Delete Question
    $(document).on("click", ".delete-question", function () {
        const questionId = $(this).data("id");
        const csrfToken = $("input[name=csrfmiddlewaretoken]").val();

        if (!confirm("Are you sure you want to delete this question?")) return;

        $.ajax({
            url: `/questions/delete/${questionId}/`,
            method: "POST",
            data: { csrfmiddlewaretoken: csrfToken },
            success: function (response) {
                $("#acknowledge").text(response.message || "Question deleted successfully!")
                    .css("color", "green").fadeIn().delay(2000).fadeOut();

                $.get("/questions/get_rows/", function(response) {
                    $("#question-table-body").html(response.html);
                });
            },
            error: function (xhr) {
                $("#acknowledge").text(xhr.responseJSON?.message || "Failed to delete the question.")
                    .css("color", "red").fadeIn().delay(2000).fadeOut();
            }
        });
    });

    // 🔄 Edit Question
    $(document).on("click", ".edit-question", function () {
        const questionId = $(this).data("id");
        const questionText = $(this).data("question");
        const categoryId = $(this).data("category");
        const subjectId = $(this).data("subject");
        const setId = $(this).data("set");
        const optionA = $(this).data("a");
        const optionB = $(this).data("b");
        const optionC = $(this).data("c");
        const optionD = $(this).data("d");
        const correct = $(this).data("correct");
        const difficulty = $(this).data("difficulty");

        // Populate form
        $("#question_id").val(questionId);
        $("#question_text").val(questionText);
        $("#option_a").val(optionA);
        $("#option_b").val(optionB);
        $("#option_c").val(optionC);
        $("#option_d").val(optionD);
        $("#correct_option").val(correct);
        $("#difficulty_score").val(difficulty);
        $("#category").val(categoryId);
        $("#add-question-btn").text("Update Question");

        // Fetch Subjects
        $.get(`/questions/get_subjects/${categoryId}/`, function (data) {
            let subjectOptions = '<option value="">-- Select Subject --</option>';
            data.subjects.forEach(subject => {
                subjectOptions += `<option value="${subject.id}" ${subject.id == subjectId ? "selected" : ""}>${subject.name}</option>`;
            });
            $("#subject").html(subjectOptions);
        });

        // Fetch Sets
        $.get(`/questions/get_sets/${categoryId}/`, function (data2) {
            let setOptions = '<option value="">-- Select Set --</option>';
            data2.sets.forEach(set => {
                setOptions += `<option value="${set.id}" ${set.id == setId ? "selected" : ""}>${set.name}</option>`;
            });
            $("#set").html(setOptions);
        });
    });

    // 🔁 Restore Question
    $(document).on("click", ".restore-question-btn", function () {
        const id = $(this).data("id");
        const csrfToken = $("input[name=csrfmiddlewaretoken]").val();

        $.ajax({
            url: `/questions/restore/${id}/`,
            type: "POST",
            headers: { "X-CSRFToken": csrfToken },
            success: function (response) {
                alert(response.message);
                location.reload();
            },
            error: function (xhr) {
                alert(xhr.responseJSON?.message || "Failed to restore question.");
            }
        });
    });
    
    // 🔄 Submit CSV Question Upload Form
    $("#upload-question-form").submit(function (e) {
        e.preventDefault();

        let formData = new FormData(this);
        const questionId = $("#question_id").val();
        const url = questionId ? `/questions/edit/${questionId}/` : `/questions/upload-questions/`;

        $.ajax({
            type: "POST",
            url: url,
            data: formData,
            processData: false,
            contentType: false,
            success: function (response) {
                $("#acknowledge").text(response.message)
                    .css("color", "green").fadeIn().delay(2000).fadeOut();

                $("#upload-question-form")[0].reset();
                $("#question_id").val("");

                $("#question-table-body").html(response.html);

                $(".error-message").empty();
            },
            error: function (xhr) {
                const errors = xhr.responseJSON || {};
                $(".error-message").empty();
                for (const field in errors) {
                    $(`#error-${field}`).html(errors[field]);
                }
            }
        });
    });

});
