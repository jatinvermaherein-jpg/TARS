"""The enrollment wizard data flow — contract A3's `enroll_voice` + `list_members`.

Flow (bible §22 / contract A3): the wizard OPENS with the honest caveat, always —
convenience-grade ID, told plainly. 5 phrases x 3 quiet rounds of PCM are
embedded and averaged into one centroid voiceprint. Calibration is derived from
the enrollment itself and persisted to vault kv: threshold = min self-score -
CALIBRATION_MARGIN, band floor = threshold - BAND_WIDTH. The acceptance trio is
a law of the fixtures: Cooper-normal ACCEPTs, the declared cold drift lands
BORDERLINE (not reject), a stranger REJECTs.

Incoherent rounds (a cold throat, a noisy room mid-enrollment) fail honestly
with the §22 enrollment row and persist nothing. Passphrases are stored
hash+salt only. Embeddings never cross the bridge: list_members() emits exactly
{name, relationship, tier, enrolledOn} — keys asserted ABSENT, not just blanked.
"""
import hashlib
import secrets
from datetime import date

from tars.core import canon
from tars.core.voiceid import hash_passphrase, cosine

ENROLL_PHRASES = (
    "Hey TARS, report for duty.",
    "TARS, what is on my plate today?",
    "Humor sixty percent, vernacular thirty.",
    "Read the last answer aloud for me.",
    "Standing down, TARS.",
)
ENROLL_ROUNDS = 3
MIN_COHERENCE = 0.95      # every round must agree with the centroid at least this much
CALIBRATION_MARGIN = 0.02 # threshold sits just under the calmest enrolled sample
BAND_WIDTH = 0.12         # below threshold, this wide: the cold-day borderline band


def open_wizard() -> dict:
    """A3 enroll_voice with payload {}: the caveat is the FIRST line, always."""
    return {"ok": True, "opening": canon.LINE_ENROLL_CAVEAT,
            "phrases": list(ENROLL_PHRASES), "rounds": ENROLL_ROUNDS}


def enroll_member(store, scorer, vault, log, name: str, relationship: str, tier: str,
                  samples: list, passphrase: str = None) -> dict:
    """15 fixture rounds -> averaged voiceprint + calibrated threshold, persisted.
    Failures return the §22 enrollment-fail line and write nothing."""
    expected = len(ENROLL_PHRASES) * ENROLL_ROUNDS
    if len(samples) != expected:
        raise ValueError(f"enrollment needs exactly {expected} rounds")
    if tier not in ("cooper", "family", "guest"):
        raise ValueError("member tier must be cooper, family, or guest")
    vectors = [scorer.embed(sample) for sample in samples]
    dims = len(vectors[0])
    centroid = [sum(v[i] for v in vectors) / expected for i in range(dims)]
    norm = sum(c * c for c in centroid) ** 0.5 or 1.0
    centroid = [c / norm for c in centroid]
    self_scores = [cosine(v, centroid) for v in vectors]
    if min(self_scores) < MIN_COHERENCE:
        log.entry("enroll", note=f"incoherent rounds (min self-score {min(self_scores):.3f}) — enrollment refused")
        return {"ok": False, "line": canon.LINE_VOICEPRINT_UNCLEAR}
    threshold = round(min(self_scores) - CALIBRATION_MARGIN, 4)
    band_floor = round(threshold - BAND_WIDTH, 4)

    member = {
        "name": name,
        "relationship": relationship,
        "tier": tier,
        "embedding": centroid,
        "sampleHashes": [hashlib.sha256(sample).hexdigest() for sample in samples],
        "enrolledOn": date.today().isoformat(),
    }
    if passphrase is not None:
        salt = secrets.token_hex(16)
        member["passSalt"] = salt
        member["passHash"] = hash_passphrase(passphrase, salt)  # hash+salt only; the raw words never persist
    store.add(member)
    vault.kv_set("voiceid:threshold", f"{threshold:.4f}")
    vault.kv_set("voiceid:band_floor", f"{band_floor:.4f}")
    vault.kv_set("voiceid:fails", "0")
    vault.kv_set("voiceid:lock", "0")
    log.entry("enroll", note=f"member enrolled: {name} ({relationship}, {tier}); threshold {threshold:.4f}")
    return {"ok": True,
            "member": {"name": name, "relationship": relationship, "tier": tier, "enrolledOn": member["enrolledOn"]},
            "threshold": threshold, "bandFloor": band_floor}


def list_members(store) -> list:
    """A3 MemberFile[]: name, relationship, tier, enrolledOn — embeddings NEVER appear."""
    return [{"name": m["name"], "relationship": m["relationship"], "tier": m["tier"],
             "enrolledOn": m["enrolledOn"]} for m in store.members_full()]
