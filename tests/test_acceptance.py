# Part 5: acceptance level.
#
# These tests are functional: they are derived from SPECIFICATION.md alone and
# were written without reference to the control flow of converter.py. Each
# implements one of the three acceptance criteria of REPORT.md section 6, in
# Given / When / Then form.
#
# When they were written the suite was passing and branch coverage of
# src/roman/converter.py was 90%. Two of the three criteria failed, because they
# describe behaviour the code did not implement; with no branch present, no
# coverage metric could report the gap. See REPORT.md section 6.1.
import pytest

from roman.converter import RomanError, from_roman, is_valid_roman, subtract_roman


# =============================================================================
# AC-1  Spec section 3, whitespace tolerance
#
#   Given a roman numeral typed into a user facing field with stray blanks
#     at the beginning or the end,
#   When the system converts or validates it,
#   Then the blanks at the ends are trimmed and the numeral is accepted,
#     while blanks inside the numeral keep it invalid.
# =============================================================================

@pytest.mark.parametrize("text,expected", [("  IV  ", 4), ("X ", 10), (" MCMXCIV", 1994), ("\tIX\n", 9)])
def test_ac1_from_roman_trims_the_ends_of_its_input(text, expected):
    assert from_roman(text) == expected


def test_ac1_is_valid_roman_accepts_a_numeral_with_blanks_at_the_ends():
    assert is_valid_roman("  IV  ") is True


@pytest.mark.parametrize("text", ["X I", "M C M", "I V"])
def test_ac1_internal_whitespace_is_still_invalid(text):
    with pytest.raises(RomanError) as exc:
        from_roman(text)
    assert isinstance(exc.value, RomanError)


@pytest.mark.parametrize("text", ["", "   ", "\t"])
def test_ac1_a_string_of_blanks_only_is_invalid(text):
    with pytest.raises(RomanError) as exc:
        from_roman(text)
    assert isinstance(exc.value, RomanError)


# =============================================================================
# AC-2  Spec section 4, canonical form only
#
#   Given a string that represents a value but is not the canonical form
#     of that value,
#   When the system converts or validates it,
#   Then it is rejected with RomanError and is_valid_roman answers False.
# =============================================================================

@pytest.mark.parametrize("text", ["IIII", "VIIII", "XXXX", "VV", "IVI", "LL", "DD", "CCCC", "MCMM"])
def test_ac2_from_roman_rejects_a_non_canonical_numeral(text):
    with pytest.raises(RomanError) as exc:
        from_roman(text)
    assert isinstance(exc.value, RomanError)


@pytest.mark.parametrize("text", ["IIII", "VIIII", "XXXX", "VV", "IVI"])
def test_ac2_is_valid_roman_rejects_a_non_canonical_numeral(text):
    assert is_valid_roman(text) is False


@pytest.mark.parametrize("text,expected", [("IV", 4), ("MCMXCIV", 1994), ("XLIX", 49), ("MMMCMXCIX", 3999)])
def test_ac2_the_canonical_forms_of_the_table_are_still_accepted(text, expected):
    assert from_roman(text) == expected


def test_ac2_each_subtractive_pair_appears_at_most_once():
    assert is_valid_roman("IXIX") is False


# =============================================================================
# AC-3  Spec section 7, the result of an operation stays inside the range
#
#   Given two roman numerals whose difference is zero or negative,
#   When subtract_roman is applied to them,
#   Then the system raises RomanError instead of returning a numeral
#     outside 1 to 3999.
# =============================================================================

def test_ac3_a_difference_of_zero_is_rejected():
    with pytest.raises(RomanError) as exc:
        subtract_roman("I", "I")
    assert isinstance(exc.value, RomanError)


def test_ac3_a_negative_difference_is_rejected():
    with pytest.raises(RomanError) as exc:
        subtract_roman("I", "X")
    assert isinstance(exc.value, RomanError)


def test_ac3_a_difference_inside_the_range_is_returned():
    assert subtract_roman("X", "I") == "IX"
