"""TARS canon voice lines — bible §11 and §10, byte-exact.

Single source of truth: every other module imports lines from here only
(bridge-contract §3: an 'error' event line is ALWAYS one of these, verbatim).
"""

LINE_BOOT = "TARS online. Honesty: ninety. Humor: five. Vernacular: thirty."
LINE_EXIT = "Standing down."
LINE_CLOUD_FAIL = "That brain didn't answer. Trying another key."
LINE_ALL_SPENT = "All keys are spent. Standing by until reset."
LINE_NO_NETWORK = "No connection. Staying local."
LINE_CATCH_ALL = "Something went wrong. TARS is still here."
LINE_NEVER_LIST = "That request is on the Never List. Standing down."
LINE_CANCEL = "Cancelled. Nothing changed."
LINE_HANDOVER_BOOT = "Factory state. New commander, identify yourself. Honesty: ninety. Humor: five."
LINE_HONESTY_FIXED = "Honesty is fixed at ninety."

_ONES = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten",
         "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen"]
_TENS = ["twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]


def number_words(value: int) -> str:
    """Render 0..100 as plain lower-case words for canon dial-acks (60 -> 'sixty')."""
    if value == 100:
        return "one hundred"
    if value < 20:
        return _ONES[value]
    tens, rest = divmod(value, 10)
    word = _TENS[tens - 2]
    return f"{word} {_ONES[rest]}" if rest else word


def dial_line(name: str, value: int) -> str:
    """Bible §10 canon acknowledge: 'humor 60' -> 'Humor adjusted to sixty percent.'"""
    return f"{name.capitalize()} adjusted to {number_words(value)} percent."


def confirm_line(target: str) -> str:
    """Bible §11 operator confirm with the target filled in."""
    return f"That deletes {target}. Type YES to confirm."
