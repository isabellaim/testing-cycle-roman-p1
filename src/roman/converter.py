class RomanError(ValueError):
    pass


_PAIRS = (
    (1000, "M"),
    (900, "CM"),
    (500, "D"),
    (400, "CD"),
    (100, "C"),
    (90, "XC"),
    (50, "L"),
    (40, "XL"),
    (10, "X"),
    (9, "IX"),
    (5, "V"),
    (4, "IV"),
    (1, "I"),
)


_SINGLE = {
    "I": 1,
    "V": 5,
    "X": 10,
    "L": 50,
    "C": 100,
    "D": 500,
    "M": 1000,
}


_VALID_SUBTRACTIVE = {"IV", "IX", "XL", "XC", "CD", "CM"}


_MIN_VALUE = 1
_MAX_VALUE = 3999


def to_roman(n):
    if not isinstance(n, int) or isinstance(n, bool):
        raise RomanError("value must be an integer")
    if n < _MIN_VALUE:
        raise RomanError("value must be >= 1")
    if n > _MAX_VALUE:
        raise RomanError("value must be <= 3999")
    out = []
    remaining = n
    for value, symbol in _PAIRS:
        while remaining >= value:
            out.append(symbol)
            remaining -= value
    return "".join(out)


def from_roman(s):
    if not isinstance(s, str):
        raise RomanError("value must be a string")
    # Spec section 3: input arrives from a user facing field, so blanks at the
    # ends are trimmed. Blanks inside the numeral are left in place and the
    # character scan below rejects them.
    text = s.strip().upper()
    if text == "":
        raise RomanError("empty string is not a roman numeral")
    for ch in text:
        if ch not in _SINGLE:
            raise RomanError("invalid roman character: " + ch)
    groups = _scan_groups(text)
    total = 0
    for group in groups:
        total += _group_value(group)
    if total < _MIN_VALUE or total > _MAX_VALUE:
        raise RomanError("value out of range 1..3999")
    # Spec section 4: only the canonical form of a value is accepted.
    _check_canonical(text, groups)
    return total


def _roundtrip_differs(value, text):
    return to_roman(value) != text


def _count_char(text, ch):
    total = 0
    for c in text:
        if c == ch:
            total += 1
    return total


def _scan_groups(text):
    """Split a roman string into groups.

    A group is one of the six subtractive pairs of section 2 of the
    specification, or a single symbol. Section 5 is enforced here: outside the
    six pairs, no symbol may be followed by one of greater value.
    """
    groups = []
    i = 0
    length = len(text)
    while i < length:
        if i + 1 < length:
            pair = text[i:i + 2]
            if pair in _VALID_SUBTRACTIVE:
                groups.append(pair)
                i += 2
                continue
        if i + 1 < length:
            current = _SINGLE[text[i]]
            nxt = _SINGLE[text[i + 1]]
            if current < nxt:
                raise RomanError("invalid subtractive pair: " + text[i:i + 2])
        groups.append(text[i])
        i += 1
    return groups


def _group_value(group):
    if len(group) == 2:
        return _SINGLE[group[1]] - _SINGLE[group[0]]
    return _SINGLE[group]


def _check_canonical(text, groups):
    """Apply the five rules of section 4 of the specification.

    The rules are the normative criterion. Canonical form is deliberately NOT
    defined as to_roman(from_roman(s)) == s, which would use the code as its
    own oracle and would accept any defect that to_roman happens to have.
    """
    # Rule 2: V, L and D appear at most once in the whole string.
    for symbol in "VLD":
        if _count_char(text, symbol) > 1:
            raise RomanError("not canonical: " + symbol + " appears more than once")

    # Rule 1: I, X, C and M appear at most three times in a row.
    run_symbol = None
    run_length = 0
    for group in groups:
        if len(group) == 1 and group in "IXCM":
            if group == run_symbol:
                run_length += 1
            else:
                run_symbol = group
                run_length = 1
            if run_length > 3:
                raise RomanError("not canonical: " + group + " repeated more than three times")
        else:
            run_symbol = None
            run_length = 0

    # Rule 3: each of the six subtractive pairs appears at most once.
    seen = set()
    for group in groups:
        if len(group) == 2:
            if group in seen:
                raise RomanError("not canonical: subtractive pair " + group + " repeated")
            seen.add(group)

    # Rules 4 and 5: group values are non-increasing from left to right, and
    # after a subtractive pair every following group is worth less than the
    # subtracted symbol, so IVI is rejected because 4 + 1 = 5 is written V.
    limit = None
    for group in groups:
        value = _group_value(group)
        if limit is not None and value > limit:
            raise RomanError("not canonical: group " + group + " is out of order")
        if len(group) == 2:
            limit = _SINGLE[group[0]] - 1
        else:
            limit = value


def is_valid_roman(s):
    try:
        from_roman(s)
        return True
    except RomanError:
        return False


def add_roman(a, b):
    return to_roman(from_roman(a) + from_roman(b))


def subtract_roman(a, b):
    return to_roman(from_roman(a) - from_roman(b))
