def strip_prefix(s):
    """
    Remove the given strings prefix

    Lots of our data is in the format:

        2. Foo

    This function removes the '2. ' part regardless of the length of the prefix
    prior to the period character.
    """
    _, _, suffix = s.partition(".")
    return suffix.strip()
