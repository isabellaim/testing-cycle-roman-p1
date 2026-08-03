"""Independent check of the fixed system against SPECIFICATION.md.

This is not part of the test suite. It walks every normative table of the
specification and then checks the whole supported range exhaustively, so the
numbers quoted in REPORT.md section 7.4 can be reproduced in one command:

    python docs/verify_specification.py
"""

from roman.converter import (
    RomanError,
    add_roman,
    from_roman,
    is_valid_roman,
    subtract_roman,
    to_roman,
)

ERR = "RomanError"
passed = 0
failed = 0


def call(fn):
    try:
        return fn()
    except RomanError:
        return ERR


def check(label, got, expected):
    global passed, failed
    if got == expected:
        passed += 1
        print(f"  ok    {label:38} = {got!r}")
    else:
        failed += 1
        print(f"  FAIL  {label:38} got {got!r}, expected {expected!r}")


print("section 2 — mandatory reference values of to_roman")
for n, e in [(1, "I"), (4, "IV"), (9, "IX"), (14, "XIV"), (40, "XL"),
             (1994, "MCMXCIV"), (3999, "MMMCMXCIX")]:
    check(f"to_roman({n})", call(lambda n=n: to_roman(n)), e)

print("\nsection 3 — whitespace at the ends is trimmed, inside it is not")
for s, e in [("  IV  ", 4), ("X ", 10), ("X I", ERR), ("   ", ERR)]:
    check(f"from_roman({s!r})", call(lambda s=s: from_roman(s)), e)

print("\nsection 4 — canonical form only")
for s, e in [("IIII", ERR), ("VIIII", ERR), ("XXXX", ERR), ("VV", ERR),
             ("IV", 4), ("MCMXCIV", 1994)]:
    check(f"from_roman({s!r})", call(lambda s=s: from_roman(s)), e)

print("\nsection 5 — invalid subtractive pairs")
for s in ["IL", "IC", "VX"]:
    check(f"from_roman({s!r})", call(lambda s=s: from_roman(s)), ERR)

print("\nsection 6 — is_valid_roman never raises")
for s, e in [("IV", True), ("IIII", False), ("Z", False), ("", False),
             ("  IV  ", True), (123, False), (None, False)]:
    check(f"is_valid_roman({s!r})", call(lambda s=s: is_valid_roman(s)), e)

print("\nsection 7 — roman arithmetic")
for label, fn, e in [
    ("add_roman('II','II')", lambda: add_roman("II", "II"), "IV"),
    ("add_roman('IV','VI')", lambda: add_roman("IV", "VI"), "X"),
    ("add_roman('MCMXCIV','VI')", lambda: add_roman("MCMXCIV", "VI"), "MM"),
    ("subtract_roman('X','I')", lambda: subtract_roman("X", "I"), "IX"),
    ("subtract_roman('I','I')", lambda: subtract_roman("I", "I"), ERR),
    ("add_roman('MMM','M')", lambda: add_roman("MMM", "M"), ERR),
]:
    check(label, call(fn), e)

print("\nexhaustive check over the supported range")
round_trip = [n for n in range(1, 4000) if from_roman(to_roman(n)) != n]
not_valid = [n for n in range(1, 4000) if not is_valid_roman(to_roman(n))]
check("from_roman(to_roman(n)) == n for n in 1..3999", round_trip, [])
check("is_valid_roman(to_roman(n)) for n in 1..3999", not_valid, [])

print(f"\n{passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
