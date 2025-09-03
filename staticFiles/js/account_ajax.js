
function validateRegistrationForm() {
    const username = $("#username").val()
    const email = $("#email").val()
    const password = $("#password").val();
    const confirmPassword = $("#confirm_password").val();

    let isValid = true;
    $(".text-danger").html(""); // clear errors

    const usernameRegex = /^[A-Za-z0-9_]{4,20}$/;
    const emailRegex = /^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$/;
    const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&]).{8,}$/;

    // Username
    if (!username) {
        $("#username_error").html("Username is required.");
        isValid = false;
    } else if (!usernameRegex.test(username)) {
        $("#username_error").html("4–20 chars, letters, numbers, underscores only.");
        isValid = false;
    }

    // Email
    if (!email) {
        $("#email_error").html("Email is required.");
        isValid = false;
    } else if (!emailRegex.test(email)) {
        $("#email_error").html("Invalid email format.");
        isValid = false;
    }

    // Password
    if (!password) {
        $("#password_error").html("Password is required.");
        isValid = false;
    } else if (!passwordRegex.test(password)) {
        $("#password_error").html("Must be 8+ chars, include upper, lower, number, special char.");
        isValid = false;
    }

    // Confirm Password
    if (!confirmPassword) {
        $("#confirm_password_error").html("Confirm your password.");
        isValid = false;
    } else if (password !== confirmPassword) {
        $("#confirm_password_error").html("Passwords do not match.");
        isValid = false;
    }

    $("#signup_btn").prop("disabled", !isValid);
    return isValid;
}

// Email uniqueness check
function validateEmailUniqueness(email, callback) {
    if (!email) return callback(false);
    $.ajax({
        url: "/account/check_email/",
        type: "POST",
        data: {
            email: email,
            csrfmiddlewaretoken: $("input[name=csrfmiddlewaretoken]").val()
        },
        success: function (res) {
            if (res.exists) {
                $("#email_error").html("Email already taken.");
                callback(false);
            } else {
                callback(true);
            }
        },
        error: function () {
            $("#email_error").html("Could not check email.");
            callback(false);
        }
    });
}

$(document).ready(function () {
    console.log("✅ Registration script loaded");

    $("#signup_btn").prop("disabled", true);

    // Live validation
    $("input").on("input blur", function () {
        validateRegistrationForm();
    });

    $("#signup_btn").click(function (e) {
        e.preventDefault();
        $("#acknowledge").html('');

        if (!validateRegistrationForm()) return;

        const formData = {
            username: $("#username").val().trim(),
            email: $("#email").val().trim(),
            password: $("#password").val(),
            confirm_password: $("#confirm_password").val(),
            role: $("#role").val(),
            csrfmiddlewaretoken: $("input[name=csrfmiddlewaretoken]").val()
        };

        // Check email uniqueness before submitting
        validateEmailUniqueness(formData.email, function (isAvailable) {
            if (!isAvailable) return;

            $.ajax({
                url: "/account/registration/",
                method: "POST",
                data: formData,
                beforeSend: function () {
                    $("#spinner-overlay").show();
                },
                success: function (response) {
                    $("#acknowledge").html(`<div class="alert alert-success">${response.message}</div>`).fadeIn().delay(5000).fadeOut();
                    if (response.redirect_url) {
                        setTimeout(() => {
                            window.location.href = response.redirect_url;
                        }, 3000);
                    }
                },
                error: function (xhr) {
                    const res = xhr.responseJSON;
                    if (res && res.errors) {
                        for (const field in res.errors) {
                            $(`#${field}_error`).html(`<div class="text-danger">${res.errors[field]}</div>`);
                        }
                    } else {
                        $("#acknowledge").html('<div class="alert alert-danger">Something went wrong!</div>');
                    }
                },
                complete: function () {
                    $("#spinner-overlay").hide();
                }
            });
        });
    });






    

    // ✅ Handle login with AJAX
    $("#login-btn").click(function (e) {
        e.preventDefault();

        const username = $("#username").val().trim();
        const password = $("#password").val().trim();
        const csrfToken = $("input[name=csrfmiddlewaretoken]").val();

        if (!username || !password) {
            alert("Please enter both username and password.");
            return;
        }

        $("#login-btn").prop("disabled", true);

        $.ajax({
            url: "/account/login_view/",
            method: "POST",
            data: {
                username: username,
                password: password,
                csrfmiddlewaretoken: csrfToken
            },
            success: function (response) {
                if (response.status === "success") {
                    window.location.href = response.redirect_url;
                } else {
                    alert("Login failed: " + response.message);
                    $("#login-btn").prop("disabled", false);
                }
            },
            error: function () {
                alert("Login failed due to server error.");
                $("#login-btn").prop("disabled", false);
            }
        });
    });

})


