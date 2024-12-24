import pytest

from fastapi_batteries.utils.pagination import page_size_to_offset_limit


def test_page_size_to_offset_limit():
    """Test page_size_to_offset_limit with various inputs."""
    # Test first page
    assert page_size_to_offset_limit(page=1, size=10) == (0, 10)

    # Test second page
    assert page_size_to_offset_limit(page=2, size=10) == (10, 10)

    # Test different page sizes
    assert page_size_to_offset_limit(page=1, size=20) == (0, 20)
    assert page_size_to_offset_limit(page=3, size=5) == (10, 5)

    # Test larger page numbers
    assert page_size_to_offset_limit(page=5, size=10) == (40, 10)


def test_page_size_to_offset_limit_edge_cases():
    """Test edge cases for page_size_to_offset_limit."""
    with pytest.raises(ValueError, match="Page must be greater than 0"):
        page_size_to_offset_limit(page=0, size=10)

    with pytest.raises(ValueError, match="Page must be greater than 0"):
        page_size_to_offset_limit(page=-1, size=10)

    with pytest.raises(ValueError, match="Size must be greater than 0"):
        page_size_to_offset_limit(page=1, size=0)

    with pytest.raises(ValueError, match="Size must be greater than 0"):
        page_size_to_offset_limit(page=1, size=-1)
