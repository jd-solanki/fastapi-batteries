# TODO: Move generic utils that are not related to fastapi batteries to a separate package "pytils-jd"
def bytes_to_kb(bytes: int) -> float:  # noqa: A002
    """Convert bytes to kilobytes."""
    return bytes / 1024


def bytes_to_mb(bytes: int) -> float:  # noqa: A002
    """Convert bytes to megabytes."""
    return bytes / 1024 / 1024


def kb_to_bytes(kb: float) -> int:
    """Convert kilobytes to bytes."""
    return int(kb * 1024)


def kb_to_mb(kb: float) -> int:
    """Convert kilobytes to megabytes."""
    return int(kb / 1024)


def mb_to_bytes(mb: float) -> int:
    """Convert megabytes to bytes."""
    return int(mb * 1024 * 1024)


def mb_to_kb(mb: float) -> int:
    """Convert megabytes to kilobytes."""
    return int(mb * 1024)
