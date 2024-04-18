import requests
import re

def extract_numbers_from_substrings(input_string):
    pattern = r'index\.php\?[\w|\=|&|;]+'  # Define the pattern for substrings
    substrings = re.findall(pattern, input_string)
    numbers = []

    for substring in substrings:
        number = extract_number_from_end(substring)
        if number is not None:
            numbers.append(url+number)

    return numbers

def extract_number_from_end(input_string):
    pattern = r'\d+$'  # Match one or more digits at the end of the string
    match = re.search(pattern, input_string)
    if match:
        return match.group()  # Extract the matched number
    else:
        return None  # Return None if no number is found

def find_occurrences(input_string):
    pattern = r'index\.php\?[\w|\=|&|;]+'
    occurrences = re.findall(pattern, input_string)
    return occurrences

data = str(requests.get("https://hypnohub.net/index.php?page=favorites&s=view&id=16732").content)
url = "https://hypnohub.net/index.php?page=post&s=view&id="

numbers = extract_numbers_from_substrings(data)
print("Numbers extracted:", numbers)

# https://hypnohub.net/index.php?page=post&s=view&id=137445
# https://hypnohub.net/index.php?page=post&amp;s=view&amp;id=137309
