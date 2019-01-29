def normalise_justification_name(some_name):
    """
    Produce a stable string for each LegalJustification name during ingestion

    LegalJustification names are in the format:

        TYPE: Some string

    However the number of spaces after the colon and the capitalisation of
    "Some string" aren't consistent.  This function normalises those so they're
    always the same.
    """
    prefix, _, suffix = some_name.partition(":")

    if not suffix:
        # some_name didn't contain a ":"
        return prefix

    prefix = prefix.strip().capitalize()
    suffix = suffix.strip()
    return f"{prefix}: {suffix}"


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
