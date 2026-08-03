# Part 3: unit level, structural tests for to_roman (converter.py lines 40-53).
#
# These tests are STRUCTURAL: they are derived from the source code, not from
# SPECIFICATION.md. Each one realises a basis path of the control flow graph
# documented in REPORT.md, and its oracle is what the code itself is written to
# do (which guard raises, which loop edge is taken).
#
# This is deliberate, and it is the point of the workshop: a structural test
# suite can drive to_roman to full branch coverage and still not notice that an
# entry of the _PAIRS table holds the wrong value. See REPORT.md, section 5.
import pytest

from roman.converter import RomanError, to_roman


# --- Path P1: N1 true -> raise at line 42 -----------------------------------
# not isinstance(n, int) is true, the second operand is never evaluated.
def test_p1_non_integer_takes_the_first_guard():
    with pytest.raises(RomanError) as exc:
        to_roman("MCMXCIV")
    assert "integer" in str(exc.value)


def test_p1_float_takes_the_first_guard():
    with pytest.raises(RomanError) as exc:
        to_roman(4.0)
    assert "integer" in str(exc.value)


# --- Path P2: N1 false, N2 true -> raise at line 42 --------------------------
# bool is a subclass of int, so the first operand is false and the compound
# predicate is only decided by its second operand.
def test_p2_bool_reaches_the_second_operand_of_the_compound_guard():
    with pytest.raises(RomanError) as exc:
        to_roman(True)
    assert "integer" in str(exc.value)


def test_p2_false_reaches_the_second_operand_of_the_compound_guard():
    with pytest.raises(RomanError) as exc:
        to_roman(False)
    assert "integer" in str(exc.value)


# --- Path P3: N4 true -> raise at line 44 ------------------------------------
def test_p3_below_the_lower_bound():
    with pytest.raises(RomanError) as exc:
        to_roman(0)
    assert ">= 1" in str(exc.value)


def test_p3_negative_value():
    with pytest.raises(RomanError) as exc:
        to_roman(-1)
    assert ">= 1" in str(exc.value)


# --- Path P4: N4 false, N6 true -> raise at line 46 --------------------------
def test_p4_above_the_upper_bound():
    with pytest.raises(RomanError) as exc:
        to_roman(4000)
    assert "<= 3999" in str(exc.value)


# --- Boundaries of the two range guards, both taking the false edge ----------
def test_lower_boundary_is_accepted():
    assert to_roman(1) == "I"


def test_upper_boundary_is_accepted():
    assert to_roman(3999) == "MMMCMXCIX"


# --- Path P6: the for body is entered, the while predicate is false ----------
# For n = 1 the first pair is (1000, "M") and 1 >= 1000 is false, so the edge
# N10 -> N9 is taken without executing the loop body for that pair.
def test_p6_while_predicate_false_on_the_first_pair():
    assert to_roman(1) == "I"


# --- Path P0 (baseline): the while body executes at least once ---------------
def test_p0_while_body_executes_once():
    assert to_roman(1000) == "M"


def test_p0_while_body_executes_repeatedly():
    # remaining is redefined at line 52 on every iteration; three iterations of
    # the while loop for the same pair exercise that redefinition.
    assert to_roman(3000) == "MMM"


# --- The loop terminates: remaining reaches 0 for every value in range -------
# Oracle derived from the code: the while guard can only stop when remaining is
# smaller than every pair value, and the smallest pair value is 1.
@pytest.mark.parametrize("n", [1, 2, 3, 5, 10, 40, 50, 90, 100, 400, 500, 900, 1000, 3999])
def test_every_symbol_appended_belongs_to_the_pairs_table(n):
    result = to_roman(n)
    assert set(result) <= set("IVXLCDM")


@pytest.mark.parametrize("n", [1, 2, 3, 5, 10, 50, 100, 500, 1000, 2024, 3999])
def test_the_output_is_a_non_empty_string(n):
    result = to_roman(n)
    assert isinstance(result, str) and result != ""
