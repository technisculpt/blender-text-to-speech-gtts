def ensure_two_chars(number):
    string = str(number)

    if len(string) == 1:
        return '0' + string
    elif len(string) > 3:
        return string[0:3]
    else:
        return string