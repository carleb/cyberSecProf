def substitution_is_found(plaintext_password): #0 if found
    # First, remove numeric sequences from the password
    sequence_removed_password, sequence_removed = remove_numeric_sequences(plaintext_password)
    # Then, try to generate substitutions
    final_password, substitution_made = generate_substitutions(sequence_removed_password)

    # Calculate the MD5 hash of the final processed password
    solution = hashlib.md5(final_password.encode()).hexdigest()
    # print(final_password)
    # Attempt to find the password in the dictionary
    try:
        with open(dictionary_file, "r") as filename:
            for line in filename:
                line = line.strip()
                if hashlib.md5(line.encode()).hexdigest() == solution:
                    # Password found in dictionary after modifications
                    return 0
    except FileNotFoundError:
        print(f"Error: The file '{dictionary_file}' was not found.")
        # If the dictionary file is missing, treat it as if the password couldn't be cracked
        return 1