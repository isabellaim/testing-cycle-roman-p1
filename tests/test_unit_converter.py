# Part 3: unit level, structural tests for the remaining units of converter.py.
#
# Same rule as test_unit_to_roman.py: these tests are derived from the source
# code and exist to drive branch coverage of src/roman/converter.py above 85%.
# They exercise one function at a time and never compose two of them, so that
# the integration level (Part 4) and the acceptance level (Part 5) still have
# something left to find.
import pytest

from roman.converter import (
    RomanError,
    add_roman,
    from_roman,
    is_valid_roman,
    subtract_roman,
    to_roman,
)


# =============================================================================
# from_roman
# =============================================================================

# --- guard at line 57-58: the argument is not a str -------------------------
def test_from_roman_rejects_a_non_string():
    with pytest.raises(RomanError) as exc:
        from_roman(4)
    assert "string" in str(exc.value)


def test_from_roman_rejects_none():
    with pytest.raises(RomanError) as exc:
        from_roman(None)
    assert "string" in str(exc.value)


# --- guard at line 60-61: the empty string ----------------------------------
def test_from_roman_rejects_the_empty_string():
    with pytest.raises(RomanError) as exc:
        from_roman("")
    assert "empty" in str(exc.value)


# --- loop at line 62-64: a character outside the symbol table ----------------
def test_from_roman_rejects_an_unknown_character():
    with pytest.raises(RomanError) as exc:
        from_roman("Z")
    assert "invalid roman character" in str(exc.value)


def test_from_roman_rejects_an_unknown_character_in_the_middle():
    with pytest.raises(RomanError) as exc:
        from_roman("XZI")
    assert "invalid roman character" in str(exc.value)


# --- line 59: the input is upper cased before it is scanned -----------------
def test_from_roman_upper_cases_its_input():
    assert from_roman("iv") == 4


def test_from_roman_accepts_mixed_case():
    assert from_roman("mCmXcIv") == 1994


# --- lines 69-74: the two character lookahead finds a valid subtractive pair -
@pytest.mark.parametrize(
    "text,expected",
    [("IV", 4), ("IX", 9), ("XL", 40), ("XC", 90), ("CD", 400), ("CM", 900)],
)
def test_from_roman_takes_the_subtractive_branch(text, expected):
    assert from_roman(text) == expected


# --- line 69 false: the last character has no lookahead ---------------------
def test_from_roman_handles_the_last_character_without_lookahead():
    assert from_roman("I") == 1


# --- lines 75-81: no pair matches, the single symbol is accumulated ----------
def test_from_roman_accumulates_single_symbols():
    assert from_roman("III") == 3


def test_from_roman_accumulates_descending_symbols():
    assert from_roman("MDCLXVI") == 1666


# --- lines 76-79: a smaller symbol precedes a larger one, outside the six ----
@pytest.mark.parametrize("text", ["IL", "IC", "VX", "IM", "XD"])
def test_from_roman_rejects_an_invalid_subtractive_pair(text):
    with pytest.raises(RomanError) as exc:
        from_roman(text)
    assert "invalid subtractive pair" in str(exc.value)


# --- lines 82-83: the accumulated total falls outside 1..3999 ----------------
def test_from_roman_rejects_a_well_formed_string_above_the_range():
    with pytest.raises(RomanError) as exc:
        from_roman("MMMM")
    assert isinstance(exc.value, RomanError)


# =============================================================================
# is_valid_roman
# =============================================================================

# --- lines 101-102: from_roman returns, the try block succeeds ---------------
def test_is_valid_roman_returns_true_when_from_roman_succeeds():
    assert is_valid_roman("MCMXCIV") is True


# --- lines 103-104: from_roman raises, the except block runs -----------------
def test_is_valid_roman_returns_false_when_from_roman_raises():
    assert is_valid_roman("Z") is False


def test_is_valid_roman_returns_false_for_the_empty_string():
    assert is_valid_roman("") is False


# --- spec section 6: it never raises, for any type of input ------------------
@pytest.mark.parametrize("value", [123, None, 4.0, [], {}, ("I",), True])
def test_is_valid_roman_never_raises(value):
    assert is_valid_roman(value) is False


# =============================================================================
# add_roman and subtract_roman, each exercised as a single unit
# =============================================================================

def test_add_roman_returns_a_roman_string():
    assert add_roman("I", "I") == "II"


def test_subtract_roman_returns_a_roman_string():
    assert subtract_roman("III", "I") == "II"


def test_add_roman_propagates_the_range_error_of_to_roman():
    with pytest.raises(RomanError) as exc:
        add_roman("MMM", "M")
    assert isinstance(exc.value, RomanError)


def test_subtract_roman_propagates_the_range_error_of_to_roman():
    with pytest.raises(RomanError) as exc:
        subtract_roman("I", "I")
    assert isinstance(exc.value, RomanError)


def test_add_roman_propagates_the_error_of_from_roman():
    with pytest.raises(RomanError) as exc:
        add_roman("Z", "I")
    assert isinstance(exc.value, RomanError)


def test_subtract_roman_propagates_the_error_of_from_roman():
    with pytest.raises(RomanError) as exc:
        subtract_roman("I", "Z")
    assert isinstance(exc.value, RomanError)


# =============================================================================
# to_roman and from_roman round trip, still one unit at a time
# =============================================================================

@pytest.mark.parametrize("n", [1, 2, 3, 5, 10, 50, 100, 500, 1000, 3999])
def test_round_trip_on_values_the_inherited_suite_already_covers(n):
    assert from_roman(to_roman(n)) == n
