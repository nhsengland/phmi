def strip_prefix(s):
    """
    Remove the given strings prefix

    Lots of our data is in the format:

        2. Foo

    This function removes the '2. ' part regardless of the length of the prefix
    prior to the period character.
    """
    separator = "."

    if separator not in s:
        return s

    _, _, suffix = s.partition(separator)
    return suffix.strip()
