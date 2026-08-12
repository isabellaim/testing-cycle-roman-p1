# Testing life cycle — Roman numeral converter

Escuela Superior Politécnica del Litoral — Software Engineering II
Isabella Martín · `iimartin@espol.edu.ec`
Repository: <https://github.com/isabellaim/testing-cycle-roman-p1>

---

## 1. What I did and what came out of it

The system is a roman numeral converter that arrived with fifteen passing tests
and three defects. I applied the three levels of the testing cycle to it, one at
a time, and each level found a different kind of problem, which is the whole
point of planning each one from a different document.

| | Result |
|---|---|
| Inherited suite | 15 tests, passing, unmodified |
| Tests I added | 161, counting parametrised cases (85 unit, 43 integration, 33 acceptance) |
| Branch coverage | 64% before, 99% after |
| Defects found | 3 |
| Found by | integration ×1, acceptance ×2 |
| Final state | 176 passed, 0 failed |

The result I want to highlight up front is the middle one. After writing the
structural unit tests, `converter.py` was at 90% branch coverage with no partial
branches and everything green, and all three defects were still there. Sections
6 and 7 explain how that happens.

---

## 2. Control flow graph of `to_roman`

These are the lines under analysis, `src/roman/converter.py` 40 to 53:

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

I drew it as a program graph in Jorgensen's sense, one node per statement
fragment labelled with its line number. Two decisions I made along the way are
worth stating, because both change the value of V(G).

The first is that line 41 stays as a single node, even though it holds a
compound predicate. The `if` is one decision of the program, so it gets one
two-way branch. The other convention splits `not isinstance(n, int)` from
`isinstance(n, bool)`, since `or` short circuits and the second operand is not
always evaluated; that gives V(G) = 7 rather than 6. Section 4.1 says what
follows from the choice I made.

The second is the sink node `Snk`. The function has four exits, three `raise`
statements and one `return`, but V(G) = E - N + 2 needs a single entry and a
single exit. `Snk` is not a statement of the source, it is just the common exit
that makes the formula apply with P = 1.

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
| `Snk` | — | sink node |

N = 15.

Both loops are pre-test, since `for` and `while` check their condition before
running the body. Each is a decision node with one edge into the body and one
edge out of the loop, and the body comes back to the decision node.

### 2.2 Edges

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
| e18 | `52 → 50` | back edge, check the `while` guard again |
| e19 | `53 → Snk` | return |

E = 19.

Two of these are back edges, and they are what give the graph its loops: e16
goes from the inner `while` back to the outer `for`, and e18 goes from the end
of the `while` body back to its guard.

### 2.3 The graph

![Control flow graph of to_roman](docs/img/control-flow-graph-to-roman.png)

Every node carries the line number of the fragment it stands for, with its kind
beside it. The five yellow ones are the predicates that determine V(G): the
three if-then nodes on lines 41, 43 and 45, and the two pre-test loops on lines
49 and 50.

---

## 3. Cyclomatic complexity

V(G) = E - N + 2 = 19 - 15 + 2 = **6**, using the E = 19 edges and N = 15 nodes
listed above.

I checked the same number two other ways:

| Method | Computation | Result |
|---|---|---|
| Edges and nodes | `19 - 15 + 2` | 6 |
| Binary predicates + 1 | `41, 43, 45, 49, 50` → `5 + 1` | 6 |
| Enclosed regions + 1 | `5 + 1` | 6 |

Every node that is not one of the five predicates has exactly one outgoing edge,
so it adds one node and one edge and leaves E - N alone. That is why drawing
`out = []` and `remaining = n` as two separate nodes instead of merging them
into one block makes no difference to V(G).

---

## 4. Basis set

With V(G) = 6 the basis has six linearly independent paths. I built them with
McCabe's baseline method: pick a baseline path, then flip one predicate at a
time and leave the rest as they were.

| # | Path | Flipped |
|---|---|---|
| B | `40 41 43 45 47 48 49 50 51 52 50 49 53 Snk` | — (baseline) |
| P1 | `40 41 42 Snk` | `41` → true |
| P2 | `40 41 43 44 Snk` | `43` → true |
| P3 | `40 41 43 45 46 Snk` | `45` → true |
| P4 | `40 41 43 45 47 48 49 53 Snk` | `49` → exhausted at once |
| P5 | `40 41 43 45 47 48 49 50 49 53 Snk` | `50` → false at once |

They are independent because each one brings in an edge none of the earlier ones
use: P1 brings e2 and e4, P2 brings e5 and e7, P3 brings e8 and e10, P4 brings
e14 in a traversal that skips the body, P5 brings e16, and B brings e15, e17 and
e18. Between the six of them they also cover all nineteen edges.

### 4.1 Test data

| Path | Input | Test |
|---|---|---|
| B | `to_roman(1000)` → `"M"` | `test_b_while_body_executes_once` |
| P1 | `to_roman("MCMXCIV")` | `test_p1_non_integer_takes_the_guard_on_line_41` |
| P2 | `to_roman(0)` | `test_p2_below_the_lower_bound` |
| P3 | `to_roman(4000)` | `test_p3_above_the_upper_bound` |
| P4 | not feasible | — |
| P5 | `to_roman(1)` → `"I"` | `test_p5_while_predicate_false_on_the_first_pair` |

Three things about that table.

P4 cannot be run. It needs node `49` to find `_PAIRS` already exhausted the
first time it is evaluated, which would mean an empty table, and `_PAIRS` is a
constant with thirteen entries. P4 is still a linearly independent path of the
graph and still belongs in the basis; there is simply no input that produces it.
Ending up with an infeasible basis path is a normal result of the method, not a
mistake in the graph.

The loop paths are not walked one at a time either. With thirteen entries in
`_PAIRS`, every run that terminates goes through `49 → 50` thirteen times, so no
input walks exactly B and nothing else. What the table gives for B and P5 is the
input that first exercises the edge separating that path from the others: e15,
e17 and e18 for B, e16 for P5. That is normal for a graph with loops, where the
basis spans the space of paths and real runs are combinations of its members.

The `bool` case does not get a path of its own. `to_roman(True)` and
`to_roman("MCMXCIV")` both walk P1, because line 41 is one node. They take the
same branch through different operands: the string through
`not isinstance(n, int)`, and `True` through `isinstance(n, bool)`, since `bool`
subclasses `int` and the first operand is false for it. I kept a test for both
anyway, `test_p1_bool_reaches_the_second_operand_of_line_41`, because a basis
set is a lower bound on what to test rather than a ceiling. Had I split line 41
into two nodes, V(G) would be 7 and `True` would have its own basis path.

---

## 5. Definition–use table for `to_roman`

A c-use is a computational use, on the right hand side of an assignment or as an
argument. A p-use is a use inside a predicate. I write pairs as
`(variable, def line, use line)`.

One thing to note: I count `out.append(symbol)` on line 51 as a c-use of `out`
and not as a definition, because the name is never rebound and only the list it
points to changes. If you count a mutating call as a definition instead, line 51
adds the pairs `(out, 51, 51)` and `(out, 51, 53)`.

| Variable | Definitions | Uses | Use kind | du-pairs |
|---|---|---|---|---|
| `n` | 40 (parameter) | 41, 43, 45, 48 | p, p, p, c | `(n,40,41)` p · `(n,40,43)` p · `(n,40,45)` p · `(n,40,48)` c |
| `out` | 47 | 51, 53 | c, c | `(out,47,51)` c · `(out,47,53)` c |
| `remaining` | 48, 52 | 50, 52 | p, c | `(remaining,48,50)` p · `(remaining,48,52)` c · `(remaining,52,50)` p · `(remaining,52,52)` c |
| `value` | 49 (loop target) | 50, 52 | p, c | `(value,49,50)` p · `(value,49,52)` c |
| `symbol` | 49 (loop target) | 51 | c | `(symbol,49,51)` c |

That is 13 du-pairs, 6 of them p-use and 7 c-use.

`n` is read twice on line 41, once per operand of the `or`, but both are p-uses
on the same line, so in the `(variable, def line, use line)` notation they are
the same pair `(n, 40, 41)`. Which operand does the reading is a property of the
predicate, not of the du-pair, and I discuss it in section 4.1.

### 5.1 Pairs created by the redefinition of `remaining`

`remaining` is defined on line 48 and redefined on line 52, inside the `while`
body, so line 52 is a use and a definition at the same time:

```
48  remaining = n            <- def
50  while remaining >= value <- p-use
52  remaining -= value       <- c-use of the old value, then def of the new one
```

| du-pair | Kind | What it is | Killed by |
|---|---|---|---|
| `(remaining, 48, 50)` | p-use | the guard runs for the first time, on the value that came from `n` | line 52, on the first iteration |
| `(remaining, 48, 52)` | c-use | the first subtraction reads the value that came from `n` | line 52, itself |
| `(remaining, 52, 50)` | p-use | created by the redefinition: the guard runs again after the body, on the decremented value | the next run of line 52 |
| `(remaining, 52, 52)` | c-use | created by the redefinition: each iteration feeds the next through the accumulator | the next run of line 52 |

Line 52 kills line 48: once the first iteration is over there is no
definition-clear path left from line 48 to any use. The last two pairs exist
only because of the redefinition, and both are covered. `(remaining, 52, 52)`
needs the same pair consumed twice in a row, which
`test_b_while_body_executes_repeatedly` gets with `to_roman(3000)` → `"MMM"`.

### 5.2 All-uses coverage

All thirteen pairs are exercised, so the unit tests meet the all-uses criterion
for `to_roman`:

| Pairs | Covering input |
|---|---|
| `(n,40,41)` | `to_roman("MCMXCIV")` and `to_roman(True)` |
| `(n,40,43)` | `to_roman(0)` |
| `(n,40,45)` | `to_roman(4000)` |
| `(n,40,48)`, `(out,47,51)`, `(out,47,53)`, `(remaining,48,50)`, `(remaining,48,52)`, `(value,49,50)`, `(value,49,52)`, `(symbol,49,51)` | `to_roman(3999)` |
| `(remaining,52,50)`, `(remaining,52,52)` | `to_roman(3000)` |

At this point all-uses was satisfied, branch coverage of `to_roman` was 100%,
and `to_roman(4)` was still returning `"IIII"`. Both criteria tell you which
paths ran. Neither tells you whether the value carried along them was right.

---

## 6. What the integration level found

### 6.1 The defect

Line 17 of `converter.py` said:

```python
(5, "V"),
(5, "IV"),   # IV is worth 4, not 5
(1, "I"),
```

The table is scanned in order and `(5, "V")` comes first, so it takes the 5.
By the time `to_roman` got to `(5, "IV")` the condition `remaining >= 5` was
false no matter what the input was, which made the `IV` entry unreachable.
Control fell through to `(1, "I")` and appended `I` four times.

| Input | Before the fix | Specification |
|---|---|---|
| `to_roman(4)` | `IIII` | `IV` |
| `to_roman(14)` | `XIIII` | `XIV` |
| `to_roman(1994)` | `MCMXCIIII` | `MCMXCIV` |
| `add_roman("II", "II")` | `IIII` | `IV` |

Fixing it took one character, `(5, "IV")` to `(4, "IV")`, in commit `b2ba968`.

### 6.2 The test that caught it

```python
@pytest.mark.parametrize("a,b,expected", [("II", "II", "IV"), ...])
def test_add_roman_matches_the_mandatory_examples_of_section_7(a, b, expected):
    assert add_roman(a, b) == expected
```

```
E       AssertionError: assert 'IIII' == 'IV'
```

`add_roman` is `to_roman(from_roman(a) + from_roman(b))`, so this test puts three
units together and compares the result against the example the specification
gives in section 7.

### 6.3 Why the unit tests of each function pass anyway

There are three reasons, and they pile up.

The first is that a wrong constant is not a missing path. My Part 3 unit tests
are structural, derived from the source as the workshop asks, and a structural
test picks its inputs off the control flow graph: one path where the `while`
guard holds, one where it does not, one through each guard. None of those needs
`to_roman(4)`. The suite hit 100% branch coverage of lines 40 to 53 with no
partial branches while `(5, "IV")` was still sitting in the table. The defect is
not on an edge of the graph, it is in the value of a constant, and no path-based
criterion — statement, branch, all-uses, or the basis set of section 4 — can see
that.

The second is that the inherited suite had the same blind spot. Its fifteen
tests check `to_roman` at 1, 2, 3, 5, 10, 50, 100, 500 and 1000, and none of
those has a 4 in any digit, which is the only way to reach the broken entry. Its
two round trips, on 7 and 58, miss it as well.

The third is the one I found most interesting: a second defect was hiding the
first. Section 7 also says that whatever `add_roman` returns must be accepted by
`is_valid_roman`. Written straight as a test, that invariant passed on the
broken code:

```python
def test_the_result_of_add_roman_is_accepted_by_is_valid_roman(a, b):
    assert is_valid_roman(add_roman(a, b)) is True    # passed with a='II', b='II'
```

`add_roman("II", "II")` gave `"IIII"`, and `is_valid_roman("IIII")` said `True`,
because `from_roman` was not checking canonical form at all. That is the third
defect, in section 7.2. The two cancelled each other out, and two more invariant
tests passed for exactly the same reason:

| Test | On the broken code | Why |
|---|---|---|
| `is_valid_roman(add_roman("II","II"))` | passed | `is_valid_roman("IIII")` was `True` |
| `from_roman(to_roman(4)) == 4` | passed | `from_roman("IIII")` was `4` |
| `is_valid_roman(to_roman(4))` | passed | same reason |

An invariant that compares two parts of the same system is only as good as the
weaker part. What actually caught the defect was an oracle from outside the
system: the value `"IV"` written in section 7, and the rule from section 2 that
a canonical numeral never repeats a symbol four times in a row.

```python
def test_the_result_of_add_roman_never_repeats_a_symbol_four_times(a, b):
    result = add_roman(a, b)
    assert "IIII" not in result     # AssertionError: assert 'IIII' not in 'IIII'
```

---

## 7. Acceptance criteria

I wrote these three from `SPECIFICATION.md` alone, in Given / When / Then form,
and implemented them in `tests/test_acceptance.py`. At the time the suite was
green and branch coverage was 90%.

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

`from_roman` called `s.upper()` and never `s.strip()`, so a leading blank got as
far as the character scan and was thrown out as an invalid symbol. Fixed in
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

`from_roman` checked the characters and the subtractive pairs and then just
added the symbols up. Nothing looked at the five rules of section 4. Fixed in
`e93397c` with `_scan_groups` and `_check_canonical`.

### AC-3 — An out-of-range result is rejected (section 7) — passed

> Given two roman numerals whose difference is zero or negative, when
> `subtract_roman` is applied to them, then the system raises `RomanError`
> instead of returning a numeral outside 1 to 3999.

This one passed on the original code, since `subtract_roman("I", "I")` ends up
calling `to_roman(0)` and the guard on line 43 was already right. I kept it to
show the criteria came from the specification and were not reverse engineered
from failures I already knew about.

### 7.1 Why coverage cannot find defects like these

AC-1 and AC-2 failed on code reporting 90% branch coverage with no partial
branches, and that follows from what the metric actually measures. Coverage only
knows about code that exists: it takes the statements and edges that are there
and reports which ones ran. The defects behind AC-1 and AC-2 are missing
behaviour. Nobody wrote `s.strip()`, and nobody wrote the five canonical rules.
There was no untaken `strip` branch and no untaken canonical-form branch,
because neither branch existed. Missing code adds nothing to the denominator, so
the metric has no way to represent it. Deleting required behaviour actually
raises coverage, since the deleted lines can no longer be reported as uncovered.

| Question | Answered by |
|---|---|
| Did this line, branch or du-pair run? | coverage, a structural measure |
| Was the value it produced correct? | the oracle of the test, section 6 |
| Is the behaviour there at all? | only a specification, this section |

Nothing but a document written independently of the code can answer the third
one. That is why the testing cycle plans each level from a different artifact,
unit testing from the code and acceptance testing from the requirements: a suite
planned entirely from the code can never get ahead of what the code already
does.

### 7.2 A note on how not to define canonical form

Section 4 of the specification warns against defining canonical form as
`to_roman(from_roman(s)) == s`, because that uses the code as its own oracle and
a defect in `to_roman` would make the formula swallow it.

That formula is already in the repository, as the unused helper
`_roundtrip_differs` on lines 76 and 77, and it is the only line left uncovered
in the final report. If I had built `_check_canonical` on top of it:

```
_roundtrip_differs(4, "IIII")  ->  to_roman(4) != "IIII"  ->  "IIII" != "IIII"  ->  False
```

The broken `to_roman` would have declared `"IIII"` to be the canonical form of
4, and AC-2 would have passed against a system that was still wrong. So
`_check_canonical` implements the five rules of section 4 directly and never
calls `to_roman`.

---

## 8. Coverage

### 8.1 Before, with the inherited suite only

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

64% branch coverage and 9 partial branches. No error path was being exercised,
and `is_valid_roman`, `add_roman` and `subtract_roman` were never called at all.

### 8.2 In the middle, after the unit tests and before any fix

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

90% branch coverage, no partial branches, 100 tests passing, three defects still
in place. The six uncovered lines were the two helpers nothing called. This is
the state I wrote the integration and acceptance tests against; running the full
suite at the same commit gave 26 failed and 150 passed.

### 8.3 After, with all three fixes

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
src/roman/converter.py     109      1     62      0    99%   77
--------------------------------------------------------------------
TOTAL                      109      1     62      0    99%
============================= 176 passed in 0.15s ==============================
```

| | Before | Middle | After |
|---|---|---|---|
| Branch coverage | 64% | 90% | 99% |
| Partial branches | 9 | 0 | 0 |
| Tests | 15 | 100 | 176 |
| Defects present | 3 | 3 | 0 |

The one uncovered line is the body of `_roundtrip_differs`, for the reason in
section 7.2. Raw captures are in [`docs/evidence/`](docs/evidence/).

### 8.4 Checking it independently of the suite

I also ran the fixed system against every normative table in the specification
and over the whole supported range, with
[`docs/verify_specification.py`](docs/verify_specification.py):

```
$ python docs/verify_specification.py

sections 2, 3, 4, 5, 6, 7 reference tables ............... 33 checks, all ok
from_roman(to_roman(n)) == n for n in 1..3999 ............ no mismatches
is_valid_roman(to_roman(n)) for n in 1..3999 ............. no mismatches

35 passed, 0 failed
```

---

## 9. The three defects

Each fix is its own commit, and the message says which level found it.

| # | Commit | Defect | Section | Found at |
|---|---|---|---|---|
| 1 | `b2ba968` | `_PAIRS` held `(5, "IV")` instead of `(4, "IV")`, so the entry was unreachable and `to_roman(4)` gave `"IIII"` | §2 | integration |
| 2 | `8d567df` | `from_roman` never trimmed its input, so `"  IV  "` was rejected | §3 | acceptance |
| 3 | `e93397c` | `from_roman` never checked canonical form, so `"IIII"` gave 4 and `is_valid_roman("IIII")` gave `True` | §4 | acceptance |

```
e93397c fix(acceptance): reject non canonical numerals in from_roman per spec section 4
8d567df fix(acceptance): trim surrounding whitespace in from_roman per spec section 3
b2ba968 fix(integration): correct the value of the IV entry in _PAIRS per spec section 2
e059999 test: add unit, integration and acceptance levels of the testing cycle
```

I did not touch the fifteen inherited tests, and all fifteen still pass:

```
$ git diff upstream/main -- tests/test_converter.py
$ pytest tests/test_converter.py -q
15 passed
```

---

## 10. Conclusion

Every level of the testing cycle is planned from a different artifact, and that
is why each one finds a different kind of defect. This system happened to show
all three cases.

The unit level, planned from the code, gave me a graph with V(G) = 6, a basis
set of six paths, all-uses coverage of `to_roman` and 90% branch coverage with
no partial branches. It found nothing, and it could not have: it took its inputs
from the same source that held the wrong constant.

The integration level, planned from the design in section 7, found the `_PAIRS`
defect, but only through an oracle outside the system. The invariant test that
compared two of the system's own parts passed, because a second defect was
covering for the first.

The acceptance level, planned from the requirements, found two defects that no
structural measure could have reported, because the behaviour was absent rather
than untested.

The number I would keep from all this is the middle measurement: 90% branch
coverage, no partial branches, everything green, three defects present. Coverage
tells you how much of the code you have was exercised. It says nothing about
whether that code is the code the specification asked for.

---

## Running it

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
