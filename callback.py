"""A module for formatting callbacl data and queries."""

SEP = "$%^"


def form_callback_query(callback_name: str, data: str) -> str:
    """Formats data for the callback handler."""
    return SEP.join([callback_name, data])


def get_data(callback_query: str) -> str:
    """Gets data from a `callback_query` and returns it."""
    data = callback_query.split(SEP)
    return SEP.join(data[1:])
