# 📊 TARS — RAM Ledger (the full data)
**v1.0 · Aug 10, 2026 · Companion to Master Spec Law 4 (RAM Charter)**
**Honesty tags:** ⚪ = engineering estimate (component typicals) · will be replaced by **real Task-Manager readings on delivery day (P3 acceptance tests)**. No local LLM exists in TARS (Cooper decree) — that 3-4GB never enters this ledger.

## Table 1 — Per-component appetite
| Component | RAM while loaded | When it's loaded | Auto-unloads? |
|---|---|---|---|
| Sleeper service (hotkey listener + tray) | 60–90MB ⚪ | Always, after you start TARS once | Never (this IS the minimum) |
| Wake-word ear (Porcupine/openWakeWord) | 60–80MB ⚪ | Always when armed | No — ears must stay open |
| Face (pywebview + WebView2, static React bundle) | 80–150MB ⚪ | While window is summoned | Yes — drops to sleeper on stand-down/Esc |
| Brain/router process (Python, HTTP, gauges, logs) | 50–80MB ⚪ | Always when armed | No — but it's the lightest worker |
| **Ears: faster-whisper `small` int8** | **800MB–1,000MB ⚪** | Only while decoding speech (2–10s bursts) | **Yes — auto-drops after 5 idle min** (`medium` upgrade would add ~1GB more — that's why it's elective) |
| Voice-ID scoring (resemblyzer/ECAPA) | 200–400MB ⚪ | ~1 second after each "Hey TARS" | Yes — unloads right after scoring |
| Mouth: Piper TTS | 50–100MB ⚪ | While speaking | Idle-unloads with ears |
| Ledger/gauge/logger | 10–20MB ⚪ | Always | Writes, doesn't hold |

## Table 2 — System states (what "fully online" actually costs)
| State | What's running | Total RAM | On your 16GB |
|---|---|---|---|
| **OFF** | nothing | **0** | 16GB free |
| **Sleeper** (waiting for `Ctrl+Alt+T` / "Hey TARS") | sleeper + wake ear + brain | **~150–250MB** | ~1.5% — a fart in the wind |
| **Window open, idle** | + face, no speech | **~250–400MB** | ~2% |
| **Active conversation** (typical peak: ears decoding + ID + mouth + face) | everything above | **~1.2–1.6GB** | ~9% |
| **EVERYTHING MAX, WORST CASE** (whisper burst + voiceprint + speaking + face, all at once) | full stack, redlined | **~1.5–1.9GB** | ~11% |

## The bottom line
- **Fully online, worst case: ~2GB max. Typical talking peak: ~1.5GB. Watching-quietly: ~0.2GB.**
- Even at absolute maximum, TARS eats **less than one Chrome with 10 tabs**, and leaves ~14GB for Minecraft, Office, and whatever you're actually doing.
- The decree saved you more than TARS will ever spend: the cancelled local brain (3–4GB) is **2× TARS's own worst case.**
- Every part except the 250MB heartbeat **auto-unloads** — TARS diets between sentences, not just between sessions.

*Delivery day (P3) replaces every ⚪ with a real reading; any component breaching its row gets fixed or cut. The Charter has teeth.* 🛰️
