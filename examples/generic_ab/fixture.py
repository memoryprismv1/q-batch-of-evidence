def classify_count(value):
    # Zero represents an empty count.
    if value == 0:
        return "empty"
    # One is a distinct singleton case.
    if value == 1:
        return "single"
    # All remaining values are treated as multiple.
    return "multiple"
