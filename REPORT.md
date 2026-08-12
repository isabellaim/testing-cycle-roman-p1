# Testing life cycle: Roman numeral converter

Isabella Martín

---

## 1. Summary

The system is a roman numeral converter that arrived with fifteen passing tests
and three defects. I applied the three levels of the testing cycle to it and each level found a different kind of problem.

| | Result |
|---|---|
| Inherited suite | 15 tests, passing, unmodified |
| Tests I added | 161, counting parametrised cases (85 unit, 43 integration, 33 acceptance) |
| Branch coverage | 64% before, 99% after |
| Defects found | 3 |
| Found by | integration (1), acceptance (2)|
| Final state | 176 passed, 0 failed |

---

## 2. Control flow graph of to_roman

These are the lines under analysis:

```python
40  def to_roman(n):
41      if not isinstance(n, int) or isinstance(n, bool):
42          raise RomanError("value must be an integer")
43      if n < _MIN_VALUE:
44          raise RomanError("value must be >= 1")
45      if n > _MAX_VALUE:
46          raise RomanError("value must be <= 3999")
47      out = []
48      remaining = n
49      for value, symbol in _PAIRS:
50          while remaining >= value:
51              out.append(symbol)
52              remaining -= value
53      return "".join(out)
```

It is a program graph with one node per statement fragment, labelled by line
number. Line 41 holds a compound predicate and is drawn as a single if-then
node, since the `if` is one decision of the program. `Snk` is a sink node added
so the graph has a single exit, which V(G) = E - N + 2 requires; the function
itself has four exits, three `raise` and one `return`.

### 2.1 Nodes

| Node | Statement or predicate | Kind |
|---|---|---|
| `40` | `def to_roman(n)` | source node |
| `41` | `not isinstance(n, int) or isinstance(n, bool)` | if-then node |
| `42` | `raise RomanError("value must be an integer")` | sequence node |
| `43` | `n < _MIN_VALUE` | if-then node |
| `44` | `raise RomanError("value must be >= 1")` | sequence node |
| `45` | `n > _MAX_VALUE` | if-then node |
| `46` | `raise RomanError("value must be <= 3999")` | sequence node |
| `47` | `out = []` | sequence node |
| `48` | `remaining = n` | sequence node |
| `49` | `for value, symbol in _PAIRS` | pre-test loop |
| `50` | `while remaining >= value` | pre-test loop |
| `51` | `out.append(symbol)` | sequence node |
| `52` | `remaining -= value` | sequence node |
| `53` | `return "".join(out)` | sequence node |
| `Snk` | | sink node |

N = 15.

### 2.2 Edges

| # | Edge | Condition |
|---|---|---|
| e1 | `40 → 41` | sequence |
| e2 | `41 → 42` | true, not a usable integer |
| e3 | `41 → 43` | false |
| e4 | `42 → Snk` | raise |
| e5 | `43 → 44` | true, `n < 1` |
| e6 | `43 → 45` | false |
| e7 | `44 → Snk` | raise |
| e8 | `45 → 46` | true, `n > 3999` |
| e9 | `45 → 47` | false |
| e10 | `46 → Snk` | raise |
| e11 | `47 → 48` | sequence |
| e12 | `48 → 49` | sequence |
| e13 | `49 → 50` | another pair remains |
| e14 | `49 → 53` | `_PAIRS` exhausted |
| e15 | `50 → 51` | true, `remaining >= value` |
| e16 | `50 → 49` | false, next pair |
| e17 | `51 → 52` | sequence |
| e18 | `52 → 50` | back edge to the guard |
| e19 | `53 → Snk` | return |

E = 19.

e16 and e18 are the back edges: e16 returns from the inner `while` to the outer
`for`, e18 from the end of the `while` body to its guard.

### 2.3 The graph

![Control flow graph of to_roman](docs/img/control-flow-graph-to-roman.png)

---

## 3. Cyclomatic complexity

V(G) = E - N + 2 = 19 - 15 + 2 = 6, with E = 19 and N = 15 from the tables
above.

The count of binary predicates confirms it: lines 41, 43, 45, 49 and 50 give
5 + 1 = 6.

---

## 4. Basis set

Six paths, derived with McCabe's baseline method: a baseline path, then one path
per predicate with that predicate flipped.

| # | Path | Flipped | Input | Test |
|---|---|---|---|---|
| B | `40 41 43 45 47 48 49 50 51 52 50 49 53 Snk` | | `to_roman(1000)` | `test_b_while_body_executes_once` |
| P1 | `40 41 42 Snk` | `41` true | `to_roman("MCMXCIV")` | `test_p1_non_integer_takes_the_guard_on_line_41` |
| P2 | `40 41 43 44 Snk` | `43` true | `to_roman(0)` | `test_p2_below_the_lower_bound` |
| P3 | `40 41 43 45 46 Snk` | `45` true | `to_roman(4000)` | `test_p3_above_the_upper_bound` |
| P4 | `40 41 43 45 47 48 49 53 Snk` | `49` exhausted | not feasible | |
| P5 | `40 41 43 45 47 48 49 50 49 53 Snk` | `50` false | `to_roman(1)` | `test_p5_while_predicate_false_on_the_first_pair` |

Each path introduces an edge the earlier ones do not use. P1 brings e2 and e4,
P2 brings e5 and e7, P3 brings e8 and e10, P4 brings e14 without the body, P5
brings e16, and B brings e15, e17 and e18. The six are therefore linearly
independent, and together they cover all nineteen edges.

P4 has no input that produces it, since it needs `_PAIRS` exhausted on the first
evaluation of node `49` and `_PAIRS` has thirteen entries. An infeasible basis
path is a normal result of the method.

---

## 5. Definition-use table for to_roman

A c-use is a use in an assignment or an argument, a p-use a use inside a
predicate. `out.append(symbol)` on line 51 counts as a c-use of `out`, since the
name is not rebound.

| Variable | Definitions | du-pairs |
|---|---|---|
| `n` | 40 | `(n,40,41)` p-use · `(n,40,43)` p-use · `(n,40,45)` p-use · `(n,40,48)` c-use |
| `out` | 47 | `(out,47,51)` c-use · `(out,47,53)` c-use |
| `remaining` | 48, 52 | `(remaining,48,50)` p-use · `(remaining,48,52)` c-use · `(remaining,52,50)` p-use · `(remaining,52,52)` c-use |
| `value` | 49 | `(value,49,50)` p-use · `(value,49,52)` c-use |
| `symbol` | 49 | `(symbol,49,51)` c-use |

13 du-pairs: 6 p-use and 7 c-use.

`n` is read twice on line 41, once per operand, but both are p-uses on the same
line and collapse into `(n, 40, 41)`.

### 5.1 Pairs created by the redefinition of remaining

`remaining` is defined on line 48 and redefined on line 52, inside the loop
body, so line 52 is a use and a definition at once:

```
48  remaining = n            <- def
50  while remaining >= value <- p-use
52  remaining -= value       <- c-use of the old value, then def of the new one
```

| du-pair | Kind | Created by the redefinition | Killed by |
|---|---|---|---|
| `(remaining, 48, 50)` | p-use | no | line 52, first iteration |
| `(remaining, 48, 52)` | c-use | no | line 52, itself |
| `(remaining, 52, 50)` | p-use | yes | the next run of line 52 |
| `(remaining, 52, 52)` | c-use | yes | the next run of line 52 |

Line 52 kills line 48: after the first iteration there is no definition-clear
path from line 48 to any use. All thirteen pairs are covered.
`(remaining, 52, 52)` needs the same pair consumed twice in a row, which
`test_b_while_body_executes_repeatedly` gets with `to_roman(3000)` giving
`"MMM"`.

---

## 6. Integration finding

### 6.1 The defect

Line 17 of `converter.py` read `(5, "IV")` instead of `(4, "IV")`. The table is
scanned in order and `(5, "V")` comes first, so `remaining >= 5` was already
false when `to_roman` reached the `IV` entry, which made it unreachable. Control
fell through to `(1, "I")`.

| Input | Before | Specification |
|---|---|---|
| `to_roman(4)` | `IIII` | `IV` |
| `to_roman(1994)` | `MCMXCIIII` | `MCMXCIV` |
| `add_roman("II", "II")` | `IIII` | `IV` |

Fixed in `b2ba968`.

### 6.2 The failing test

```python
def test_add_roman_matches_the_mandatory_examples_of_section_7(a, b, expected):
    assert add_roman(a, b) == expected
```

```
E       AssertionError: assert 'IIII' == 'IV'
```

`add_roman` is `to_roman(from_roman(a) + from_roman(b))`, so the test combines
three units and compares the result against the example in section 7 of the
specification.

### 6.3 Why the unit tests of each function pass

A wrong constant is not a missing path. The unit tests are structural, and a
structural test takes its inputs from the control flow graph: one path where the
`while` guard holds, one where it does not, one through each guard. None of
those requires `to_roman(4)`. The suite reached 100% branch coverage of lines 40
to 53 with `(5, "IV")` still in place, because the defect is in the value of a
constant and not on an edge of the graph.

The inherited suite had the same gap. It checks `to_roman` at 1, 2, 3, 5, 10,
50, 100, 500 and 1000, none of which has a 4 in any digit.

A second defect was also masking the first. Section 7 says the result of
`add_roman` must be accepted by `is_valid_roman`, and written directly that
invariant passed:

```python
assert is_valid_roman(add_roman("II", "II")) is True    # passed
```

`add_roman("II", "II")` returned `"IIII"` and `is_valid_roman("IIII")` returned
`True`, because `from_roman` did not check canonical form, which is defect 3.
Two more invariants passed for the same reason: `from_roman(to_roman(4)) == 4`
and `is_valid_roman(to_roman(4))`.

What caught the defect was an oracle outside the system: the value `"IV"` given
in section 7, and the rule in section 2 that a canonical numeral never repeats a
symbol four times.

```python
def test_the_result_of_add_roman_never_repeats_a_symbol_four_times(a, b):
    assert "IIII" not in add_roman(a, b)    # assert 'IIII' not in 'IIII'
```

---

## 7. Acceptance criteria

Written from `SPECIFICATION.md` and implemented in `tests/test_acceptance.py`,
at a point where the suite was green at 90% branch coverage.

### AC-1. Whitespace at the ends (section 3): failed

> Given a roman numeral typed with stray blanks at the beginning or the end,
> when the system converts or validates it, then the blanks at the ends are
> trimmed and the numeral is accepted, while blanks inside it keep it invalid.

```
FAILED test_ac1_from_roman_trims_the_ends_of_its_input[  IV  -4]
        RomanError: invalid roman character:
```

`from_roman` called `s.upper()` but not `s.strip()`. Fixed in `8d567df`.

### AC-2. Canonical form only (section 4): failed

> Given a string that represents a value but is not the canonical form of that
> value, such as `IIII` or `VV`, when the system converts or validates it, then
> it is rejected with `RomanError` and `is_valid_roman` returns `False`.

```
FAILED test_ac2_from_roman_rejects_a_non_canonical_numeral[IIII]
        DID NOT RAISE <class 'roman.converter.RomanError'>
```

`from_roman` checked characters and subtractive pairs, then added the symbols
up. Nothing applied the five rules of section 4. Fixed in `e93397c` with
`_scan_groups` and `_check_canonical`.

### AC-3. Out-of-range result (section 7): passed

> Given two roman numerals whose difference is zero or negative, when
> `subtract_roman` is applied, then the system raises `RomanError` instead of
> returning a numeral outside 1 to 3999.

Passed on the original code, since `subtract_roman("I", "I")` calls
`to_roman(0)` and the guard on line 43 was already correct.

### 7.1 Why coverage cannot reveal these

Both defects are missing behaviour. `s.strip()` was never written, and neither
were the five canonical rules, so there was no uncovered `strip` branch and no
uncovered canonical-form branch to report. Coverage partitions the code that
exists and reports which parts ran; code that was never written contributes
nothing to the denominator. Removing required behaviour in fact raises coverage.

Coverage answers whether a line or branch ran. Whether the value it produced was
correct is up to the oracle of the test, and whether the behaviour is present at
all can only be answered against a specification. That is why the unit level is
planned from the code and the acceptance level from the requirements.

---

## 8. Coverage

### 8.1 Before, inherited suite only

```
$ pytest --cov=roman.converter --cov-branch --cov-report=term-missing

tests/test_converter.py ...............                                  [100%]

Name                     Stmts   Miss Branch BrPart  Cover   Missing
--------------------------------------------------------------------
src/roman/converter.py      68     24     34      9    64%   42, 44, 46, 58, 61,
                                                            64, 72-74, 79, 83,
                                                            88, 92-96, 100-104,
                                                            108, 112
--------------------------------------------------------------------
TOTAL                       68     24     34      9    64%
============================== 15 passed in 0.05s ==============================
```

### 8.2 After the unit tests, before any fix

```
$ pytest tests/test_converter.py tests/test_unit_to_roman.py tests/test_unit_converter.py \
         --cov=roman.converter --cov-branch --cov-report=term-missing

Name                     Stmts   Miss Branch BrPart  Cover   Missing
--------------------------------------------------------------------
src/roman/converter.py      68      6     34      0    90%   88, 92-96
--------------------------------------------------------------------
TOTAL                       68      6     34      0    90%
============================= 100 passed in 0.10s ==============================
```

90% branch coverage, no partial branches, all tests green, and the three defects
still present. The full suite at this commit gave 26 failed and 150 passed.

### 8.3 After the three fixes

```
$ pytest --cov=roman.converter --cov-branch --cov-report=term-missing

tests/test_acceptance.py .................................               [ 18%]
tests/test_converter.py ...............                                  [ 27%]
tests/test_integration.py ...........................................    [ 51%]
tests/test_unit_converter.py ...........................................
.....                                                                    [ 78%]
tests/test_unit_to_roman.py .....................................        [100%]

Name                     Stmts   Miss Branch BrPart  Cover   Missing
--------------------------------------------------------------------
src/roman/converter.py     109      1     62      0    99%   77
--------------------------------------------------------------------
TOTAL                      109      1     62      0    99%
============================= 176 passed in 0.15s ==============================
```

| | Before | Intermediate | After |
|---|---|---|---|
| Branch coverage | 64% | 90% | 99% |
| Partial branches | 9 | 0 | 0 |
| Tests | 15 | 100 | 176 |
| Defects present | 3 | 3 | 0 |

Line 77 is the body of `_roundtrip_differs`, a helper that defines canonical
form as `to_roman(from_roman(s)) == s`. Section 4 of the specification warns
against that formula, so `_check_canonical` applies the five rules directly and
the helper stays unused.

Raw captures are in [`docs/evidence/`](docs/evidence/).
[`docs/verify_specification.py`](docs/verify_specification.py) checks the fixed
system against every table of the specification and over the range 1 to 3999.

---

## 9. Defects and commits

| # | Commit | Defect | Section | Found at |
|---|---|---|---|---|
| 1 | `b2ba968` | `_PAIRS` held `(5, "IV")` instead of `(4, "IV")`, so `to_roman(4)` gave `"IIII"` | 2 | integration |
| 2 | `8d567df` | `from_roman` did not trim its input, so `"  IV  "` was rejected | 3 | acceptance |
| 3 | `e93397c` | `from_roman` did not check canonical form, so `is_valid_roman("IIII")` was `True` | 4 | acceptance |

```
e93397c fix(acceptance): reject non canonical numerals in from_roman per spec section 4
8d567df fix(acceptance): trim surrounding whitespace in from_roman per spec section 3
b2ba968 fix(integration): correct the value of the IV entry in _PAIRS per spec section 2
e059999 test: add unit, integration and acceptance levels of the testing cycle
```

The fifteen inherited tests are unmodified and still pass:

```
$ git diff upstream/main -- tests/test_converter.py
$ pytest tests/test_converter.py -q
15 passed
```

---

## 10. Conclusion

Each level of the cycle is planned from a different artifact, and each found a
different kind of defect. The unit level, planned from the code, reached
V(G) = 6, a basis set of six paths, all thirteen du-pairs and 90% branch
coverage, and found nothing, because it drew its inputs from the same source
that held the wrong constant. The integration level found that constant, but
only through an oracle outside the system. The acceptance level, planned from
the requirements, found two defects that no structural measure could report,
because the behaviour was absent rather than untested.

## Running it

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt -e .
pytest --cov=roman.converter --cov-branch --cov-report=term-missing
```

## References

[1] Jorgensen, P. *Software Testing: A Craftsman's Approach*, chapters 1, 2, 8, 9 and 10.
[2] Pressman, R. and Maxim, B. *Software Engineering: A Practitioner's Approach*, chapter 22.
[3] Course slides, lecture 1c: Software Testing, Basic Definitions.
[4] Course slides, lecture 2a: Test Cases Identification.
