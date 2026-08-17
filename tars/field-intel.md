# 🕵️ TARS — Field Intel: The "tars" Repos on GitHub (scouted & vetted, Aug 10 2026)

Mission rule for all finds: **ideas are free, code needs a license.** Never List applies. Nothing here changes the Master Spec — this file is the evidence locker.

## The Scoreboard

| Repo | ★ | Pulse | Verdict | Take |
|---|---|---|---|---|
| [TARS-AI-Community/TARS-AI](https://github.com/TARS-AI-Community/TARS-AI) ← *the mothership* | **575** · 111 forks | ✅ Active (1,442 commits, Apr 2026) | ⭐ **THE find** | See "What to steal" below |
| [latishab/tars](https://github.com/latishab/tars) (fork of above) | 36 | ✅ Active (Mar 2026) | 🟡 Idea gold — **deep-reviewed** (Cooper's correction) | Distributed edition: Pi daemon + gRPC/WebRTC APIs + dashboard + apps model — architecture gold. **`tars-conversation-app` (STT→LLM→TTS pipeline) = the closest software cousin; P1–P2 study target.** Roboeyes animation refs · HUD screensaver elective (P4). LICENSE + LEGAL.md present ✔ |
| [agustinsacco/tars](https://github.com/agustinsacco/tars) | 4 | ✅ Active (347 commits, v1.44.0, Jul 2026) | 🟡 Architecture study | Extension registry pattern · self-healing health checks → **Watcher tier** · release discipline. TS/Docker world → read, don't port |
| [Manraj29/Tars](https://github.com/Manraj29/Tars) | 3 | ❌ Dead (8 commits, Feb 2025) | ⚪ Validation only | Confirms: wake-word loop, barge-in, error→back-to-listening recovery, voice+text in one app. Bonus intel: **Gemini free-tier API** exists as brain-lane option |
| [primantah/tars](https://github.com/primantah/tars) (earlier find) | 22 | ❌ Dead (3 commits, Nov 2024) | ⚪ Validation only | The 80-line soul-v0 prototype. Proved the loop; we superseded it |

## ⭐ TARS-AI-Community — why it's the motherlode
The famous physical recreation of movie-TARS (3D-printed, Raspberry Pi, walks). Hardware ≠ our mission, BUT it stockpiles exactly the hard parts of ours:

1. **`Static Version (no motors)/`** — a software-only TARS build. Closest living relative of our project. Study its structure at P1.
2. **`tools/wakeword-trainer/`** — wake-word training tooling, ONNX/LFS references → strong chance it holds a **trained "Hey TARS" wake model** or the recipe to mint one. Exactly what P3 needs (our Porcupine/openWakeWord slot).
3. **Persona craft** — their character system is *the* reference for canon-accurate TARS (dry wit, humor-setting behavior). Study for the P1 soul prompt. Our original: dials + honesty-90 → theirs is the benchmark to beat.
4. **External STT support** (recent commits) — validates our local-whisper / cloud-ear fallback design.
5. `DUAL-LICENSE.md` + `ATTRIBUTION.md` present ⇒ **before reusing ANY asset (esp. a wake model): read the dual license terms first. Attribution file copied into our credits regardless.**

## What to steal (idea-level, always legal)
- [ ] Wake model / training recipe — "Hey TARS" (P3 gate: license read first)
- [ ] Persona field-study → beat it in P1 soul prompt
- [ ] Roboeyes → our slab-state animation references (C-01 upgrade hook)
- [ ] AiO **screensaver HUD** elective → P4 (from latishab fork)
- [ ] Extension-registry + self-healing patterns → Watcher tier (from agustinsacco)
- [ ] Gemini free-tier = registered as *possible 7th ammo lane*; architecture unchanged

## Scout's next orders
The name *"tars"* on GitHub is now **fully mapped** — we own the terrain. Further scouting by name = diminishing returns. Hunt by component instead (keywords already issued: faster-whisper · openwakeword/porcupine · pywebview · groq · resemblyzer), or hand hunting to me. 🫡

*Filed by the Architect. Honesty: ninety.* 🛰️
