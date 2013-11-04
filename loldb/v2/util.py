import re


def alias(s):
    """
    Generate alias for s.

    Aliases contain only numbers, lowercase letters, and underscores.
    Any groups of invalid characters will be replaced by one underscore.

    """
    return re.sub('[^a-z0-9]+', '_', s.lower())
