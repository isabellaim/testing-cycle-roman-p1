import pytest

from roman.converter import RomanError, from_roman, is_valid_roman, subtract_roman


@pytest.mark.parametrize("text,expected", [("  IV  ", 4), ("X ", 10), (" MCMXCIV", 1994), ("\tIX\n", 9)])
def test_ac1_from_roman_trims_the_ends_of_its_input(text, expected):
    assert from_roman(text) == expected


def test_ac1_is_valid_roman_accepts_a_numeral_with_blanks_at_the_ends():
    assert is_valid_roman("  IV  ") is True


@pytest.mark.parametrize("text", ["X I", "M C M", "I V"])
def test_ac1_internal_whitespace_is_still_invalid(text):
    with pytest.raises(RomanError) as exc:
        from_roman(text)
    assert "invalid roman character" in str(exc.value)


@pytest.mark.parametrize("text", ["", "   ", "\t"])
def test_ac1_a_string_of_blanks_only_is_invalid(text):
    with pytest.raises(RomanError) as exc:
        from_roman(text)
    assert "empty string" in str(exc.value)


@pytest.mark.parametrize("text", ["IIII", "VIIII", "XXXX", "VV", "IVI", "LL", "DD", "CCCC", "MCMM"])
def test_ac2_from_roman_rejects_a_non_canonical_numeral(text):
    with pytest.raises(RomanError) as exc:
        from_roman(text)
    assert "not canonical" in str(exc.value)


@pytest.mark.parametrize("text", ["IIII", "VIIII", "XXXX", "VV", "IVI"])
def test_ac2_is_valid_roman_rejects_a_non_canonical_numeral(text):
    assert is_valid_roman(text) is False


@pytest.mark.parametrize("text,expected", [("IV", 4), ("MCMXCIV", 1994), ("XLIX", 49), ("MMMCMXCIX", 3999)])
def test_ac2_the_canonical_forms_of_the_table_are_still_accepted(text, expected):
    assert from_roman(text) == expected


def test_ac2_each_subtractive_pair_appears_at_most_once():
    assert is_valid_roman("IXIX") is False


def test_ac3_a_difference_of_zero_is_rejected():
    with pytest.raises(RomanError) as exc:
        subtract_roman("I", "I")
    assert ">= 1" in str(exc.value)


def test_ac3_a_negative_difference_is_rejected():
    with pytest.raises(RomanError) as exc:
        subtract_roman("I", "X")
    assert ">= 1" in str(exc.value)


def test_ac3_a_difference_inside_the_range_is_returned():
    assert subtract_roman("X", "I") == "IX"
