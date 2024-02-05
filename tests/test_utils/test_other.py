import pytest

from src.utils.other import hex_to_rgba


def test_valid_hex_color_codes():
    assert hex_to_rgba("#FF0000") == (255, 0, 0, 255)
    assert hex_to_rgba("#00FF00") == (0, 255, 0, 255)
    assert hex_to_rgba("#0000FF") == (0, 0, 255, 255)
    assert hex_to_rgba("#FFFFFF") == (255, 255, 255, 255)
    assert hex_to_rgba("#000000") == (0, 0, 0, 255)
    assert hex_to_rgba("#123456") == (18, 52, 86, 255)
    assert hex_to_rgba("#12345678") == (18, 52, 86, 120)


def test_invalid_hex_color_codes():
    with pytest.raises(ValueError):
        hex_to_rgba("#12345")  # Invalid: Shorter than 3 characters

    with pytest.raises(ValueError):
        hex_to_rgba("#1234567")  # Invalid: Longer than 8 characters

    with pytest.raises(ValueError):
        hex_to_rgba("#GGGGGG")  # Invalid characters

    with pytest.raises(ValueError):
        hex_to_rgba("#123G56")  # Invalid characters

    with pytest.raises(ValueError):
        hex_to_rgba("#12345G")  # Invalid characters
