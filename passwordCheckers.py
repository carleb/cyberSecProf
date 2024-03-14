import time
import hashlib
import requests
from password_strength import PasswordPolicy
from password_strength import PasswordStats
# Predefined dictionary file
dictionary_file = "common_passwords.txt"


def crack_password(plaintext_password):
    solution = hashlib.md5(plaintext_password.encode()).hexdigest()
    print(f"MD5 Hash of the input password: {solution}")

    start = time.time()
    sol = "No solution found"

    try:
        with open(dictionary_file, "r") as filename:
            for line in filename:
                line_hash = hashlib.md5(line.strip().encode()).hexdigest()
                if line_hash == solution:
                    sol = line.strip()
                    print("Password found with dictionary")
                    break
    except FileNotFoundError:
        print(f"Error: The file '{dictionary_file}' was not found.")
        return ("Error: Dictionary file not found.", 0)

    end = time.time()
    t_time = end - start

    if sol == "No solution found":
        estimated_time = brute_force_attack(len(plaintext_password))
        return (
            f"No solution found using dictionary attack. \nEstimated brute force cracking time: {estimated_time} seconds ",
            t_time,
        )
    else:
        return (sol, t_time)


def format_time(seconds):
    """
    Converts seconds into years, months, days, hours, minutes, and seconds with appropriate formatting.

    Parameters:
        seconds (float): Total time in seconds to be converted.

    Returns:
        str: A string representing the formatted time.
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
    attempts_per_second = 1e11
    possible_characters = (
        26 + 26 + 10 + 32
    )  # Assuming a combination of uppercase, lowercase letters, and digits
    total_combinations = possible_characters**password_length
    estimated_seconds = total_combinations / attempts_per_second

    # Format the estimated time
    return format_time(estimated_seconds)

def check_password_security(plaintext_password):
    # Hash the plaintext password using SHA-1
    hashed_password = hashlib.sha1(plaintext_password.encode()).hexdigest().upper()
    first_five_chars = hashed_password[:5]
    rest_of_hash = hashed_password[5:]
    # Make GET request to the Pwned Passwords API
    api_url = f"https://api.pwnedpasswords.com/range/{first_five_chars}"
    response = requests.get(api_url)

    # Check if the request was successful
    if response.status_code == 200:
        # Extract the list of hashes returned from the API response
        hashes = response.text.splitlines()

        # Search for the full SHA-1 hash in the list
        for item in hashes:
            if rest_of_hash in item:
                return "Password has been breached before. It has been found in the Pwned Passwords database."
        
        # If the password hash is not found in the list, it's considered safe
        return "Password is safe based on all known SHA-1 hashed breaches"
    else:
        # If the request fails, return an error message
        return f"Error: Failed to fetch data from the Pwned Passwords API. Status code: {response.status_code}"

def check_password_policy_compliance(password):
    # Define password policy criteria
    min_length = 8
    requires_uppercase = True
    requires_lowercase = True
    requires_digit = True
    requires_special = True
    disallowed_phrases = ["passw0rd","password", "123456", "qwerty", "p@ssw0rd","p@55w0rd","P@ssw0rd123"]

    if any(phrase.lower() in password.lower() for phrase in disallowed_phrases):
        return "Weak", "Password contains common password phrases"
    if len(password) >= min_length and any(char.isupper() for char in password) and any(char.isdigit() for char in password) and any(char in "!@#$%^&*()-_=+[{]}\\|;:'\",<.>/?`~" for char in password):
        return "Strong", "Password meets the required policy"
    if len(password) >= min_length and any(char.isupper() for char in password) and any(char.isdigit() for char in password) and not any(char in "!@#$%^&*()-_=+[{]}\\|;:'\",<.>/?`~" for char in password):
        return "Moderate", "Password does not contain any special characters"
    if len(password) >= min_length and not any(char.isupper() for char in password) and any(char.isdigit() for char in password) and not any(char in "!@#$%^&*()-_=+[{]}\\|;:'\",<.>/?`~" for char in password):
        return "Moderate", "Password does not contain any special characters and uppercase characters"
    if len(password) >= min_length and any(char.isupper() for char in password) and not any(char.isdigit() for char in password) and any(char in "!@#$%^&*()-_=+[{]}\\|;:'\",<.>/?`~" for char in password):
        return "Moderate", "Password does not contain any digits"
    if len(password) >= min_length and not any(char.isupper() for char in password) and any(char.isdigit() for char in password) and any(char in "!@#$%^&*()-_=+[{]}\\|;:'\",<.>/?`~" for char in password):
        return "Moderate", "Password does not contain any uppercase characters"
    if len(password) <=min_length:
        return "Weak", "Password is too short"



if __name__ == "__main__":
    def check_password_until_strong(password):
        policy_message, reason = check_password_policy_compliance(password)
        if policy_message == "Strong":
            return policy_message, reason
        else:
            print(f"Password is {policy_message}\nReason: {reason}\n")
            new_password = input("Enter new password: ")
            return check_password_until_strong(new_password)
    

    plaintext_password = input("Enter the plaintext password to find the hash for: ")

    stats = PasswordStats(plaintext_password)
    sequence = stats.sequences_length
    strength = stats.strength(weak_bits = 30)
    weakness_factor = stats.weakness_factor
    password_strength = (1 - weakness_factor) * strength
    print(sequence)
    print(strength)
    print(weakness_factor)
    print(password_strength)
    # policy_message, reason = check_password_until_strong(plaintext_password)
    # print(f"Password is {policy_message}\nReason: {reason}\n")
    # print("Based on given password the following result is assumed:")
    # resultpwned = check_password_security(plaintext_password)
    # result, runtime = crack_password(plaintext_password)
    # print(f"Total runtime was -- {runtime} seconds. Result: {result} \n")
    # print(resultpwned)
