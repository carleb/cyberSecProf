function updatePasswordInfo() {
    const input = document.getElementById("passwordInput");
    const password = input.value;
    document.getElementById("passwordLength").textContent = "Number of Characters: " + password.length;

    // Using Bootstrap's 'text-success' class
    document.getElementById("lowercase").classList.toggle("text-success", /[a-z]/.test(password));
    document.getElementById("uppercase").classList.toggle("text-success", /[A-Z]/.test(password));
    document.getElementById("numbers").classList.toggle("text-success", /[0-9]/.test(password));
    document.getElementById("symbols").classList.toggle("text-success", /[^A-Za-z0-9]/.test(password));
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

// Initial call to ensure dynamic updates from the start
updatePasswordInfo();

// Add an event listener for the input field to update info dynamically
document.getElementById("passwordInput").addEventListener("input", updatePasswordInfo);
