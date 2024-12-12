# TODO: Move generic utils that are not related to fastapi batteries to a separate package "pytils-jd"
def page_size_to_offset_limit(page: int, size: int):
    """Convert page and size to offset and limit.

    This is useful to convert page and size to offset and limit for SQL queries.

    Args:
        page: Page number.
        size: Page size.

    Returns:
        Tuple of offset and limit.

    Examples:
        >>> page_size_to_offset_limit(1, 10)
        (0, 10)
        >>> page_size_to_offset_limit(2, 10)
        (10, 10)

    Raises:
        ValueError: If page or size is less than 1.

    """
    if page < 1:
        msg = "Page must be greater than 0"
        raise ValueError(msg)
    if size < 1:
        msg = "Size must be greater than 0"
        raise ValueError(msg)

    return (page - 1) * size, size
