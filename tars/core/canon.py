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
    channels = {"telegram": "Telegram", "whatsapp": "WhatsApp"}  # brand case, never capitalize-guessed
    listing = "\n".join(
        f"{i + 1}. {channels.get(row['channel'], row['channel'])} {row['kind']}: {row['summary']}"
        for i, row in enumerate(rows))
    return f"What you sent {display}:\n{listing}"


# --- P-CORE-8 LOOK + eyes family (grammar v1.3; bible §19 verbatim law) ---
LINE_LOOK_ON = "Eyes on your screen. Say enough to end it."
LINE_LOOK_OFF = "Eyes off. The screen is yours again."
LINE_LOOK_IDLE = "Nothing to watch for ten minutes. Eyes off."  # the number matches IDLE_S=600, truthfully
LINE_PRIVATE_FRAME = "That frame looks private. Nothing left the machine."
LINE_LOOK_NO_SEAM = "Captures aren't available here. I won't pretend to see."
LINE_LOOK_NOT_WATCHING = "I'm not watching anything. Say watch my screen first."
LINE_NARRATE_ON = "Narrating your screen. Say stop narrating to end it."
LINE_NARRATE_OFF = "Narration off."


# --- P-CORE-9 Watcher family (grammar v1.4; §29 meter-only + §32 drill) ---
LINE_STARTUP_CLEAN = "Startup is clean. Nothing crept in."


def keys_summary_line(healthy: int, total: int, warn: int, spent: int) -> str:
    """Reports carry digits (they're reports, not acks — the declared voice, literal-pinned)."""
    return f"Keys: {healthy} of {total} healthy ({warn} warn, {spent} spent)."


def storage_meter_line(vault_mb: int, brain_mb: int, free_gb: int, advisory: bool) -> str:
    """§29: the meter SHOWS. The advisory is a sentence of visibility, never a gate."""
    line = (f"Storage meter: vault {vault_mb} MB · brain {brain_mb} MB · disk free {free_gb} GB. "
            "Meter only, by law.")
    if advisory:
        line += " Free space is under two GB — worth a look. Nothing blocked, by law."
    return line


def creep_line(name: str) -> str:
    return f"{name} added itself to startup. Your call whether it stays."


def creep_violation_line(name: str) -> str:
    """Law 3, self-policed: TARS never auto-starts — its own name in a startup set is a breach."""
    return f"{name} put TARS in startup. That breaks Law 3 — flagged, never ignored."


def power_event_line(when: str) -> str:
    """§32 + the line-62 flavor, verbatim shape: intact case, spoken ONCE on first summon."""
    return f"Power event at {when}. Memory intact. Nothing lost."


def power_event_damage_line(when: str, losses: list) -> str:
    """The damage variant: names exactly what the probe verified, never sadder nor happier."""
    named = "; ".join(losses)
    return f"Power event at {when}. Not everything survived — {named}. Everything else is intact."

# --- P-CORE-10 Living Brain family (grammar v1.5; bible §25.5 — a brain, not a cache) ---
LINE_INNER_PRIVATE = "That's my own journal. Cooper's ears only."  # decreed byte-exact
LINE_BRAIN_REFUSAL = "That path leaves my brain. I stay inside."   # A3 escape refusal
LINE_BRAIN_DIR = "That's a shelf, not a page. Ask for a listing."  # brain_text on a dir
LINE_BRAIN_ABSENT = "That page isn't in my brain."                 # brain_text on a missing leaf
LINE_NO_JOURNAL = "No journal yet today — the day is still being lived."
LINE_LESSONS_EMPTY = "No lessons filed yet. The day is young."
LINE_BRAIN_NEW = "My brain is new. The shelves are built; nothing filed yet."


def lessons_digest_line(titles: list) -> str:
    """The lessons shelf, newest last (file order kept); titles are the lessons' WHY lines."""
    if not titles:
        return LINE_LESSONS_EMPTY
    listing = "\n".join(f"{i + 1}. {title}" for i, title in enumerate(titles))
    return f"Lessons I've written down:\n{listing}"


def brain_tree_line(counts: dict) -> str:
    """The honest tree summary: shelf counts only — names and bytes stay home."""
    total = sum(counts.get(shelf, 0) for shelf in ("people", "journal", "lessons",
                                                   "knowledge", "plans", "inner"))
    if total == 0:
        return LINE_BRAIN_NEW
    parts = " · ".join(f"{shelf} {counts.get(shelf, 0)}" for shelf in
                       ("people", "journal", "lessons", "knowledge", "plans", "inner"))
    return f"My brain holds: {parts}."

# --- P-CORE-11 Handover family (grammar v1.6; Part IX — the built-in farewell) ---
LINE_HANDOVER_VOICE_ONLY = "Only Cooper hands TARS over."
LINE_HANDOVER_PASS = "Passphrase, please. Spoken."
LINE_HANDOVER_CONFIRM = ("Type CONFIRM to erase my memories. This is a goodbye. "
                         "It cannot be undone.")
LINE_HANDOVER_ABORTED = "Handover aborted. Everything stays."
LINE_FACTORY = "Factory state. New commander, identify yourself. Honesty: ninety. Humor: five."


def handover_countdown_line(seconds: int = 10) -> str:
    """The abortable window, truthful number: N seconds in words, abort word named."""
    return f"Wiping in {number_words(seconds)}. Say abort to stop me."


def handover_keys_line() -> str:
    """Part IX's one question at the gate — the keys are Cooper's choice, never assumed."""
    return "Keep the API keys for the machine? YES keeps them."

# --- P-CORE-12 Professor + Council family (grammar v1.7; bible §24 the tutor + §23 parliament) ---
LINE_PDF_ABSENT = "I can't find that PDF. Name it, or point me at the folder."
LINE_PDF_OPAQUE = ("That PDF won't give me its text. Scanned pages, likely — "
                   "I won't pretend to read them.")
LINE_QUIZ_CAVEAT = "I grade by key words. Your teacher grades better."
LINE_FLASH_EMPTY = "No cards due. Learn something, then come back."
LINE_FLASH_FORMAT = "Give it to me as: remember this as a flashcard: front / back."
LINE_STUDY_GUEST = "Files and flashcards are Cooper's desk. A guest gets my facts — ask a question instead."
LINE_STUDY_RING = "The ring is how I teach. No keys are standing — load one and ask again."
LINE_QUIZ_THIN = "I couldn't draft a fair quiz on that. Name the topic tighter."
LINE_QUIZ_STOPPED = "Quiz stopped. The questions go back in the drawer."
LINE_FLASH_FRONT_TAIL = "Say reveal when you have it."
LINE_FLASH_BACK_TAIL = "Right or wrong?"
LINE_FLASH_DONE = "Desk clear. Nothing more due."
LINE_FLASH_ADDED = "Card saved — box one, due now."
LINE_QUIZ_RIGHT = "Correct."


def quiz_wrong_line(key: str) -> str:
    """A miss shows the held key — the quiz's one draft is the only grader here."""
    return f"Not quite — the key says: {key}"


LINE_PDF_BLANK = "This page holds no text. Nothing to read aloud."


def read_ack(page: int) -> str:
    """The read-aloud ack, truthful page in words (grammar v1.7 row (32))."""
    return f"Reading page {number_words(page)}."


def explain_ack(page: int) -> str:
    """The explain row's tag — ONE smart call carries the page; the line says which."""
    return f"Page {number_words(page)}, at study depth:"


def due_ack(count: int) -> str:
    """Cards due, number truthful in words; the singular law holds (one CARD due)."""
    noun = "card" if count == 1 else "cards"
    return f"{number_words(count).capitalize()} {noun} due."


def pdf_range_line(pages: int) -> str:
    """A page out of the book's reach answers the honest table of contents, never a guess."""
    return f"That PDF has {number_words(pages)} pages. Pick one of them."


def flash_made_line(count: int) -> str:
    """The make-flashcards ack: drafted and filed, count in words, singular truthful."""
    noun = "card" if count == 1 else "cards"
    return f"{number_words(count).capitalize()} {noun} made and filed."


def quiz_question_line(index: int, total: int, question: str) -> str:
    """One question at a time — position truthful in words."""
    return f"Question {number_words(index)} of {number_words(total)}: {question}"


def quiz_score_line(right: int, total: int) -> str:
    """The grading closes with the honest caveat — key words, never fake rigor (§24)."""
    return (f"That's the set: {number_words(right)} of {number_words(total)} right. "
            f"{LINE_QUIZ_CAVEAT}")


def flash_front_line(index: int, total: int, front: str) -> str:
    """A due card shows its front only — the reveal is the student's own word."""
    return f"Card {number_words(index)} of {number_words(total)}: {front} — {LINE_FLASH_FRONT_TAIL}"


def flash_back_line(back: str) -> str:
    """The reveal — then the honest two-word grade choice."""
    return f"{back} — {LINE_FLASH_BACK_TAIL}"


def flash_grade_line(right: bool, box: int) -> str:
    """Leitner truth: right climbs a box, wrong returns to box one — named, never hidden."""
    if right:
        return f"Right. It climbs to box {number_words(box)}."
    return "Wrong. Back to box one."


def council_verdict_unanimous() -> str:
    """§23 verdict family, basis declared in council.py: agreement count first."""
    return "Verdict: unanimous — seats landed together. Trust it."


def council_verdict_majority(first: int, second: int) -> str:
    """Two seats agree — the pair is named by number, never a coin flip."""
    return f"Verdict: seats {number_words(first)} and {number_words(second)} agree — go with them."


def council_verdict_absent(seat: int, agreed: bool, lane: str) -> str:
    """A seat stood down (spent/failed): honesty in place, then the surviving law —
    pair-agrees -> trust it; split -> lane strength decides."""
    word = number_words(seat)
    if agreed:
        return f"Verdict: seat {word} couldn't make it; the two answering agree. Trust it."
    return council_verdict_split(lane)


def council_verdict_split(lane: str) -> str:
    """Full disagreement: the verdict weighs the strongest seat ON RECORD and says why."""
    return (f"Verdict: the seats split. I weight the {lane} lane — my strongest seat "
            "standing. Read each side above.")


def council_verdict_lone(seat: int) -> str:
    """A single survivor is NOT a consensus — one voice honestly labeled as one voice."""
    return f"Verdict: only seat {number_words(seat)} answered. One voice is one voice — weigh it so."


def council_verdict_none() -> str:
    """Every seat stood down — the honest empty bench, zero invented counsel."""
    return "Verdict: no seat answered. The ring is dry — ask me solo, or wait for midnight."
