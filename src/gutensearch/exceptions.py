"""
Custom exceptions for gutensearch.
"""


class HandledFatalException(Exception):
    """Raise when user wants to terminate rather than do something."""
    pass


class FrequenciesNotCachedError(Exception):
    """Raise when a new book is requested for which frequencies have not been stored."""
    pass


class TxtNotExistError(Exception):
    """Raise when the book url does not exist."""
    pass
