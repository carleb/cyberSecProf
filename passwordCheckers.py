import time
import hashlib

# Predefined dictionary file
dictionary_file = 'common_passwords.txt'

def crack_password(plaintext_password):
    solution = hashlib.md5(plaintext_password.encode()).hexdigest()
    print(f"MD5 Hash of the input password: {solution}")

    start = time.time()
    sol = "No solution found"
    
    try:
        with open(dictionary_file, 'r') as filename:
            for line in filename:
                line_hash = hashlib.md5(line.strip().encode()).hexdigest()
                if line_hash == solution:
                    sol = line.strip()
                    break
    except FileNotFoundError:
        print(f"Error: The file '{dictionary_file}' was not found.")
        return ("Error: Dictionary file not found.", 0)

    end = time.time()
    t_time = end - start
    
    if sol == "No solution found":
        estimated_time = brute_force_attack(len(plaintext_password))
        return (f"No solution found using dictionary attack. \nEstimated brute force cracking time: {estimated_time} seconds ", t_time)
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
    possible_characters = 26 + 26 + 10 + 32  # Assuming a combination of uppercase, lowercase letters, and digits
    total_combinations = possible_characters ** password_length
    estimated_seconds = total_combinations / attempts_per_second
    
    # Format the estimated time
    return format_time(estimated_seconds)

if __name__ == "__main__":
    plaintext_password = input("Enter the plaintext password to find the hash for: ")
    result, runtime = crack_password(plaintext_password)
    print(f"Total runtime was -- {runtime} seconds. Result: {result} \n")
