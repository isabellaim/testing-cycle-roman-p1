import pytest

from roman.converter import (
    RomanError,
    add_roman,
    from_roman,
    is_valid_roman,
    subtract_roman,
    to_roman,
)


@pytest.mark.parametrize(
    "a,b,expected",
    [("II", "II", "IV"), ("IV", "VI", "X"), ("MCMXCIV", "VI", "MM")],
)
def test_add_roman_matches_the_mandatory_examples_of_section_7(a, b, expected):
    assert add_roman(a, b) == expected


@pytest.mark.parametrize("a,b,expected", [("X", "I", "IX"), ("V", "I", "IV")])
def test_subtract_roman_matches_the_mandatory_examples_of_section_7(a, b, expected):
    assert subtract_roman(a, b) == expected


@pytest.mark.parametrize("a,b", [("II", "II"), ("IV", "VI"), ("X", "X"), ("MCMXCIV", "VI")])
def test_the_result_of_add_roman_is_accepted_by_is_valid_roman(a, b):
    assert is_valid_roman(add_roman(a, b)) is True


@pytest.mark.parametrize("a,b", [("X", "I"), ("MM", "I"), ("L", "X")])
def test_the_result_of_subtract_roman_is_accepted_by_is_valid_roman(a, b):
    assert is_valid_roman(subtract_roman(a, b)) is True


@pytest.mark.parametrize("a,b", [("II", "II"), ("III", "I"), ("I", "III"), ("X", "IV")])
def test_the_result_of_add_roman_never_repeats_a_symbol_four_times(a, b):
    result = add_roman(a, b)
    assert "IIII" not in result
    assert "XXXX" not in result
    assert "CCCC" not in result


@pytest.mark.parametrize("a,b", [("II", "II"), ("MCMXCIV", "VI"), ("XX", "XXIV")])
def test_add_roman_agrees_with_the_arithmetic_of_its_two_components(a, b):
    assert from_roman(add_roman(a, b)) == from_roman(a) + from_roman(b)


@pytest.mark.parametrize("a,b", [("X", "I"), ("MM", "VI"), ("L", "VI")])
def test_subtract_roman_agrees_with_the_arithmetic_of_its_two_components(a, b):
    assert from_roman(subtract_roman(a, b)) == from_roman(a) - from_roman(b)


@pytest.mark.parametrize("n", [4, 9, 14, 40, 44, 49, 94, 400, 444, 1994, 2444, 3999])
def test_to_roman_and_from_roman_close_the_round_trip_on_subtractive_values(n):
    assert from_roman(to_roman(n)) == n


@pytest.mark.parametrize("n", [4, 9, 14, 40, 44, 1994, 3999])
def test_is_valid_roman_accepts_everything_to_roman_produces(n):
    assert is_valid_roman(to_roman(n)) is True


def test_a_result_below_the_range_surfaces_as_roman_error():
    with pytest.raises(RomanError) as exc:
        subtract_roman("I", "I")
    assert ">= 1" in str(exc.value)


def test_a_result_above_the_range_surfaces_as_roman_error():
    with pytest.raises(RomanError) as exc:
        add_roman("MMM", "M")
    assert "<= 3999" in str(exc.value)
