# Part 3: unit tests for to_roman, derived from the source (converter.py 40-53).
# Test names carry the basis path they cover; REPORT.md section 4.1 maps them.
import pytest

from roman.converter import RomanError, to_roman


def test_p1_non_integer_takes_the_guard_on_line_41():
    with pytest.raises(RomanError) as exc:
        to_roman("MCMXCIV")
    assert "must be an integer" in str(exc.value)


def test_p1_float_takes_the_guard_on_line_41():
    with pytest.raises(RomanError) as exc:
        to_roman(4.0)
    assert "must be an integer" in str(exc.value)


# bool subclasses int, so the first operand of line 41 is false and the second
# one decides. Same basis path as above, reached through the other operand.
def test_p1_bool_reaches_the_second_operand_of_line_41():
    with pytest.raises(RomanError) as exc:
        to_roman(True)
    assert "must be an integer" in str(exc.value)


def test_p1_false_reaches_the_second_operand_of_line_41():
    with pytest.raises(RomanError) as exc:
        to_roman(False)
    assert "must be an integer" in str(exc.value)


def test_p2_below_the_lower_bound():
    with pytest.raises(RomanError) as exc:
        to_roman(0)
    assert ">= 1" in str(exc.value)


def test_p2_negative_value():
    with pytest.raises(RomanError) as exc:
        to_roman(-1)
    assert ">= 1" in str(exc.value)


def test_p3_above_the_upper_bound():
    with pytest.raises(RomanError) as exc:
        to_roman(4000)
    assert "<= 3999" in str(exc.value)


def test_lower_boundary_is_accepted():
    assert to_roman(1) == "I"


def test_upper_boundary_is_accepted():
    assert to_roman(3999) == "MMMCMXCIX"


# For n = 1 the first pair is (1000, "M"), so the while guard is false straight
# away and edge e16 is taken without running the body.
def test_p5_while_predicate_false_on_the_first_pair():
    assert to_roman(1) == "I"


def test_b_while_body_executes_once():
    assert to_roman(1000) == "M"


# Three iterations on the same pair exercise the redefinition of remaining.
def test_b_while_body_executes_repeatedly():
    assert to_roman(3000) == "MMM"


@pytest.mark.parametrize("n", [1, 2, 3, 5, 10, 40, 50, 90, 100, 400, 500, 900, 1000, 3999])
def test_every_symbol_appended_belongs_to_the_pairs_table(n):
    assert set(to_roman(n)) <= set("IVXLCDM")


@pytest.mark.parametrize("n", [1, 2, 3, 5, 10, 50, 100, 500, 1000, 2024, 3999])
def test_the_output_is_a_non_empty_string(n):
    result = to_roman(n)
    assert isinstance(result, str) and result != ""
