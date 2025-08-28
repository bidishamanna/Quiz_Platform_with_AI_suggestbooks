function validateRegistrationForm() {
    const firstNameField = document.getElementById('first_name');
    const lastNameField = document.getElementById('last_name');
    const usernameField = document.getElementById('username');
    const emailField = document.getElementById('email');
    const passwordField = document.getElementById('password');
    const confirmPasswordField = document.getElementById('confirm_password');
    const dobField = document.getElementById('dob');
    const genderFields = document.getElementsByName('gender');

    const firstNameError = document.getElementById('first_name_error');
    const lastNameError = document.getElementById('last_name_error');
    const usernameError = document.getElementById('username_error');
    const emailError = document.getElementById('email_error');
    const passwordError = document.getElementById('password_error');
    const confirmPasswordError = document.getElementById('confirm_password_error');
    const dobError = document.getElementById('dob_error');
    const genderError = document.getElementById('gender_error');

    const firstName = firstNameField.value.trim();
    const lastName = lastNameField.value.trim();
    const username = usernameField.value.trim();
    const email = emailField.value.trim();
    const password = passwordField.value;
    const confirmPassword = confirmPasswordField.value;
    const dob = dobField.value;

    let gender = "";
    for (const radio of genderFields) {
        if (radio.checked) {
            gender = radio.value;
            break;
        }
    }

    let isValid = true;

    // Clear errors
    firstNameError.innerHTML = '';
    lastNameError.innerHTML = '';
    usernameError.innerHTML = '';
    emailError.innerHTML = '';
    passwordError.innerHTML = '';
    confirmPasswordError.innerHTML = '';
    dobError.innerHTML = '';
    genderError.innerHTML = '';

    const nameRegex = /^[A-Za-z]{2,30}$/;
    const usernameRegex = /^[A-Za-z0-9_]{4,20}$/;
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&]).{8,}$/;

    const today = new Date();

    // First Name
    if (firstName === '') {
        firstNameError.innerHTML = `<div class="alert alert-danger">First name is required.</div>`;
        isValid = false;
    } else if (!nameRegex.test(firstName)) {
        firstNameError.innerHTML = `<div class="alert alert-danger">Only letters allowed (2–30 characters).</div>`;
        isValid = false;
    }

    // Last Name
    if (lastName === '') {
        lastNameError.innerHTML = `<div class="alert alert-danger">Last name is required.</div>`;
        isValid = false;
    } else if (!nameRegex.test(lastName)) {
        lastNameError.innerHTML = `<div class="alert alert-danger">Only letters allowed (2–30 characters).</div>`;
        isValid = false;
    }

    // Username
    if (username === '') {
        usernameError.innerHTML = `<div class="alert alert-danger">Username is required.</div>`;
        isValid = false;
    } else if (!usernameRegex.test(username)) {
        usernameError.innerHTML = `<div class="alert alert-danger">Use 4–20 characters: letters, numbers, underscores.</div>`;
        isValid = false;
    }

    // Email
    if (email === '') {
        emailError.innerHTML = `<div class="alert alert-danger">Email is required.</div>`;
        isValid = false;
    } else if (!emailRegex.test(email)) {
        emailError.innerHTML = `<div class="alert alert-danger">Invalid email format.</div>`;
        isValid = false;
    }

    // Password
    if (password === '') {
        passwordError.innerHTML = `<div class="alert alert-danger">Password is required.</div>`;
        isValid = false;
    } else if (!passwordRegex.test(password)) {
        passwordError.innerHTML = `<div class="alert alert-danger">Password must contain upper, lower, number, and special char.</div>`;
        isValid = false;
    }

    // Confirm Password
    if (confirmPassword === '') {
        confirmPasswordError.innerHTML = `<div class="alert alert-danger">Please confirm your password.</div>`;
        isValid = false;
    } else if (password !== confirmPassword) {
        confirmPasswordError.innerHTML = `<div class="alert alert-danger">Passwords do not match.</div>`;
        isValid = false;
    }

    // Gender
    if (!gender) {
        genderError.innerHTML = `<div class="alert alert-danger">Please select a gender.</div>`;
        isValid = false;
    }

    // DOB
    if (dob === '') {
        dobError.innerHTML = `<div class="alert alert-danger">Date of birth is required.</div>`;
        isValid = false;
    } else {
        const dobDate = new Date(dob);
        if (dobDate > today) {
            dobError.innerHTML = `<div class="alert alert-danger">DOB cannot be in the future.</div>`;
            isValid = false;
        } else {
            const age = today.getFullYear() - dobDate.getFullYear();
            const m = today.getMonth() - dobDate.getMonth();
            const actualAge = m > 0 || (m === 0 && today.getDate() >= dobDate.getDate()) ? age : age - 1;
            if (actualAge < 10) {
                dobError.innerHTML = `<div class="alert alert-danger">You must be at least 10 years old.</div>`;
                isValid = false;
            }
        }
    }

    // Enable/Disable register button
    document.getElementById('signup_btn').disabled = !isValid;
    return isValid;
}
