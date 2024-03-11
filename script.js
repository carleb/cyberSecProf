function updatePasswordInfo() {
    const input = document.getElementById("passwordInput");
    const password = input.value;
    document.getElementById("passwordLength").textContent = "Number of Characters: " + password.length;

    document.getElementById("lowercase").classList.toggle("green", /[a-z]/.test(password));
    document.getElementById("uppercase").classList.toggle("green", /[A-Z]/.test(password));
    document.getElementById("numbers").classList.toggle("green", /[0-9]/.test(password));
    document.getElementById("symbols").classList.toggle("green", /[^A-Za-z0-9]/.test(password));
}

function togglePasswordVisibility() {
    const input = document.getElementById("passwordInput");
    const checkbox = document.getElementById("toggleView");
    if (checkbox.checked) {
        input.type = "text";
    } else {
        input.type = "password";
    }
}
