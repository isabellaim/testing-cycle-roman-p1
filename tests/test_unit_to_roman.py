# Part 3: unit level, structural tests for to_roman (converter.py lines 40-53).
#
# These tests are structural: they are derived from the source code rather than
# from SPECIFICATION.md. Each corresponds to a basis path of the control flow
# graph in REPORT.md section 3, and its oracle is what the code is written to do,
# that is, which guard raises and which loop edge is taken.
#
# A consequence of deriving tests this way is that full branch coverage of
# to_roman is reachable without detecting the wrong value in the _PAIRS table.
# See REPORT.md section 5.3.
import pytest

from roman.converter import RomanError, to_roman


# --- Path P1: 40 41 42 54, the guard on line 41 is true ----------------------
# Decided by the first operand: not isinstance(n, int) is true, so the second
# operand is never evaluated.
def test_p1_non_integer_takes_the_guard_on_line_41():
    with pytest.raises(RomanError) as exc:
        to_roman("MCMXCIV")
    assert "integer" in str(exc.value)


def test_p1_float_takes_the_guard_on_line_41():
    with pytest.raises(RomanError) as exc:
        to_roman(4.0)
    assert "integer" in str(exc.value)


# --- Path P1 again, decided by the second operand of line 41 -----------------
# bool is a subclass of int, so the first operand is false and the predicate is
# decided by isinstance(n, bool). Line 41 is a single node, so this is the same
# basis path as the two tests above. See REPORT.md section 3.1.
def test_p1_bool_reaches_the_second_operand_of_line_41():
    with pytest.raises(RomanError) as exc:
        to_roman(True)
    assert "integer" in str(exc.value)


def test_p1_false_reaches_the_second_operand_of_line_41():
    with pytest.raises(RomanError) as exc:
        to_roman(False)
    assert "integer" in str(exc.value)


# --- Path P2: 40 41 43 44 54, the guard on line 43 is true -------------------
def test_p2_below_the_lower_bound():
    with pytest.raises(RomanError) as exc:
        to_roman(0)
    assert ">= 1" in str(exc.value)


def test_p2_negative_value():
    with pytest.raises(RomanError) as exc:
        to_roman(-1)
    assert ">= 1" in str(exc.value)


# --- Path P3: 40 41 43 45 46 54, the guard on line 45 is true ----------------
def test_p3_above_the_upper_bound():
    with pytest.raises(RomanError) as exc:
        to_roman(4000)
    assert "<= 3999" in str(exc.value)


# --- Boundaries of the two range guards, both taking the false edge ----------
def test_lower_boundary_is_accepted():
    assert to_roman(1) == "I"


def test_upper_boundary_is_accepted():
    assert to_roman(3999) == "MMMCMXCIX"


# --- Path P5: the for body is entered, the while predicate is false ----------
# For n = 1 the first pair is (1000, "M") and 1 >= 1000 is false, so edge e16,
# 50 -> 49, is taken without executing the loop body for that pair.
def test_p5_while_predicate_false_on_the_first_pair():
    assert to_roman(1) == "I"


# --- Path B (baseline): the while body executes at least once, edges e15/e18 -
def test_b_while_body_executes_once():
    assert to_roman(1000) == "M"


def test_b_while_body_executes_repeatedly():
    # remaining is redefined at line 52 on every iteration; three iterations of
    # the while loop for the same pair exercise that redefinition.
    assert to_roman(3000) == "MMM"


# --- Properties derived from the code, holding for every value in range ------
# The while guard can only stop when remaining is smaller than every pair value,
# and the smallest pair value is 1, so the loop terminates and every symbol
# appended comes from the _PAIRS table.
@pytest.mark.parametrize("n", [1, 2, 3, 5, 10, 40, 50, 90, 100, 400, 500, 900, 1000, 3999])
def test_every_symbol_appended_belongs_to_the_pairs_table(n):
    result = to_roman(n)
    assert set(result) <= set("IVXLCDM")


@pytest.mark.parametrize("n", [1, 2, 3, 5, 10, 50, 100, 500, 1000, 2024, 3999])
def test_the_output_is_a_non_empty_string(n):
    result = to_roman(n)
    assert isinstance(result, str) and result != ""
