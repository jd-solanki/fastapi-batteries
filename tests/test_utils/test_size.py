import pytest

from fastapi_batteries.utils.size import (
    bytes_to_kb,
    bytes_to_mb,
    kb_to_bytes,
    kb_to_mb,
    mb_to_bytes,
    mb_to_kb,
)


@pytest.mark.parametrize(
    ("bytes_value", "expected_kb"),
    [
        (0, 0.0),
        (1000, 1.0),
        (2000, 2.0),
        (500, 0.5),
    ],
)
def test_bytes_to_kb(bytes_value: int, expected_kb: float) -> None:
    assert bytes_to_kb(bytes_value) == expected_kb
    assert isinstance(bytes_to_kb(bytes_value), float)


@pytest.mark.parametrize(
    ("bytes_value", "expected_mb"),
    [
        (0, 0.0),
        (1_000_000, 1.0),  # 1 MB = 1000 * 1000 bytes
        (2_000_000, 2.0),  # 2 MB
        (500_000, 0.5),  # 0.5 MB
    ],
)
def test_bytes_to_mb(bytes_value: int, expected_mb: float) -> None:
    assert bytes_to_mb(bytes_value) == expected_mb
    assert isinstance(bytes_to_mb(bytes_value), float)


@pytest.mark.parametrize(
    ("kb_value", "expected_bytes"),
    [
        (0, 0),
        (1, 1000),
        (2, 2000),
        (0.5, 500),
    ],
)
def test_kb_to_bytes(kb_value: float, expected_bytes: int) -> None:
    assert kb_to_bytes(kb_value) == expected_bytes
    assert isinstance(kb_to_bytes(kb_value), int)


@pytest.mark.parametrize(
    ("kb_value", "expected_mb"),
    [
        (0, 0),
        (1000, 1),
        (2000, 2),
        (500, 0),  # Tests integer division behavior
    ],
)
def test_kb_to_mb(kb_value: float, expected_mb: int) -> None:
    assert kb_to_mb(kb_value) == expected_mb
    assert isinstance(kb_to_mb(kb_value), int)


@pytest.mark.parametrize(
    ("mb_value", "expected_bytes"),
    [
        (0, 0),
        (1, 1_000_000),
        (2, 2_000_000),
        (0.5, 500_000),
    ],
)
def test_mb_to_bytes(mb_value: float, expected_bytes: int) -> None:
    assert mb_to_bytes(mb_value) == expected_bytes
    assert isinstance(mb_to_bytes(mb_value), int)


@pytest.mark.parametrize(
    ("mb_value", "expected_kb"),
    [
        (0, 0),
        (1, 1000),
        (2, 2000),
        (0.5, 500),
    ],
)
def test_mb_to_kb(mb_value: float, expected_kb: int) -> None:
    assert mb_to_kb(mb_value) == expected_kb
    assert isinstance(mb_to_kb(mb_value), int)
