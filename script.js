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

function checkPasswordStrength() {
    var password = document.getElementById("passwordInput").value
    if(password.length == 0){
        document.getElementById("password-strength-text").innerText = 'Please enter a password'
        return
    }
    var requestOptions = {
        method: 'GET',
        redirect: 'follow'
    };
    const url = "http://127.0.0.1:5000/give_password_score?password=" + encodeURIComponent(password);
    fetch(url, {
        method: 'GET'
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json(); // Parse response as JSON
        })
        .then(data => {
            console.log(data); // Log the response data to the console
            var dicAttInt = "Pass"
            var dicAttExt = "Pass"
            var numSeq = "Pass"
            var charSub = "Pass"
            var standardNum = "Pass"
            var finalScore = 0
            if(data.dict_atk_int_src != 1){
                dicAttInt = "Fail"
            }
            if(data.dict_atk_ext_src != 1){
                dicAttExt = "Fail"
            }
            if(data.num_seq_is_found != 1){
                numSeq = "Fail"
            }
            if(data.substitution_is_found != 1){
                charSub = "Fail"
            }
            if(data.standard_checks_is_pass != 1){
                standardNum = "Fail"
            }
            document.getElementById("dict_atk_int_src").innerText=dicAttInt
            document.getElementById("dict_atk_ext_src").innerText=dicAttExt
            document.getElementById("num_seq_is_found").innerText=numSeq
            document.getElementById("char_seq_strength").innerText=data.char_seq_strength
            document.getElementById("substitution_is_found").innerText=charSub
            document.getElementById("ml_password_classifer_score").innerText=data.ml_password_classifer_score
            document.getElementById("standard_checks_is_pass").innerText=standardNum
            document.getElementById("brute_force_timing").innerText=0
            
            finalScore = (document.getElementById("dicAttIntWeight").value*data.dict_atk_int_src) +
            (document.getElementById("dicAttExtWeight").value*data.dict_atk_ext_src) +
            (document.getElementById("numSeqWeight").value*data.num_seq_is_found) +
            (document.getElementById("charSeqWeight").value*data.char_seq_strength) +
            (document.getElementById("charSubWeight").value*data.substitution_is_found) +
            (document.getElementById("mlWeight").value*data.ml_password_classifer_score) +
            (document.getElementById("standardNumWeight").value*data.standard_checks_is_pass) +
            (document.getElementById("bruteForceWeight").value*0)
            document.getElementById("finalScore").innerText=finalScore

            if (finalScore > 0 && finalScore <= 0.2) {
                document.getElementById("password-strength-bg").className = "bg-danger p-1 text-center rounded"
                document.getElementById("password-strength-text").textContent = "Weak"
                document.getElementById("strength").className = "text-danger"
                document.getElementById("strength").innerText = "Weak"
            }
            else if (finalScore > 0.2 && finalScore <= 0.4) {
                document.getElementById("password-strength-bg").className = "bg-warning p-1 text-center rounded"
                document.getElementById("password-strength-text").textContent = "Medium"
                document.getElementById("strength").className = "text-warning"
                document.getElementById("strength").innerText = "Medium"
            }
            else if (finalScore > 0.4) {
                document.getElementById("password-strength-bg").className = "bg-success p-1 text-center rounded"
                document.getElementById("password-strength-text").textContent = "Strong"
                document.getElementById("strength").className = "text-success"
                document.getElementById("strength").innerText = "Strong"
            }
        })
        .catch(error => {
            console.error('There was a problem with the fetch operation:', error);
        });

        

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

function validateInput(input) {
    var value = parseFloat(input.value);
    if (value <= 0 || value > 1) {
        input.setCustomValidity('The number must be more than 0 and less than or equal to 1.');
    } else {
        input.setCustomValidity('');
    }
}

function setDefaultWeights() {
    var arr = [0, 0.1348961535622344, 0.01796824218137424, 0.761481294060113, 0.0768704525711875, 0.008783857625090846, 0, 0]
    var inputs = document.querySelectorAll('.strength-weightage-input');
    var i = 0
    inputs.forEach(function (input) {
        input.value = arr[i];
        input.setCustomValidity('');
        i++
    });
}

setDefaultWeights()
