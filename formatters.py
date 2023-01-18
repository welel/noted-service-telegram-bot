"""Utils for formatting messages."""


def format_commit(commit: dict, nn: int = None) -> str:
    """Formats commit to html string message.

    Example of output:
        [<b>1.</b> ] fix: fixed bugs with icons.
        <b>SHA</b>: 57d968d84591e1514d8b40f326e934602df39133

    Attrs:
        commit: json form of a commit.
        nn: serial number of a commit (optional).
    Returns:
        Formatted string of a comment.
    """
    output = f"<b>{nn}</b>. " if nn else ""
    output += "{comment}\n<b>SHA</b>: {sha}".format(
        comment=commit["comment"], sha=commit["sha"]
    )
    return output
