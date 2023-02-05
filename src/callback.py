"""A module for formatting callback data and queries."""

SEP = "$%^"


def form_callback_query(callback_name: str, data: str) -> str:
    """Formats data for use in a callback button.

    Args:
        callback_name: The name of the callback to be used.
        data: The data to be passed to the callback.

    Returns:
        str: A string formatted for use in a callback button.
    """
    return SEP.join([callback_name, data])


def get_data(callback_query: str) -> str:
    """Gets data from a `callback_query` and returns it.

    Args:
        callback_query: A string representing a callback query.

    Returns:
        str: The data associated with the callback query.
    """
    data = callback_query.split(SEP)
    return SEP.join(data[1:])
