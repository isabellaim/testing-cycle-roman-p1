# Part 4: integration level.
#
# The unit level exercised one function at a time. This file combines two or
# more units and checks that they work together as a group, which is the
# collaboration described in section 7 of SPECIFICATION.md: add_roman and
# subtract_roman are built on top of from_roman and to_roman, and their result
# must be accepted by is_valid_roman.
#
# The oracle comes from the specification rather than from the source, since a
# composition has no source of its own from which to derive one.
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
# The mandatory examples of section 7
# =============================================================================

@pytest.mark.parametrize(
    "a,b,expected",
    [
        ("II", "II", "IV"),          # spec section 7, first mandatory example
        ("IV", "VI", "X"),
        ("MCMXCIV", "VI", "MM"),
    ],
)
def test_add_roman_matches_the_mandatory_examples_of_section_7(a, b, expected):
    assert add_roman(a, b) == expected


@pytest.mark.parametrize("a,b,expected", [("X", "I", "IX"), ("V", "I", "IV")])
def test_subtract_roman_matches_the_mandatory_examples_of_section_7(a, b, expected):
    assert subtract_roman(a, b) == expected


# =============================================================================
# The collaboration invariant of section 7
# =============================================================================

@pytest.mark.parametrize("a,b", [("II", "II"), ("IV", "VI"), ("X", "X"), ("MCMXCIV", "VI")])
def test_the_result_of_add_roman_is_accepted_by_is_valid_roman(a, b):
    # Section 7: "the result of add_roman is always a string that
    # is_valid_roman accepts".
    assert is_valid_roman(add_roman(a, b)) is True


@pytest.mark.parametrize("a,b", [("X", "I"), ("MM", "I"), ("L", "X")])
def test_the_result_of_subtract_roman_is_accepted_by_is_valid_roman(a, b):
    assert is_valid_roman(subtract_roman(a, b)) is True


# The invariant above is checked against is_valid_roman, which belongs to the
# same system. Section 2 provides an oracle independent of the system: the
# canonical form never contains four identical symbols in succession.
@pytest.mark.parametrize("a,b", [("II", "II"), ("III", "I"), ("I", "III"), ("X", "IV")])
def test_the_result_of_add_roman_never_repeats_a_symbol_four_times(a, b):
    result = add_roman(a, b)
    assert "IIII" not in result
    assert "XXXX" not in result
    assert "CCCC" not in result


# =============================================================================
# The three units agree on the same value
# =============================================================================

@pytest.mark.parametrize("a,b", [("II", "II"), ("MCMXCIV", "VI"), ("XX", "XXIV")])
def test_add_roman_agrees_with_the_arithmetic_of_its_two_components(a, b):
    result = add_roman(a, b)
    assert from_roman(result) == from_roman(a) + from_roman(b)


@pytest.mark.parametrize("a,b", [("X", "I"), ("MM", "VI"), ("L", "VI")])
def test_subtract_roman_agrees_with_the_arithmetic_of_its_two_components(a, b):
    result = subtract_roman(a, b)
    assert from_roman(result) == from_roman(a) - from_roman(b)


# The round trip closes only if to_roman produces the canonical string that
# from_roman reads back, for every value in the supported range.
@pytest.mark.parametrize("n", [4, 9, 14, 40, 44, 49, 94, 400, 444, 1994, 2444, 3999])
def test_to_roman_and_from_roman_close_the_round_trip_on_subtractive_values(n):
    assert from_roman(to_roman(n)) == n


@pytest.mark.parametrize("n", [4, 9, 14, 40, 44, 1994, 3999])
def test_is_valid_roman_accepts_everything_to_roman_produces(n):
    assert is_valid_roman(to_roman(n)) is True


# =============================================================================
# Errors cross the composition boundary as RomanError
# =============================================================================

def test_a_result_below_the_range_surfaces_as_roman_error():
    with pytest.raises(RomanError) as exc:
        subtract_roman("I", "I")
    assert isinstance(exc.value, RomanError)


def test_a_result_above_the_range_surfaces_as_roman_error():
    with pytest.raises(RomanError) as exc:
        add_roman("MMM", "M")
    assert isinstance(exc.value, RomanError)
