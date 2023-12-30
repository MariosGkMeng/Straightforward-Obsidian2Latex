

# Sample list of strings
list_of_strings = [
    "This is a single line.",
    "This string\nhas\nmultiple\nlines.",
    "Another single line here."
]

result_list = []

for string in list_of_strings:
    # Check if the string contains line breaks
    if "\n" in string:
        # Split the string into separate lines
        lines = string.split("\n")
        # Extend the result list with the separated lines
        result_list.extend(lines)
    else:
        # If no line break, add the string as it is
        result_list.append(string)

print(result_list)
