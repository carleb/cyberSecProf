from flask import Flask, jsonify, request, render_template_string
from flask_cors import CORS
import pandas as pd
import hashlib
import requests
import json
import string
import numpy as np
import lightgbm as lgb
from password_strength import PasswordStats

app = Flask(__name__)
CORS(app)
# helper functions
substitutions_dict_path = "substitutions_dict.json"  # Update this path if necessary
with open(substitutions_dict_path, "r") as file:
    substitutions_dict = json.load(file)

# Predefined dictionary file
dictionary_file = "common_passwords.txt"


def dict_atk_ext_src(plaintext_password):
    hashed_password = hashlib.sha1(plaintext_password.encode()).hexdigest().upper()
    first_five_chars = hashed_password[:5]
    rest_of_hash = hashed_password[5:]
    api_url = f"https://api.pwnedpasswords.com/range/{first_five_chars}"
    response = requests.get(api_url)
    if response.status_code == 200:
        hashes = (line.split(":") for line in response.text.splitlines())
        for h, count in hashes:
            if h == rest_of_hash:
                return 0  # Breached
        return 1  # Not breached
    return 0  # Default to breached if API call fails


def standard_checks_is_pass(password):
    # Simplified standard checks. Returns 1 if password passes, 0 otherwise
    if (
        len(password) >= 8
        and any(char.isdigit() for char in password)
        and any(char.isupper() for char in password)
    ):
        return 1
    return 0


def generate_substitutions(plaintext):
    """
    Generate possible substitutions for the given plaintext, replacing common substituted characters
    with their alphabetical representation.
    """
    chars = list(plaintext)
    modified = False
    for i, char in enumerate(chars):
        if char in substitutions_dict:
            chars[i] = substitutions_dict[char]
            modified = True
    return "".join(chars), modified


def remove_numeric_sequences(password):
    """
    Remove sequences of three or more sequential numbers from the password.
    Returns the modified password and a flag indicating if any sequence was removed.
    """

    def is_sequential(s):
        ascending = all(
            ord(next_char) == ord(current_char) + 1
            for current_char, next_char in zip(s, s[1:])
        )
        descending = all(
            ord(next_char) == ord(current_char) - 1
            for current_char, next_char in zip(s, s[1:])
        )
        return ascending or descending

    new_password = ""
    numeric_sequence = ""
    modified = False
    for char in password:
        if char.isdigit():
            numeric_sequence += char
        else:
            if is_sequential(numeric_sequence) and len(numeric_sequence) >= 3:
                modified = True  # Indicate removal without keeping the first digit
                numeric_sequence = ""  # Reset sequence
            new_password += numeric_sequence + char
            numeric_sequence = ""
    if is_sequential(numeric_sequence) and len(numeric_sequence) >= 3:
        modified = True
    else:
        new_password += (
            numeric_sequence  # Add any remaining sequence not identified as sequential
        )
    return new_password, modified


def dict_atk_int_src(plaintext_password):
    sequence_removed_password, sequence_removed = remove_numeric_sequences(
        plaintext_password
    )
    final_password, substitution_made = generate_substitutions(
        sequence_removed_password
    )

    solution = hashlib.md5(final_password.encode()).hexdigest()

    sol = "No solution found"
    methods_used = []

    if sequence_removed:
        methods_used.append("numeric sequence removal")
    if substitution_made:
        methods_used.append("character substitution")
    methods_used.append("dictionary")  # Ensure dictionary check is always mentioned

    method_str = ", ".join(methods_used) if methods_used else "direct check"

    try:
        with open(dictionary_file, "r") as filename:
            for line in filename:
                line = line.strip()
                if hashlib.md5(line.encode()).hexdigest() == solution:
                    sol = line
                    break  # Found a match
    except FileNotFoundError:
        print(f"Error: The file '{dictionary_file}' was not found.")
        return "Error: Dictionary file not found.", 0

    if sol == "No solution found":
        return 1  # non found
    else:
        return 0


def is_sequential(s):
    if len(s) < 3:
        return False
    ascending = all(
        ord(next_char) == ord(current_char) + 1
        for current_char, next_char in zip(s, s[1:])
    )
    descending = all(
        ord(next_char) == ord(current_char) - 1
        for current_char, next_char in zip(s, s[1:])
    )
    return ascending or descending


def num_seq_is_found(password):
    numeric_sequence = ""
    for char in password:
        if char.isdigit():
            numeric_sequence += char
            if is_sequential(numeric_sequence) and len(numeric_sequence) >= 3:
                return 0  # Found a sequential numeric sequence
        else:
            if is_sequential(numeric_sequence) and len(numeric_sequence) >= 3:
                return 0  # Found a sequential numeric sequence
            numeric_sequence = ""  # Reset sequence because current char is not a digit
    # Check the last sequence if the password ends with a numeric sequence
    if is_sequential(numeric_sequence) and len(numeric_sequence) >= 3:
        return 0
    return 1  #  sequential numeric sequence found


def substitution_is_found(
    plaintext_password,
):  # Returns 0 if a substitution has been made
    # First, remove numeric sequences from the password
    sequence_removed_password, sequence_removed = remove_numeric_sequences(
        plaintext_password
    )
    # Then, try to generate substitutions
    final_password, substitution_made = generate_substitutions(
        sequence_removed_password
    )

    # Return 0 if a substitution has been made, 1 otherwise
    return 0 if substitution_made else 1


def char_seq_strength(plaintext_password):
    stats = PasswordStats(plaintext_password)
    sequence = stats.sequences_length
    strength = stats.strength(weak_bits=30)
    weakness_factor = stats.weakness_factor
    password_strength = (1 - weakness_factor) * strength

    return password_strength


def ml_password_classifier_score(password):
    """
    Machine Learning Based Password Strength Classifier.
    Accepts a single password string as input.
    """

    # Feature engineering setup
    punctuation = list(string.punctuation)

    # Wrap the input password in a DataFrame
    X_new = pd.DataFrame([password], columns=["password"])

    # Apply feature engineering
    X_new["length"] = X_new["password"].apply(len)
    X_new["has_num"] = X_new["password"].apply(
        lambda x: any(char.isdigit() for char in x)
    )
    X_new["num_cnt"] = X_new["password"].apply(lambda x: sum(c.isdigit() for c in x))
    X_new["has_lower"] = X_new["password"].apply(
        lambda x: any(char.islower() for char in x)
    )
    X_new["lower_cnt"] = X_new["password"].apply(lambda x: sum(c.islower() for c in x))
    X_new["has_upper"] = X_new["password"].apply(
        lambda x: any(char.isupper() for char in x)
    )
    X_new["upper_cnt"] = X_new["password"].apply(lambda x: sum(c.isupper() for c in x))
    X_new["has_special"] = X_new["password"].apply(
        lambda x: any(char in punctuation for char in x)
    )
    X_new["special_cnt"] = X_new["password"].apply(
        lambda x: sum(char in punctuation for char in x)
    )

    # Prepare features for prediction
    features = X_new.drop(columns=["password"])

    # Load the model
    # bst = lgb.Booster(model_file="lgb_model_password_classifier.txt")
    bst = lgb.Booster(model_file="lgb_model_password_classifier.lgb")

    # Predict
    y_pred = bst.predict(features)
    return np.argmax(y_pred)


def estimate_brute_force_time(password):
    """
    Estimates the time required for a brute force attack to crack the given password, returning the time in hours.
    """
    password_length = len(password)
    attempts_per_second = 1e11  # Assumption based on computational capability
    possible_characters = (
        26 + 26 + 10 + 32
    )  # Uppercase, lowercase, digits, and 32 symbols
    total_combinations = possible_characters**password_length
    estimated_seconds = total_combinations / attempts_per_second

    # Convert estimated time from seconds to hours
    estimated_hours = estimated_seconds / 3600
    return estimated_hours


@app.route("/")
def home():
    return render_template_string(open("index.html").read())


@app.route("/give_password_score", methods=["GET"])
def give_password_score():
    # Extract the password from query parameters of the GET request
    password = str(request.args.get("password"))

    # Calculate the scores, ensuring they are Python integers for JSON serialization compatibility
    res = {
        "dict_atk_ext_src": int(dict_atk_ext_src(password)),  # Convert to Python int
        "dict_atk_int_src": int(dict_atk_int_src(password)),  # Convert to Python int
        "num_seq_is_found": int(num_seq_is_found(password)),  # Convert to Python int
        "substitution_is_found": int(
            substitution_is_found(password)
        ),  # Convert to Python int
        "char_seq_strength": round(
            char_seq_strength(password), 2
        ),  # Convert to Python int
        "ml_password_classifer_score": int(
            ml_password_classifier_score(password)
        ),  # Convert to Python int
        "standard_checks_is_pass": int(
            standard_checks_is_pass(password)
        ),  # Convert to Python int
        "estimate_brute_force_time_hours": round(
            estimate_brute_force_time(password), 3
        ),  # Convert to Python int
    }

    # Print the dictionary for debugging (optional)
    print(res)

    # Return the dictionary serialized to JSON
    return jsonify(res)


print(substitution_is_found("password123"))


@app.route("/password_strength", methods=["GET"])
def get_password_strength():
    plaintext_password = request.args.get("password")

    if not plaintext_password:
        return jsonify({"error": "No password provided"}), 400

    stats = PasswordStats(plaintext_password)
    strength = stats.strength(weak_bits=30)
    weakness_factor = stats.weakness_factor
    password_strength = int(
        (1 - weakness_factor) * strength * 100
    )  # Convert to integer percentage

    return jsonify({"password_strength": password_strength})


if __name__ == "__main__":
    app.run(debug=True)
