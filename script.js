function updatePasswordInfo() {
    const input = document.getElementById("passwordInput");
    const password = input.value;
    document.getElementById("passwordLength").textContent = "Number of Characters: " + password.length;
    crackPasswordTiming(password)
    // Using Bootstrap's 'text-success' class
    document.getElementById("lowercase").classList.toggle("text-success", /[a-z]/.test(password));
    document.getElementById("uppercase").classList.toggle("text-success", /[A-Z]/.test(password));
    document.getElementById("numbers").classList.toggle("text-success", /[0-9]/.test(password));
    document.getElementById("symbols").classList.toggle("text-success", /[^A-Za-z0-9]/.test(password));
}

function crackPasswordTiming(passwordInput){
    num = Number(document.getElementById("years").textContent);
    num += 1000;
    document.getElementById("years").textContent = num;

    //Change password bg
    if(num > 2000 && num <= 5000){
        document.getElementById("password-strength-bg").className ="bg-danger p-1 text-center rounded"
        document.getElementById("password-strength-text").textContent = "Very Weak"
    }
    else if(num > 5000 && num <= 10000){
        document.getElementById("password-strength-bg").className ="bg-warning p-1 text-center rounded"
        document.getElementById("password-strength-text").textContent = "Medium"
    }
    else if(num > 10000){
        document.getElementById("password-strength-bg").className ="bg-success p-1 text-center rounded"
        document.getElementById("password-strength-text").textContent = "Strong"
    }
     
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
