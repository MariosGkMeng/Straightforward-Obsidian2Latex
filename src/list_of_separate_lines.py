
def get_list_of_separate_string_lines(S):

    result_list = []

    for string in S:
        # Check if the string contains line breaks
        if "\n" in string:
            # Split the string into separate lines
            lines = string.split("\n")
            # Extend the result list with the separated lines
            result_list.extend(lines)
        else:
            # If no line break, add the string as it is
            result_list.append(string)

    return result_list
