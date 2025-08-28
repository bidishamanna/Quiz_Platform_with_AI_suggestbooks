// static/js/category.js
$(document).ready(function () {
    console.log("AJAX Script loaded");

    // Populate form for editing
    $(document).on("click", ".edit-btn", function () {
        const categoryId = $(this).data("id");
        const categoryName = $(this).data("name");

        $("#category_id").val(categoryId);
        $("#category_name").val(categoryName);
        $("h3.text-primary").text("Edit Category");
        $("#category_register_btn").text("Update");
    });

    // Create or Update category
    $("#category_register_btn").click(function (event) {
        event.preventDefault();

        const category_id = $("#category_id").val();
        const category_name = $("#category_name").val().trim();
        const csrfToken = $("input[name=csrfmiddlewaretoken]").val();

        if (!category_name) {
            $("#acknowledge").text("Category name cannot be empty.")
                .css("color", "red")
                .fadeIn().delay(2000).fadeOut();
            return;
        }

        $.ajax({
            url: category_id ? `/category/edit/${category_id}/` : `/category/add/`,
            method: "POST",
            data: {
                category_id: category_id,
                category_name: category_name,
                csrfmiddlewaretoken: csrfToken
            },
            success: function (response) {
                $("#category_id").val("");
                $("#category_name").val("");
                $("h3.text-primary").text("Category Register");
                $("#category_register_btn").text("Save");

                $("#acknowledge").text("Category saved successfully!")
                    .css("color", "green")
                    .fadeIn().delay(2000).fadeOut();

                $.get("/category/get_rows/", function (data) {
                    $("#categoryList").html(data.html);
                });
            },
            error: function (error) {
                const errorMessage = error.responseJSON?.message || "An error occurred.";
                $("#acknowledge").text(errorMessage)
                    .css("color", "red")
                    .fadeIn().delay(2000).fadeOut();
            }
        });
    });

    
    $(document).on("click", ".delete-btn", function () {
        const categoryId = $(this).data("id");
        const csrfToken = $("input[name=csrfmiddlewaretoken]").val();

        if (!confirm("AJAX: Are you sure you want to delete this category?")) return;

        $.ajax({
            url: `/category/delete/${categoryId}/`,
            method: "POST",
            data: {
                csrfmiddlewaretoken: csrfToken
            },
            success: function () {
                $("#acknowledge").text("Category deleted successfully!")
                    .css("color", "green")
                    .fadeIn().delay(2000).fadeOut();

                $.get("/category/get_rows/", function (data) {
                    $("#categoryList").html(data.html);
                });
            },
            error: function () {
                $("#acknowledge").text("Failed to delete the category.")
                    .css("color", "red")
                    .fadeIn().delay(2000).fadeOut();
            }
        });
    });


    $(document).on("click", ".restore-btn", function () {
    const id = $(this).data("id");
    const csrfToken = $("input[name=csrfmiddlewaretoken]").val();

    if (!confirm("Are you sure you want to restore this category?")) return;

    $.ajax({
        url: `/category/restore/${id}/`,
        method: "POST",
        data: {
            csrfmiddlewaretoken: csrfToken
        },
        success: function (response) {
                alert(response.message);
                location.reload();
            },
        
        error: function () {
            $("#acknowledge").text("Failed to restore the category.")
                .css("color", "red")
                .fadeIn().delay(2000).fadeOut();
        }
    });
});
})

