import time
import hashlib
import json
import pandas as pd
import string
import lightgbm as lgb
import numpy as np


# Load substitutions dictionary from JSON file
substitutions_dict_path = "substitutions_dict.json"  # Update this path if necessary
with open(substitutions_dict_path, "r") as file:
    substitutions_dict = json.load(file)

# Predefined dictionary file
dictionary_file = "common_passwords.txt"


def predict_with_model(password):
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
    bst = lgb.Booster(model_file="lgb_model_password_classifier.txt")

    # Predict
    y_pred = bst.predict(features)
    return np.argmax(y_pred)


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


def crack_password(plaintext_password):
    sequence_removed_password, sequence_removed = remove_numeric_sequences(
        plaintext_password
    )
    final_password, substitution_made = generate_substitutions(
        sequence_removed_password
    )

    solution = hashlib.md5(final_password.encode()).hexdigest()
    print(f"MD5 Hash of the final processed password: {solution}")

    start = time.time()
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

    end = time.time()
    t_time = end - start

    if sol == "No solution found":
        estimated_time = brute_force_attack(len(final_password))
        result_msg = (
            f"No solution found using {method_str}. Estimated brute force cracking time: {estimated_time}",
            t_time,
        )
    else:
        result_msg = (f"Password found through {method_str}: {sol}", t_time)

    return result_msg


def format_time(seconds):
    """
    Converts seconds into years, months, days, hours, minutes, and seconds with appropriate formatting.
    """
    # Constants for time conversion
    seconds_in_a_minute = 60
    seconds_in_an_hour = 3600
    seconds_in_a_day = 86400
    seconds_in_a_month = 30 * seconds_in_a_day  # Approximation
    seconds_in_a_year = 365.25 * seconds_in_a_day  # Accounting for leap year

    # Calculate each time component
    years = seconds // seconds_in_a_year
    seconds %= seconds_in_a_year
    months = seconds // seconds_in_a_month
    seconds %= seconds_in_a_month
    days = seconds // seconds_in_a_day
    seconds %= seconds_in_a_day
    hours = seconds // seconds_in_an_hour
    seconds %= seconds_in_an_hour
    minutes = seconds // seconds_in_a_minute
    seconds %= seconds_in_a_minute

    # Return formatted string
    return f"{years:.0f} year(s), {months:.0f} month(s), {days:.0f} day(s), {hours:.0f} hour(s), {minutes:.0f} minute(s), {seconds:.2f} second(s)"


def brute_force_attack(password_length):
    """
    Estimates the time required for a brute force attack based on password length.
    """
    attempts_per_second = 1e11
    possible_characters = (
        26 + 26 + 10 + 32
    )  # Assuming a combination of uppercase, lowercase letters, and digits
    total_combinations = possible_characters**password_length
    estimated_seconds = total_combinations / attempts_per_second

    # Format the estimated time
    return format_time(estimated_seconds)


if __name__ == "__main__":
    plaintext_password = input("Enter the plaintext password to find the hash for: ")
    result, runtime = crack_password(plaintext_password)
    print(f"Total runtime was -- {runtime} seconds. \nResult: {result} \n")

    print("Running model through ML Password Strength Classifier")
    model_prediction_strenghts = {0: "Weak", 1: "Normal", 2: "Strong"}

    mlResult = predict_with_model(plaintext_password)
    print("Result:", model_prediction_strenghts[mlResult])
