import math

def crack_time(password):
    # Define character sets
    lowercase = "abcdefghijklmnopqrstuvwxyz"
    uppercase = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    digits = "0123456789"
    special_chars = "!@#$%^&*()-=_+[]{}|;:,.<>?/~`"
    
    # Calculate the size of character set
    charset_size = len(lowercase) + len(uppercase) + len(digits) + len(special_chars)
    
    # Estimate the entropy of the password
    entropy = math.log2(charset_size) * len(password)
    
    # Calculate the time to crack the password in seconds
    # Assuming 10^12 guesses per second (modern hardware), the actual time may vary
    # depending on various factors such as the attacker's resources and techniques.
    time_to_crack_seconds = (2 ** entropy) / (10 ** 12)
    
    # Convert seconds to more human-readable format
    time_to_crack = format_time(time_to_crack_seconds)
    
    return time_to_crack

def format_time(seconds):
    # Convert seconds to years, days, hours, minutes, and seconds
    years = int(seconds // (3600 * 24 * 365))
    seconds %= (3600 * 24 * 365)
    days = int(seconds // (3600 * 24))
    seconds %= (3600 * 24)
    hours = int(seconds // 3600)
    seconds %= 3600
    minutes = int(seconds // 60)
    seconds %= 60
    
    # Construct the formatted time string
    time_str = ""
    if years:
        time_str += f"{years} years "
    if days:
        time_str += f"{days} days "
    if hours:
        time_str += f"{hours} hours "
    if minutes:
        time_str += f"{minutes} minutes "
    if seconds:
        time_str += f"{round(seconds)} seconds"
    
    return time_str.strip()

def main():
    password = input("Enter your password: ")
    crack_time_str = crack_time(password)
    print(f"It would take approximately {crack_time_str} to crack your password.")

if __name__ == "__main__":
    main()
