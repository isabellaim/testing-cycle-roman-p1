# Testing life cycle — Roman numeral converter

Escuela Superior Politécnica del Litoral — Software Engineering II
Isabella Martín · `iimartin@espol.edu.ec`
Repository: <https://github.com/isabellaim/testing-cycle-roman-p1>

---

## 0. Summary

| | Result |
|---|---|
| Inherited suite | 15 tests, passing, unmodified |
| Tests added | 161 (85 unit, 43 integration, 33 acceptance, counting parametrised cases) |
| Branch coverage before | 64% |
| Branch coverage after | 99% |
| Defects found | 3 |
| Level that found each | integration ×1, acceptance ×2 |
| Final state | 176 passed, 0 failed |

The result worth noting at the outset is that the structural unit tests reached
90% branch coverage of `converter.py`, with no partial branches and every test
passing, while all three defects were still present. Sections 5 and 6 explain
why, and what each level of testing contributed.

---

## 1. Control flow graph of `to_roman`

Source under analysis, `src/roman/converter.py` lines 40 to 53:

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

The graph is a program graph in Jorgensen's sense: one node per statement
fragment, labelled with its line number, and edges representing flow of control.
Two conventions were adopted, and both are stated here because they affect the
value of V(G).

First, the compound predicate on line 41 is kept as a single node. The `if`
statement is one decision of the program and is drawn as one two-way branch. The
alternative convention separates `not isinstance(n, int)` from
`isinstance(n, bool)`, on the grounds that `or` short circuits and the second
operand is not always evaluated; that convention yields V(G) = 7 instead of 6.
Section 3.1 records what follows from the choice made here.

Second, a sink node `Snk` is added. The three `raise` statements and the
`return` are four exits from the function, while V(G) = E - N + 2 requires a
single entry and a single exit. `Snk` does not correspond to any statement of
the source; it is the common exit that makes the graph single-entry and
single-exit, so the formula applies with P = 1.

### 1.1 Nodes

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
| `Snk` | — | sink node |

N = 15.

Both loops are pre-test: `for` and `while` evaluate their condition before the
body runs, so each is drawn as a decision node with one exit edge and one body
edge, and the body returns to the decision node.

### 1.2 Edges

| # | Edge | Condition |
|---|---|---|
| e1 | `40 → 41` | sequence |
| e2 | `41 → 42` | true, the argument is not a usable integer |
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
| e13 | `49 → 50` | another pair remains, enter the body |
| e14 | `49 → 53` | `_PAIRS` exhausted, leave the loop |
| e15 | `50 → 51` | true, `remaining >= value` |
| e16 | `50 → 49` | false, back to the `for` for the next pair |
| e17 | `51 → 52` | sequence |
| e18 | `52 → 50` | back edge, re-evaluate the `while` guard |
| e19 | `53 → Snk` | return |

E = 19.

Two of these edges are back edges, and they are what make the graph contain
loops rather than form a tree: e16 returns from the inner `while` to the outer
`for`, and e18 returns from the end of the `while` body to the `while` guard.

### 1.3 The graph

![Control flow graph of to_roman](docs/img/control-flow-graph-to-roman.png)

Each node carries the line number of the statement fragment it represents, and
the label beside it gives its kind. The five predicates that determine V(G) are
the three if-then nodes on lines 41, 43 and 45 and the two pre-test loops on
lines 49 and 50.

---

## 2. Cyclomatic complexity

V(G) = E - N + 2 = 19 - 15 + 2 = **6**, with E = 19 edges and N = 15 nodes, as
enumerated in sections 1.1 and 1.2.

Two further methods give the same value:

| Method | Computation | Result |
|---|---|---|
| Edges and nodes | `19 - 15 + 2` | 6 |
| Binary predicates + 1 | `41, 43, 45, 49, 50` → `5 + 1` | 6 |
| Enclosed regions + 1 | `5 + 1` | 6 |

Every node other than the five predicates is a sequence node with exactly one
outgoing edge, so it contributes one node and one edge and leaves E - N
unchanged. That is why drawing `out = []` and `remaining = n` as two nodes,
rather than merging them into a single block, does not affect V(G).

---

## 3. Basis set

Since V(G) = 6, a basis consists of six linearly independent paths. They were
derived with McCabe's baseline method: one baseline path, then one path per
predicate, flipping that predicate's decision and leaving the others as in the
baseline.

| # | Path | Flipped |
|---|---|---|
| B | `40 41 43 45 47 48 49 50 51 52 50 49 53 Snk` | — (baseline) |
| P1 | `40 41 42 Snk` | `41` → true |
| P2 | `40 41 43 44 Snk` | `43` → true |
| P3 | `40 41 43 45 46 Snk` | `45` → true |
| P4 | `40 41 43 45 47 48 49 53 Snk` | `49` → exhausted at once |
| P5 | `40 41 43 45 47 48 49 50 49 53 Snk` | `50` → false at once |

Each path introduces at least one edge that no earlier path uses: P1 introduces
e2 and e4, P2 introduces e5 and e7, P3 introduces e8 and e10, P4 introduces e14
in a traversal that skips the loop body, P5 introduces e16, and B introduces
e15, e17 and e18. The six incidence vectors over the 19 edges are therefore
linearly independent, and together they cover every edge of section 1.2.

### 3.1 Test data

| Path | Input | Test |
|---|---|---|
| B | `to_roman(1000)` → `"M"` | `test_b_while_body_executes_once` |
| P1 | `to_roman("MCMXCIV")` | `test_p1_non_integer_takes_the_guard_on_line_41` |
| P2 | `to_roman(0)` | `test_p2_below_the_lower_bound` |
| P3 | `to_roman(4000)` | `test_p3_above_the_upper_bound` |
| P4 | not feasible | — |
| P5 | `to_roman(1)` → `"I"` | `test_p5_while_predicate_false_on_the_first_pair` |

Three remarks on this table.

P4 is infeasible. It requires node `49` to find `_PAIRS` exhausted on its first
evaluation, which would mean an empty table, and `_PAIRS` is a module level
constant with thirteen entries. P4 is a linearly independent path of the graph
and belongs in the basis, but no input can produce that traversal. Infeasible
basis paths are a normal outcome of the method rather than a defect in the
graph.

The loop paths are traversed in combination rather than in isolation. With
thirteen entries in `_PAIRS`, every terminating execution walks `49 → 50`
thirteen times, so no single input walks exactly B and nothing else. The table
gives, for B and P5, the input that first exercises the edge distinguishing that
path from the others: e15, e17 and e18 for B, and e16 for P5. This is the usual
situation for a graph containing loops, where the basis spans the path space and
real executions are linear combinations of its members.

The `bool` case does not receive a basis path of its own. Both `to_roman(True)`
and `to_roman("MCMXCIV")` traverse P1, because line 41 is a single node under
the convention of section 1. The two inputs decide the same branch through
different operands: the string through `not isinstance(n, int)`, and `True`
through `isinstance(n, bool)`, since `bool` is a subclass of `int` and the first
operand is false for it. The suite tests both cases in
`test_p1_bool_reaches_the_second_operand_of_line_41`, since a basis set is a
lower bound on what to test rather than an upper one. Under the alternative
convention the two operands would be separate nodes, V(G) would be 7, and the
`bool` input would correspond to a basis path of its own.

---

## 4. Definition–use table for `to_roman`

A c-use is a computational use, occurring on the right hand side of an
assignment or as an argument; a p-use is a use inside a predicate. Pairs are
written `(variable, def line, use line)`.

One convention should be noted: `out.append(symbol)` on line 51 is recorded as a
c-use of `out` rather than as a definition, because the name `out` is not
rebound and only the list object it refers to is mutated. Under the convention
in which a mutating method call also counts as a definition, line 51 would add
the pairs `(out, 51, 51)` and `(out, 51, 53)`.

| Variable | Definitions | Uses | Use kind | du-pairs |
|---|---|---|---|---|
| `n` | 40 (parameter) | 41, 43, 45, 48 | p, p, p, c | `(n,40,41)` p · `(n,40,43)` p · `(n,40,45)` p · `(n,40,48)` c |
| `out` | 47 | 51, 53 | c, c | `(out,47,51)` c · `(out,47,53)` c |
| `remaining` | 48, 52 | 50, 52 | p, c | `(remaining,48,50)` p · `(remaining,48,52)` c · `(remaining,52,50)` p · `(remaining,52,52)` c |
| `value` | 49 (loop target) | 50, 52 | p, c | `(value,49,50)` p · `(value,49,52)` c |
| `symbol` | 49 (loop target) | 51 | c | `(symbol,49,51)` c |

Total: 13 du-pairs, of which 6 are p-use pairs and 7 are c-use pairs.

The variable `n` is used twice on line 41, once in each operand of the `or`.
Both are p-uses on the same line, so under the notation
`(variable, def line, use line)` they collapse into the single pair `(n, 40, 41)`.
The distinction between the two operands belongs to the predicate rather than to
the du-pair, and is discussed in section 3.1.

### 4.1 Pairs created by the redefinition of `remaining`

`remaining` is defined at line 48 and redefined at line 52, inside the `while`
body, so line 52 is both a use and a definition:

```
48  remaining = n            <- def
50  while remaining >= value <- p-use
52  remaining -= value       <- c-use of the old value, then def of the new one
```

| du-pair | Kind | Meaning | Killed by |
|---|---|---|---|
| `(remaining, 48, 50)` | p-use | the guard is evaluated for the first time, on the value coming from `n` | line 52, on the first iteration |
| `(remaining, 48, 52)` | c-use | the first subtraction reads the value coming from `n` | line 52, itself |
| `(remaining, 52, 50)` | p-use | created by the redefinition: the guard is re-evaluated after the body has run, on the decremented value | the next execution of line 52 |
| `(remaining, 52, 52)` | c-use | created by the redefinition: one iteration feeds the next through the accumulator | the next execution of line 52 |

The definition at line 52 kills the definition at line 48: after the first
iteration no definition-clear path from line 48 to any use survives. The last
two pairs exist only because of the redefinition. Both are covered;
`(remaining, 52, 52)` requires the same pair to be consumed at least twice in
succession, which `test_b_while_body_executes_repeatedly` provides with
`to_roman(3000)` → `"MMM"`.

### 4.2 All-uses coverage

All thirteen pairs are exercised, so the unit tests satisfy the all-uses
criterion for `to_roman`:

| Pairs | Covering input |
|---|---|
| `(n,40,41)` | `to_roman("MCMXCIV")` and `to_roman(True)` |
| `(n,40,43)` | `to_roman(0)` |
| `(n,40,45)` | `to_roman(4000)` |
| `(n,40,48)`, `(out,47,51)`, `(out,47,53)`, `(remaining,48,50)`, `(remaining,48,52)`, `(value,49,50)`, `(value,49,52)`, `(symbol,49,51)` | `to_roman(3999)` |
| `(remaining,52,50)`, `(remaining,52,52)` | `to_roman(3000)` |

At this point all-uses coverage was satisfied, branch coverage of `to_roman` was
100%, and `to_roman(4)` still returned `"IIII"`. Both criteria establish which
paths were executed; neither establishes whether the value carried along a path
was correct.

---

## 5. Integration finding

### 5.1 The defect

Line 17 of `converter.py` read:

```python
(5, "V"),
(5, "IV"),   # the value of IV is 4, not 5
(1, "I"),
```

The table is scanned in order, and `(5, "V")` is tried first and consumes the 5.
By the time `to_roman` reached `(5, "IV")`, the condition `remaining >= 5` was
false by construction, so the `IV` entry was unreachable for every input.
Control fell through to `(1, "I")`, which appended `I` four times.

| Input | Result before the fix | Specification |
|---|---|---|
| `to_roman(4)` | `IIII` | `IV` |
| `to_roman(14)` | `XIIII` | `XIV` |
| `to_roman(1994)` | `MCMXCIIII` | `MCMXCIV` |
| `add_roman("II", "II")` | `IIII` | `IV` |

The correction is one character, `(5, "IV")` to `(4, "IV")`, in commit `b2ba968`.

### 5.2 The failing integration test

```python
@pytest.mark.parametrize("a,b,expected", [("II", "II", "IV"), ...])
def test_add_roman_matches_the_mandatory_examples_of_section_7(a, b, expected):
    assert add_roman(a, b) == expected
```

```
E       AssertionError: assert 'IIII' == 'IV'
```

`add_roman` is `to_roman(from_roman(a) + from_roman(b))`. The test combines three
units — `from_roman`, integer addition and `to_roman` — and compares the
composition against the mandatory example of section 7 of the specification.

### 5.3 Why the unit tests of each function pass

There are three separate reasons, and they compound.

The first is that a wrong constant is not a missing path. The unit tests of
Part 3 are structural, derived from the source as the workshop requires, and a
structural test selects its inputs from the control flow graph: a path where the
`while` guard is true, a path where it is false, a path through each guard. None
of these requires calling `to_roman(4)`. The suite reached 100% branch coverage
of lines 40 to 53, with no partial branches, while `(5, "IV")` was still in the
table. The defect does not lie on an edge of the graph but in the value of a
module level constant, and no path-based criterion — statement, branch, all-uses
or the basis set of section 3 — is sensitive to it.

The second is that the inherited suite selected its inputs from the same blind
spot. Its fifteen tests check `to_roman` at 1, 2, 3, 5, 10, 50, 100, 500 and
1000. None of these has a 4 in any digit position, which is the only way to
reach the broken entry, and the two round trips, `from_roman(to_roman(7))` and
`from_roman(to_roman(58))`, avoid it as well.

The third is that a second defect was masking the first. Section 7 also states
that the result of `add_roman` is always a string accepted by `is_valid_roman`.
Written directly as a test, that invariant passed on the broken code:

```python
def test_the_result_of_add_roman_is_accepted_by_is_valid_roman(a, b):
    assert is_valid_roman(add_roman(a, b)) is True    # passed with a='II', b='II'
```

`add_roman("II", "II")` produced `"IIII"`, and `is_valid_roman("IIII")` returned
`True`, because `from_roman` performed no canonical form validation at all. That
is the third defect, described in section 6. The two defects cancelled each
other, and two further invariant tests passed for the same reason:

| Test | Result on the broken code | Reason |
|---|---|---|
| `is_valid_roman(add_roman("II","II"))` | passed | `is_valid_roman("IIII")` was `True` |
| `from_roman(to_roman(4)) == 4` | passed | `from_roman("IIII")` was `4` |
| `is_valid_roman(to_roman(4))` | passed | as above |

An invariant checked between two components of the same system is only as
reliable as the weaker of the two. What detected the defect was an oracle
external to the system: the value `"IV"` given in section 7 of the
specification, together with the rule from section 2 that a canonical numeral
never contains four identical symbols in succession.

```python
def test_the_result_of_add_roman_never_repeats_a_symbol_four_times(a, b):
    result = add_roman(a, b)
    assert "IIII" not in result     # AssertionError: assert 'IIII' not in 'IIII'
```

---

## 6. Acceptance criteria

The three criteria below were written from `SPECIFICATION.md` alone, in Given /
When / Then form, and implemented in `tests/test_acceptance.py`. All three were
written while the suite was passing and branch coverage stood at 90%.

### AC-1 — Whitespace at the ends is tolerated (section 3) — failed

> Given a roman numeral typed into a user facing field with stray blanks at the
> beginning or the end, when the system converts or validates it, then the
> blanks at the ends are trimmed and the numeral is accepted, while blanks
> inside the numeral keep it invalid.

```
FAILED test_ac1_from_roman_trims_the_ends_of_its_input[  IV  -4]
        RomanError: invalid roman character:
FAILED test_ac1_is_valid_roman_accepts_a_numeral_with_blanks_at_the_ends
        assert False is True
```

`from_roman` called `s.upper()` but never `s.strip()`, so a leading blank
reached the character scan and was rejected as an invalid symbol. Fixed in
`8d567df`.

### AC-2 — Only the canonical form is accepted (section 4) — failed

> Given a string that represents a value but is not the canonical form of that
> value, such as `IIII`, `VIIII`, `XXXX`, `VV` or `IVI`, when the system
> converts or validates it, then it is rejected with `RomanError` and
> `is_valid_roman` returns `False`.

```
FAILED test_ac2_from_roman_rejects_a_non_canonical_numeral[IIII]
        DID NOT RAISE <class 'roman.converter.RomanError'>
FAILED test_ac2_is_valid_roman_rejects_a_non_canonical_numeral[IIII]
        assert True is False
```

`from_roman` validated characters and subtractive pairs and then added the
symbols up, with nothing checking the five rules of section 4. Fixed in
`e93397c` by `_scan_groups` together with `_check_canonical`.

### AC-3 — An out-of-range result is rejected (section 7) — passed

> Given two roman numerals whose difference is zero or negative, when
> `subtract_roman` is applied to them, then the system raises `RomanError`
> instead of returning a numeral outside 1 to 3999.

This passed on the original code, since `subtract_roman("I", "I")` calls
`to_roman(0)` and the guard on line 43 was already correct. It is included to
show that the criteria were derived from the specification rather than
reverse engineered from the failures already known.

### 6.1 Why coverage cannot reveal defects of this kind

AC-1 and AC-2 failed on code that reported 90% branch coverage with no partial
branches. This follows from what the metric measures. Coverage is a function of
the code that exists: it partitions the statements and edges that are present
and reports which of them were executed. The defects behind AC-1 and AC-2 are
missing behaviour, in that `s.strip()` was never written and neither were the
five canonical rules. There was no untaken `strip` branch and no untaken
canonical-form branch, because neither existed. Missing code contributes nothing
to the denominator, so the metric cannot represent it; removing required
behaviour in fact raises coverage, since the deleted code can no longer be
reported as uncovered.

| Question | Answered by |
|---|---|
| Was this line, branch or du-pair executed? | coverage, a structural measure |
| Was the value produced along it correct? | the oracle of the test (section 5) |
| Is the required behaviour present at all? | only a specification (this section) |

Only a document written independently of the code can answer the third question.
This is the reason the testing life cycle plans each level from a different
artifact, unit testing from the code and acceptance testing from the
requirements: a suite planned entirely from the code cannot exceed what the code
already does.

### 6.2 A note on the definition of canonical form

Section 4 of the specification states that canonical form should not be defined
as `to_roman(from_roman(s)) == s`, since that formula uses the code as its own
oracle and a defect in `to_roman` would make the formula accept it.

That formula is already present in the repository as the unused helper
`_roundtrip_differs` on lines 79 and 80, and it is the only uncovered line in
the final coverage report. Had `_check_canonical` been implemented with it, the
result would have been:

```
_roundtrip_differs(4, "IIII")  ->  to_roman(4) != "IIII"  ->  "IIII" != "IIII"  ->  False
```

The defective `to_roman` would have certified `"IIII"` as the canonical form of
4, and AC-2 would have passed against a system that was still incorrect.
`_check_canonical` therefore implements the five rules of section 4 directly and
does not call `to_roman`.

---

## 7. Coverage

### 7.1 Before: inherited suite only

```
$ pytest --cov=roman.converter --cov-branch --cov-report=term-missing

tests/test_converter.py ...............                                  [100%]

================================ tests coverage ================================
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

64% branch coverage with 9 partial branches. Every error path was unexercised,
and `is_valid_roman`, `add_roman` and `subtract_roman` were never called.

### 7.2 Intermediate: after the structural unit tests, before any fix

```
$ pytest tests/test_converter.py tests/test_unit_to_roman.py tests/test_unit_converter.py \
         --cov=roman.converter --cov-branch --cov-report=term-missing

================================ tests coverage ================================
Name                     Stmts   Miss Branch BrPart  Cover   Missing
--------------------------------------------------------------------
src/roman/converter.py      68      6     34      0    90%   88, 92-96
--------------------------------------------------------------------
TOTAL                       68      6     34      0    90%
============================= 100 passed in 0.10s ==============================
```

90% branch coverage, no partial branches, 100 tests passing, and all three
defects still present. The six uncovered lines were the two helpers that nothing
called. This is the state against which the integration and acceptance tests
were written; running the full suite at the same commit gave 26 failed and
150 passed.

### 7.3 After: full suite with all three fixes applied

```
$ pytest --cov=roman.converter --cov-branch --cov-report=term-missing

tests/test_acceptance.py .................................               [ 18%]
tests/test_converter.py ...............                                  [ 27%]
tests/test_integration.py ...........................................    [ 51%]
tests/test_unit_converter.py ...........................................
.....                                                                    [ 78%]
tests/test_unit_to_roman.py .....................................        [100%]

================================ tests coverage ================================
Name                     Stmts   Miss Branch BrPart  Cover   Missing
--------------------------------------------------------------------
src/roman/converter.py     109      1     62      0    99%   80
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

The single uncovered line is 80, the body of `_roundtrip_differs`, discussed in
section 6.2. Raw captures are in [`docs/evidence/`](docs/evidence/).

### 7.4 Independent verification

Beyond the suite, the corrected system was checked against every normative table
of the specification and exhaustively over the supported range, by
[`docs/verify_specification.py`](docs/verify_specification.py):

```
$ python docs/verify_specification.py

sections 2, 3, 4, 5, 6, 7 reference tables ............... 33 checks, all ok
from_roman(to_roman(n)) == n for n in 1..3999 ............ no mismatches
is_valid_roman(to_roman(n)) for n in 1..3999 ............. no mismatches

35 passed, 0 failed
```

---

## 8. Defects and commits

Each fix is a separate commit whose message names the level of testing that
found the defect.

| # | Commit | Defect | Section | Found at |
|---|---|---|---|---|
| 1 | `b2ba968` | `_PAIRS` held `(5, "IV")` instead of `(4, "IV")`, leaving the entry unreachable, so `to_roman(4)` returned `"IIII"` | §2 | integration |
| 2 | `8d567df` | `from_roman` never trimmed its input, so `"  IV  "` was rejected | §3 | acceptance |
| 3 | `e93397c` | `from_roman` performed no canonical form validation, so `"IIII"` returned 4 and `is_valid_roman("IIII")` returned `True` | §4 | acceptance |

```
e93397c fix(acceptance): reject non canonical numerals in from_roman per spec section 4
8d567df fix(acceptance): trim surrounding whitespace in from_roman per spec section 3
b2ba968 fix(integration): correct the value of the IV entry in _PAIRS per spec section 2
e059999 test: add unit, integration and acceptance levels of the testing cycle
```

The fifteen inherited tests in `tests/test_converter.py` were neither modified
nor deleted, and all fifteen still pass:

```
$ git diff upstream/main -- tests/test_converter.py
$ pytest tests/test_converter.py -q
15 passed
```

---

## 9. Conclusion

Each level of the testing life cycle is planned from a different artifact, and
that is why each finds a different kind of defect. All three cases appeared in
this system.

The unit level, planned from the code, produced a graph with V(G) = 6, a basis
set of six paths, all-uses coverage of `to_roman` and 90% branch coverage with
no partial branches. It found no defects, and could not have: it derived its
inputs from the same source that contained the incorrect constant.

The integration level, planned from the design described in section 7 of the
specification, found the `_PAIRS` defect, though only through an oracle external
to the system. The invariant test that compared two of the system's own
components passed, because a second defect masked the first.

The acceptance level, planned from the requirements, found two defects that no
structural measure could have reported, since the required behaviour was absent
rather than merely untested.

The intermediate measurement is the one that summarises the exercise: 90% branch
coverage, no partial branches, every test passing, three defects present.
Coverage bounds how much of the existing code was exercised, and says nothing
about whether that code is what the specification asked for.

---

## Reproducing

```bash
git clone https://github.com/isabellaim/testing-cycle-roman-p1.git
cd testing-cycle-roman-p1
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt -e .

pytest                                                                # 176 passed
pytest --cov=roman.converter --cov-branch --cov-report=term-missing   # 99%
```

## References

[1] Jorgensen, P. *Software Testing: A Craftsman's Approach*, chapters 1, 2, 8, 9 and 10.
[2] Pressman, R. and Maxim, B. *Software Engineering: A Practitioner's Approach*, chapter 22.
[3] Course slides, lecture 1c: Software Testing, Basic Definitions.
[4] Course slides, lecture 2a: Test Cases Identification.
