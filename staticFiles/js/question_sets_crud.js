$(document).ready(function () {
    console.log("AJAX Script loaded");

    // Save/Edit Set
    $("#set_register_btn").click(function (event) {
        event.preventDefault();

        const set_id = $("#set_id").val();
        const set_name = $("#set_name").val();
        const category_id = $("#category").val();
        const csrfToken = $("input[name=csrfmiddlewaretoken]").val();

        if (!set_name || !category_id) {
            $("#acknowledge").text("Set name and category are required.")
                .css("color", "red").fadeIn().delay(2000).fadeOut();
            return;
        }

        $.ajax({
            url: set_id ? `/question_sets/edit/${set_id}/` : `/question_sets/add/`,
            method: "POST",
            data: {
                set_name: set_name,
                category: category_id,
                csrfmiddlewaretoken: csrfToken
            },
            success: function (response) {
                // Reset form
                $("#set_id").val("");
                $("#set_name").val("");
                $("#category").val("");
                $("h3.text-primary").text("Set Register");
                $("#set_register_btn").text("Save");

                $("#acknowledge").text(response.message || "Set saved successfully!")
                    .css("color", "green").fadeIn().delay(2000).fadeOut();

                // Reload set rows
                $.get("/question_sets/get_rows/", function (data) {
                    $("#setList").html(data.html);
                });
            },
            error: function (error) {
                const errorMessage = error.responseJSON?.message || "An error occurred.";
                $("#acknowledge").text(errorMessage)
                    .css("color", "red").fadeIn().delay(2000).fadeOut();
            }
        });
    });

    // Delete Set
    $(document).on("click", ".delete-set", function () {
        const setId = $(this).data("id");
        const csrfToken = $("input[name=csrfmiddlewaretoken]").val();

        if (!confirm("Are you sure?")) return;

        $.ajax({
            url: `/question_sets/delete/${setId}/`,
            method: "POST",
            data: { csrfmiddlewaretoken: csrfToken },
            success: function (response) {
                $("#acknowledge").text(response.message).css("color", "green").fadeIn().delay(2000).fadeOut();
                $.get("/question_sets/get_rows/", function (data) {
                    $("#setList").html(data.html);
                });
            },
            error: function (xhr) {
                $("#acknowledge").text(xhr.responseJSON?.message || "Failed").css("color", "red").fadeIn().delay(2000).fadeOut();
            }
        });
    });

    // Edit Set
    $(document).on("click", ".edit-set", function () {
        const setId = $(this).data("id");
        const setName = $(this).data("name");
        const categoryId = $(this).data("category");

        $("#set_id").val(setId);
        $("#set_name").val(setName);
        $("#category").val(categoryId);
        $("h3.text-primary").text("Edit Set");
        $("#set_register_btn").text("Update");
    });

    // Restore Set
    $(document).on("click", ".restore-set-btn", function () {
        const id = $(this).data("id");
        const csrfToken = $("input[name=csrfmiddlewaretoken]").val();

        $.ajax({
            url: `/question_sets/restore/${id}/`,
            type: "POST",
            data: { csrfmiddlewaretoken: csrfToken },
            success: function (response) {
                alert(response.message);
                location.reload();
            },
            error: function (xhr) {
                alert(xhr.responseJSON?.message || "Failed to restore set.");
            }
        });
    });
});
