# Part 3: unit tests for the rest of converter.py, derived from the source.
# Each one exercises a single function; compositions belong to Part 4.
import pytest

from roman.converter import (
    RomanError,
    add_roman,
    from_roman,
    is_valid_roman,
    subtract_roman,
    to_roman,
)


def test_from_roman_rejects_a_non_string():
    with pytest.raises(RomanError) as exc:
        from_roman(4)
    assert "must be a string" in str(exc.value)


def test_from_roman_rejects_none():
    with pytest.raises(RomanError) as exc:
        from_roman(None)
    assert "must be a string" in str(exc.value)


def test_from_roman_rejects_the_empty_string():
    with pytest.raises(RomanError) as exc:
        from_roman("")
    assert "empty string" in str(exc.value)


def test_from_roman_rejects_an_unknown_character():
    with pytest.raises(RomanError) as exc:
        from_roman("Z")
    assert "invalid roman character" in str(exc.value)


def test_from_roman_rejects_an_unknown_character_in_the_middle():
    with pytest.raises(RomanError) as exc:
        from_roman("XZI")
    assert "invalid roman character" in str(exc.value)


def test_from_roman_upper_cases_its_input():
    assert from_roman("iv") == 4


def test_from_roman_accepts_mixed_case():
    assert from_roman("mCmXcIv") == 1994


@pytest.mark.parametrize(
    "text,expected",
    [("IV", 4), ("IX", 9), ("XL", 40), ("XC", 90), ("CD", 400), ("CM", 900)],
)
def test_from_roman_takes_the_subtractive_branch(text, expected):
    assert from_roman(text) == expected


# A single trailing symbol has no lookahead available.
def test_from_roman_handles_the_last_character_without_lookahead():
    assert from_roman("I") == 1


def test_from_roman_accumulates_single_symbols():
    assert from_roman("III") == 3


def test_from_roman_accumulates_descending_symbols():
    assert from_roman("MDCLXVI") == 1666


@pytest.mark.parametrize("text", ["IL", "IC", "VX", "IM", "XD"])
def test_from_roman_rejects_an_invalid_subtractive_pair(text):
    with pytest.raises(RomanError) as exc:
        from_roman(text)
    assert "invalid subtractive pair" in str(exc.value)


# MMMM is well formed but worth 4000.
def test_from_roman_rejects_a_well_formed_string_above_the_range():
    with pytest.raises(RomanError) as exc:
        from_roman("MMMM")
    assert isinstance(exc.value, RomanError)


def test_is_valid_roman_returns_true_when_from_roman_succeeds():
    assert is_valid_roman("MCMXCIV") is True


def test_is_valid_roman_returns_false_when_from_roman_raises():
    assert is_valid_roman("Z") is False


def test_is_valid_roman_returns_false_for_the_empty_string():
    assert is_valid_roman("") is False


@pytest.mark.parametrize("value", [123, None, 4.0, [], {}, ("I",), True])
def test_is_valid_roman_never_raises(value):
    assert is_valid_roman(value) is False


def test_add_roman_returns_a_roman_string():
    assert add_roman("I", "I") == "II"


def test_subtract_roman_returns_a_roman_string():
    assert subtract_roman("III", "I") == "II"


def test_add_roman_propagates_the_range_error_of_to_roman():
    with pytest.raises(RomanError) as exc:
        add_roman("MMM", "M")
    assert "<= 3999" in str(exc.value)


def test_subtract_roman_propagates_the_range_error_of_to_roman():
    with pytest.raises(RomanError) as exc:
        subtract_roman("I", "I")
    assert ">= 1" in str(exc.value)


def test_add_roman_propagates_the_error_of_from_roman():
    with pytest.raises(RomanError) as exc:
        add_roman("Z", "I")
    assert "invalid roman character" in str(exc.value)


def test_subtract_roman_propagates_the_error_of_from_roman():
    with pytest.raises(RomanError) as exc:
        subtract_roman("I", "Z")
    assert "invalid roman character" in str(exc.value)


@pytest.mark.parametrize("n", [1, 2, 3, 5, 10, 50, 100, 500, 1000, 3999])
def test_round_trip_on_values_the_inherited_suite_already_covers(n):
    assert from_roman(to_roman(n)) == n
