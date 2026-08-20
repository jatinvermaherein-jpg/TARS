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

# Drafted in P-CORE-2, Cooper-RATIFIED in commit 8706128 (command-grammar v1.0 decree)
LINE_NOTED = "Noted. I'll remember that."
LINE_GUEST = "Voice not recognized. Guest rules apply."
LINE_GUEST_DIAL = "Only Cooper moves the dials."

# Bible §22 error-matrix rows, verbatim — declared here for the ears; P-CORE-4 wires the full matrix.
LINE_HEARD_BADLY = "Heard that badly. I don't guess — repeat, please."
LINE_NO_MIC = "No mic. Text mode it is."

# Bible §22 matrix rows, verbatim — the remaining lines of the 16-row script (line 209 is scripture).
LINE_VERIFIED = "Cooper."
LINE_VOICE_UNCERTAIN = "Voice uncertain. Passphrase, please."
LINE_NOISE = "Too much noise to hear you. Closer, or repeat."
LINE_TWO_VOICES = "One at a time, please."
LINE_VOICEPRINT_UNCLEAR = "Voiceprint unclear. Quiet room, one more round."
LINE_MIC_DENIED = "Microphone access is off. TARS can't hear you like this."
# The honest caveat (bible §22), the enrollment wizard's opening line — told plainly, always.
LINE_ENROLL_CAVEAT = ("First, honesty: this voice check is convenience-grade — like face-unlock on a phone, "
                      "not a password. A good recording could fool it. That is why dangerous work always asks "
                      "for live confirmation and your passphrase — layers, not paranoia.")

_ONES = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten",
         "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen"]
_TENS = ["twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]


def number_words(value: int) -> str:
    """Render plain lower-case words. The 0..100 band (dial acks, command numbers) is
    byte-stable canon; P-CORE-6 extends the composer to 9999 for meter reads (storage
    gigabytes, uptime hours). >= 10000 falls back to plain digits — declared, honest."""
    value = int(value)
    if value > 9999:
        return str(value)
    if value < 100:
        if value < 20:
            return _ONES[value]
        tens, rest = divmod(value, 10)
        word = _TENS[tens - 2]
        return f"{word} {_ONES[rest]}" if rest else word
    if value < 1000:
        hundreds, rest = divmod(value, 100)
        head = f"{_ONES[hundreds]} hundred"
        return f"{head} {number_words(rest)}" if rest else head
    thousands, rest = divmod(value, 1000)
    head = f"{number_words(thousands)} thousand"
    return f"{head} {number_words(rest)}" if rest else head


def dial_line(name: str, value: int) -> str:
    """Bible §10 canon acknowledge: 'humor 60' -> 'Humor adjusted to sixty percent.'"""
    return f"{name.capitalize()} adjusted to {number_words(value)} percent."


def confirm_line(target: str, verb: str = "deletes") -> str:
    """Bible §11 operator confirm with the target filled in (verb variant for the RED row family)."""
    return f"That {verb} {target}. Type YES to confirm."


# Command-grammar §9 acknowledgment templates (v1.0) — GREEN acks are short
# past-tense, numbers in words. Declared once; every operator row speaks one shape.
def open_ack(display: str) -> str:
    return f"{display} opened."


def open_fail_ack(display: str) -> str:
    return f"{display} wouldn't open from here."


def close_ack(display: str) -> str:
    return f"{display} closed."


def delete_ack(target: str) -> str:
    return f"{target} deleted."


def move_ack(source: str, dest: str) -> str:
    return f"{source} moved to {dest}."


def power_ack(verb: str, seconds: int) -> str:
    verbs = {"shutdown": "Shutting down", "restart": "Restarting", "sleep": "Sleeping"}
    return f"{verbs[verb]} in {number_words(seconds)} seconds."


def volume_ack(action: str, value: int = None) -> str:
    if action == "set":
        return f"Volume set to {number_words(value)}."
    return {"up": "Volume raised.", "down": "Volume lowered.", "mute": "Volume muted."}[action]


def brightness_ack(action: str, value: int = None) -> str:
    if action == "set":
        return f"Brightness set to {number_words(value)}."
    return {"up": "Brightness raised.", "down": "Brightness lowered."}[action]


def snap_ack(action: str) -> str:
    return {"left": "Snapped left.", "right": "Snapped right.", "maximize": "Maximized."}[action]


def preset_idle_line(name: str, humor: int, vernacular: int) -> str:
    """A preset that would move nothing says so instead of pretending."""
    return f"{name} — humor and vernacular already stand at {number_words(humor)} and {number_words(vernacular)}."


def pending_line(feature: str, phase: str) -> str:
    """Honest pending line for meters another phase owns — never a fake number."""
    return f"{feature} isn't wired yet — that answer ships with {phase}. Nothing invented until then."


def boot_line(humor: int, vernacular: int) -> str:
    """New chat: the boot shape re-read with CURRENT dials (LINE_BOOT stays the factory boot)."""
    return f"TARS online. Honesty: ninety. Humor: {number_words(humor)}. Vernacular: {number_words(vernacular)}."


def dials_line(dials: dict) -> str:
    return (f"Humor {number_words(dials['humor'])}. Vernacular {number_words(dials['vernacular'])}. "
            f"Discretion {number_words(dials['discretion'])}. Trust {number_words(dials['trust'])}. "
            f"{LINE_HONESTY_FIXED}")


def time_line(now) -> str:
    return f"The time is {now:%H:%M}."


def date_line(now) -> str:
    return f"The date is {now:%Y-%m-%d}."


def clarify_app_line(token: str) -> str:
    """§16 ambiguity law: one short clarifying question — never a guessed app."""
    return f"'{token}' isn't on my app list — which app did you mean?"


def find_one_line(path: str) -> str:
    return f"Found it — {path}."


def find_list_line(paths: list) -> str:
    rows = "\n".join(f"{i + 1}. {p}" for i, p in enumerate(paths))
    return f"I found a few — which one?\n{rows}"


LINE_FIND_NONE = "Nothing in your folders matched that."
LINE_NOTHING_REMEMBERED = "Nothing on that yet."
LINE_NO_RESULTS = "Nothing came back for that search."
LINE_NEAR_MISS = "Almost a command — I won't guess it. Say it once more, plainly?"


def search_row_line(rank: int, title: str, source: str) -> str:
    return f"{rank}. {title} — {source}"


def search_picks_line() -> str:
    return "Say 'open one', 'open two', or 'open three' — I'll take you there."


def open_rank_line(rank: int, title: str) -> str:
    return f"Opening result {number_words(rank)} — {title}."


def words_number(text: str):
    """Inverse of number_words: digits or words 0..100 -> int, anything else -> None."""
    cleaned = str(text).strip().lower()
    if cleaned.isdigit():
        value = int(cleaned)
        return value if 0 <= value <= 100 else None
    if cleaned == "one hundred":
        return 100
    parts = cleaned.split()
    if len(parts) == 1 and parts[0] in _ONES:
        return _ONES.index(parts[0])
    if len(parts) == 1 and parts[0] in _TENS:
        return (_TENS.index(parts[0]) + 2) * 10
    if len(parts) == 2 and parts[0] in _TENS and parts[1] in _ONES[1:10]:
        return (_TENS.index(parts[0]) + 2) * 10 + _ONES.index(parts[1])
    return None


# --- P-CORE-6 daily-ops + Office Studio ack family (grammar v1.1; generative, literal-pinned) ---
LINE_CLIPBOARD_EMPTY = "The clipboard is empty."
LINE_COPIED = "Copied to the clipboard."
LINE_NOTHING_TO_COPY = "Nothing to copy yet."
LINE_SHOT_SAVED = "Screenshot saved to Desktop."


def meter_unavailable_line(meter: str) -> str:
    """A meter that can't be read here says so — never a guessed number (§16)."""
    return f"{meter} isn't available here. I won't guess."


LINE_NO_CPU_METER = meter_unavailable_line("CPU meter")


def saved_ack(name: str) -> str:
    """§18: finished work lands on the Desktop; the deed line is LOCAL mint."""
    return f"Saved to Desktop: {name}."


def reminder_ack(text: str, when: str) -> str:
    return f"Reminder set for {when}: {text}."


def alarm_ack(when: str) -> str:
    return f"Alarm set for {when}."


def timer_set_ack(label: str, span_words: str) -> str:
    return f"Timer set for {span_words}{': ' + label if label else ''}."


def reminder_fire_line(text: str) -> str:
    return f"Reminder: {text}."


def alarm_fire_line(text: str) -> str:
    return f"Alarm: {text}." if text else "Alarm."


def timer_fire_line(label: str) -> str:
    return f"Timer done{': ' + label if label else ''}."


def away_line(inner: str) -> str:
    """Missed-while-OFF wrap: fires once on next summon, never spam-batches."""
    return f"While you were away: {inner.rstrip('.')}."


def cancel_ack(target: str) -> str:
    return f"Cancelled: {target}."


def uptime_ack(hours: int) -> str:
    return f"Uptime: {number_words(hours)} hours."


def ram_ack(percent: int) -> str:
    return f"RAM in use: {number_words(percent)} percent."


def storage_ack(gb: int) -> str:
    return f"Storage free: {number_words(gb)} gigabytes."


def hog_ack(name: str, percent: int) -> str:
    return f"Top of the CPU pile: {name} at {number_words(percent)} percent."


def clipboard_line(content: str) -> str:
    return f"On your clipboard: {content}"


def office_draft_line(count: int, unit: str, title: str) -> str:
    """Hue honesty: the CONTENT travelled (cloud/amber); the save line stays local."""
    return f"Drafted {number_words(count)} {unit} for '{title}' on the cloud."


# --- P-CORE-7 TeleSend ack family (grammar v1.2; bible §17 stage -> show -> YES) ---
LINE_TELE_NOT_LINKED = "Telegram isn't linked yet. Setup happens on the AiO."
LINE_TELE_FAILED = "That send didn't go through. Nothing left the box."
LINE_WA_FILES_OFF = "WhatsApp file-send stays off. Telegram carries files."
LINE_NO_CONTACTS = "I don't know anyone yet."


def no_contact_line(name: str) -> str:
    """I-don't-guess doctrine: ONE line, never a fuzzy match on the people-book."""
    return f"I don't know {name} yet. Save them first."


def no_channel_line(display: str, channel: str) -> str:
    return f"I know {display}, but no {channel} is saved. Save it first."


def contact_saved_ack(display: str, channel: str) -> str:
    return f"Saved — {display} on {channel}."


def contact_updated_ack(display: str, channel: str) -> str:
    return f"Updated — {display} now on {channel} too."


def contact_dup_line(display: str, channel: str) -> str:
    """A name already owed that channel says so — never a silent overwrite."""
    return f"I already know {display} on {channel}. Forget them first to change it."


def contact_forgot_ack(display: str) -> str:
    return f"Forgotten — {display}."


def contacts_line(rows: list) -> str:
    listing = "\n".join(
        f"{i + 1}. {row['name']}: telegram {row['telegram'] or 'none'}, whatsapp {row['whatsapp'] or 'none'}"
        for i, row in enumerate(rows))
    return f"Who I know:\n{listing}"


def stage_text_line(display: str, channel: str, payload: str) -> str:
    """§17's face: recipient, channel, the EXACT quoted bytes, then the gate words."""
    return f'Staged for {display} on {channel}: "{payload}". Type YES to send it.'


def stage_file_line(display: str, path: str) -> str:
    """Files stage with the FULL path — Cooper judges the exact artifact (§17)."""
    return f"Staged for {display} on Telegram: the file {path}. Type YES to send it."


def send_draft_line(payload: str) -> str:
    """Two-truths pair: the DRAFT travelled on the ring (cloud/lane hue); the gate
    preview that follows stays local mint."""
    return f'Drafted on the cloud: "{payload}".'


def sent_ack(display: str, channel: str) -> str:
    return f"Sent to {display} on {channel}."


def opened_ack(display: str) -> str:
    return f"Opened WhatsApp for {display}. Review and press send there."


def nothing_sent_line(name: str) -> str:
    return f"Nothing sent to {name} yet."


def sent_recall_line(display: str, rows: list) -> str:
    listing = "\n".join(
        f"{i + 1}. {row['channel'].capitalize()} {row['kind']}: {row['summary']}"
        for i, row in enumerate(rows))
    return f"What you sent {display}:\n{listing}"
