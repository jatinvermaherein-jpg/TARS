/* TARS Bridge app — the Mock bridge (contract v1.4 §6, incl. Amendments A1-A4).
   Activates ONLY when a real window.tarsBridge is absent, so opening index.html in any
   browser gives a living demo with zero backend. Implements all ten bridge methods and
   plays the canon demo script on natural triggers:
     load                      -> boot line
     "humor 60"                -> "Humor adjusted to sixty percent."
     "honesty 50"              -> "Honesty is fixed at ninety."
     "status" / Status chip    -> LOCAL-hue gauges
     "search ..." -> 3 results -> "open the second"
     "explain ..."             -> cloud failure line, then the smart-lane answer
     "shutdown"                -> red-verb action gate -> cancel -> "Cancelled. Nothing changed."
     push-to-talk twice        -> Cooper's voice, then the unrecognized-voice guest line
     read_aloud action         -> browser-native speechSynthesis (engine default voice;
                                  the real Piper voice belongs to CORE, P-CORE-3)
     redo action               -> a different canned reply for the same scene, streamed
                                  over the old one, hue and lane kept honest
     enroll_voice action       -> the §22 failure line, the honest demo path (real
                                  enrollment is CORE, P-CORE-4)
     10 idle minutes           -> "Standing down." + close
   Settings data (member files, the Living Brain tree, brain previews) has no contract
   channel yet, so it rides host.tarsMockPayloads as plain data — mock-side only, never
   a smuggled bridge method.
   Runs in a browser (window) and headless in Node (globalThis) — same code, same script. */

(function (host) {
  "use strict";

  if (host.tarsBridge) { return; }

  var ONES = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine",
    "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen",
    "eighteen", "nineteen"];
  var TENS = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"];

  function words(n) {
    if (n >= 100) { return "one hundred"; }
    if (n < 20) { return ONES[n]; }
    var t = TENS[Math.floor(n / 10)];
    var r = n % 10;
    return r === 0 ? t : t + "-" + ONES[r];
  }

  var IDLE_MS = (typeof host.TARS_MOCK_IDLE_MS === "number") ? host.TARS_MOCK_IDLE_MS : 600000;
  var TICK = (typeof host.TARS_MOCK_TICK_MS === "number") ? host.TARS_MOCK_TICK_MS : 55;

  var dials = { humor: 5, vernacular: 30, discretion: 95, trust: 25 };
  var state = "IDLE";
  var audience = "cooper";
  var hue = "local";
  var lane = null;
  var pttCount = 0;
  var actionSeq = 0;
  var chatSeq = 0;
  var idleTimer = null;

  /* Ring order is the rotation order: Groq #1-#6, then the OpenRouter pair (bible §26).
     state words match core/gauge.py exactly: spent at 0, warn at <=20, else ok. */
  var keys = [
    { index: 0, lane: "fast", remainingPct: 94, state: "ok" },
    { index: 1, lane: "fast", remainingPct: 88, state: "ok" },
    { index: 2, lane: "smart", remainingPct: 71, state: "ok" },
    { index: 3, lane: "smart", remainingPct: 46, state: "ok" },
    { index: 4, lane: "eyes", remainingPct: 97, state: "ok" },
    { index: 5, lane: "ears", remainingPct: 82, state: "ok" },
    { index: 6, lane: "ultra", remainingPct: 18, state: "warn" },
    { index: 7, lane: "council", remainingPct: 62, state: "ok" }
  ];

  /* Settings payloads (P-APP-2). These are NOT bridge methods: the contract has no
     channel for member files or the brain tree yet, so the mock hands them over as
     plain data on host.tarsMockPayloads and the app reads them defensively. Declared
     in the phase report as "needs contract note". */
  var members = [
    { name: "Cooper", relationship: "commander", tier: "COOPER", enrolledOn: "2026-08-14" },
    { name: "Bhaiya", relationship: "elder brother", tier: "FAMILY-STANDARD", enrolledOn: "2026-08-15" },
    { name: "Ma", relationship: "mother", tier: "FAMILY-STANDARD", enrolledOn: "2026-08-15" },
    { name: "unfiled voice", relationship: "no file", tier: "GUEST", enrolledOn: "never" }
  ];

  var brain = [
    { path: "people", kind: "dir", sizeKb: 44, modifiedDay: "2026-08-17" },
    { path: "people/cooper.md", kind: "file", sizeKb: 12, modifiedDay: "2026-08-17" },
    { path: "people/bhaiya.md", kind: "file", sizeKb: 18, modifiedDay: "2026-08-16" },
    { path: "people/ma.md", kind: "file", sizeKb: 14, modifiedDay: "2026-08-12" },
    { path: "journal", kind: "dir", sizeKb: 61, modifiedDay: "2026-08-17" },
    { path: "journal/2026-08-15.md", kind: "file", sizeKb: 22, modifiedDay: "2026-08-15" },
    { path: "journal/2026-08-16.md", kind: "file", sizeKb: 19, modifiedDay: "2026-08-16" },
    { path: "journal/2026-08-17.md", kind: "file", sizeKb: 20, modifiedDay: "2026-08-17" },
    { path: "lessons", kind: "dir", sizeKb: 17, modifiedDay: "2026-08-16" },
    { path: "lessons/never-guess-a-transcript.md", kind: "file", sizeKb: 9, modifiedDay: "2026-08-14" },
    { path: "lessons/ask-before-deleting.md", kind: "file", sizeKb: 8, modifiedDay: "2026-08-16" },
    { path: "plans", kind: "dir", sizeKb: 12, modifiedDay: "2026-08-17" },
    { path: "plans/result-day-reminder.md", kind: "file", sizeKb: 5, modifiedDay: "2026-08-17" },
    { path: "plans/physics-revision.md", kind: "file", sizeKb: 7, modifiedDay: "2026-08-13" }
  ];

  var brainText = {
    "people/cooper.md": "Commander. Builds late, tests before he trusts. Wants the honest number first and the comfort never. Asks for physics in plain words, then argues with the plain words.",
    "people/bhaiya.md": "Elder brother. Speaks fast when excited, slows down when it matters. Result day sits on his calendar and on mine. Prefers files over links.",
    "people/ma.md": "Mother. The worry-voice is a different voice; when I hear it I keep answers short and certain. No personal data spoken unless she is filed and cleared.",
    "journal/2026-08-15.md": "Cooper moved humor to sixty for an hour and moved it back. Search lane answered twice, ultra key untouched. I lost a transcript to room noise and said so instead of guessing.",
    "journal/2026-08-16.md": "Long session on projectile motion. Smart lane timed out once; the second key answered. Cooper asked for the letter about power cuts and kept the second draft.",
    "journal/2026-08-17.md": "Quiet morning. Watcher reported the disk unchanged. Consolidation folded two journal days into the people files and pruned a duplicate note.",
    "lessons/never-guess-a-transcript.md": "Heard a command at low confidence and nearly ran it. Rule written: below the hearing threshold I repeat the question, I do not guess. A wrong guess costs more than a second ask.",
    "lessons/ask-before-deleting.md": "Cooper said clear the folder and meant one file. Rule written: every red verb names its target back and waits for a typed YES.",
    "plans/result-day-reminder.md": "Remind Cooper the morning Bhaiya's result posts. Open loop until the date passes.",
    "plans/physics-revision.md": "Rotational motion next, then a quiz from the chapters already read aloud. Cooper asked for spaced repetition, not a lecture."
  };

  var enrollPhrases = [
    "TARS, are you awake?",
    "Open my physics notes.",
    "Honesty ninety, humor five.",
    "Send this to Bhaiya on Telegram.",
    "Stand down for now."
  ];

  var chats = [];
  var store = {};
  var current = null;

  function now() { return Date.now(); }

  function emit(detail) {
    if (typeof host.__tarsEvent !== "function") { return; }
    try { host.__tarsEvent(detail); } catch (err) { host.console.error(err); }
  }

  function notice() {
    return {
      type: "state",
      state: state,
      dials: { humor: dials.humor, vernacular: dials.vernacular, discretion: dials.discretion, trust: dials.trust },
      audience: audience,
      lane: lane,
      hue: hue
    };
  }

  function setState(next, nextHue, nextLane) {
    state = next;
    if (nextHue !== undefined) { hue = nextHue; }
    if (nextLane !== undefined) { lane = nextLane; }
    emit(notice());
  }

  function newChat(title) {
    chatSeq += 1;
    var chat = { id: "c" + chatSeq, title: title || "New chat", ts: now(), lastHue: null };
    chats.unshift(chat);
    store[chat.id] = [];
    current = chat;
    return chat;
  }

  function ensureChat(title) {
    if (!current) { newChat(title); }
    if (current.title === "New chat" && title) { current.title = title; }
    return current;
  }

  function record(who, text, msgHue, msgLane) {
    var chat = ensureChat(null);
    var id = chat.id + "-m" + store[chat.id].length;
    store[chat.id].push({
      id: id,
      who: who,
      text: text,
      ts: now(),
      hue: msgHue || null,
      lane: msgLane || null,
      actions: ["copy", "read_aloud", "redo"]
    });
    if (who === "tars") { chat.lastHue = msgHue || chat.lastHue; }
    chat.ts = now();
    return id;
  }

  function chunksOf(text) {
    var pieces = text.match(/\S+\s*/g) || [text];
    var groups = [];
    var buf = "";
    pieces.forEach(function (piece, i) {
      buf += piece;
      if ((i + 1) % 4 === 0) { groups.push(buf); buf = ""; }
    });
    if (buf) { groups.push(buf); }
    return groups;
  }

  function stream(chatId, text, replyHue, replyLane, onDone, after) {
    setState("THINKING", replyHue, replyLane);
    var groups = chunksOf(text);
    setState("SPEAKING", replyHue, replyLane);
    groups.forEach(function (g, i) {
      host.setTimeout(function () {
        emit({ type: "chunk", chatId: chatId, seq: i, text: g });
      }, TICK * (i + 1));
    });
    host.setTimeout(function () {
      /* A2: done carries messageId, so the message is filed first and the event
         reports the id it was filed under. */
      var messageId = (typeof onDone === "function") ? onDone() : null;
      emit({ type: "done", chatId: chatId, messageId: messageId, hue: replyHue, lane: replyLane });
      setState("IDLE", replyHue, replyLane);
      if (typeof after === "function") { after(); }
    }, TICK * (groups.length + 1));
  }

  function speak(text, replyHue, replyLane, after) {
    var chat = ensureChat(null);
    stream(chat.id, text, replyHue, replyLane, function () {
      return record("tars", text, replyHue, replyLane);
    }, after);
  }

  function spendKey(index, cost) {
    var key = keys[index];
    key.remainingPct = Math.max(0, key.remainingPct - cost);
    key.state = key.remainingPct === 0 ? "spent" : (key.remainingPct <= 20 ? "warn" : "ok");
    emit({ type: "gauge", keyIndex: key.index, lane: key.lane, remainingPct: key.remainingPct });
  }

  function armIdle() {
    if (idleTimer) { host.clearTimeout(idleTimer); }
    idleTimer = host.setTimeout(function () {
      speak("Standing down.", "local", null, function () {
        setState("OFF", "local", null);
        emit({ type: "close" });
      });
    }, IDLE_MS);
  }

  /* ── read aloud: browser-native voice only. The real Piper voice is CORE's, P-CORE-3. ── */

  var synth = (typeof host.speechSynthesis === "object") ? host.speechSynthesis : null;

  function readAloud(msg) {
    if (!synth || typeof host.SpeechSynthesisUtterance !== "function") {
      return { ok: false, line: "No speech engine in this browser." };
    }
    if (synth.speaking || synth.pending) {
      synth.cancel();
      setState("IDLE", hue, lane);
      return { ok: true, line: "Stopped." };
    }
    var utter = new host.SpeechSynthesisUtterance(msg.text);
    utter.rate = 1;
    utter.pitch = 1;
    utter.onend = function () { setState("IDLE", msg.hue || hue, msg.lane || lane); };
    setState("SPEAKING", msg.hue || hue, msg.lane || lane);
    synth.speak(utter);
    return { ok: true, line: "Reading aloud." };
  }

  /* ── redo: a genuinely different wording of the same scene, hue and lane unchanged ── */

  var ALTERNATES = [
    { match: /^Ready, Cooper\.$/, text: "Standing by, Cooper. Say the word." },
    {
      match: /^TARS online\./,
      text: "Systems up. Honesty holds at ninety, humor low, vernacular modest."
    },
    {
      match: /^Three results\./,
      text: "Same three hits, tighter: one, the latest Vines upload at eleven minutes. Two, a twenty-two minute interview clip. Three, an eight minute shorts compilation. Say open the second."
    },
    {
      match: /^Projectile motion/,
      text: "Try it this way: horizontal and vertical are separate problems. Sideways the speed never changes, downward gravity pulls at a steady rate, and the clock they share is the time of flight."
    },
    {
      match: /^Uptime four hours/,
      text: "Four hours and eleven minutes up. Seven keys comfortable, the ultra key thin at eighteen percent. Memory sits near three hundred megabytes against a two gigabyte ceiling, and the disk has plenty left."
    },
    {
      match: /^Opening result two\./,
      text: "Playing the second one now: the Ashish Chanchlani interview clip."
    },
    {
      match: /^Watching the screen\./,
      text: "Eyes on the screen. Say enough to stop. Frames travel to the eyes lane, which is why the pill reads amber."
    },
    {
      match: /^Three hundred twelve megabytes\./,
      text: "About three hundred megabytes in use. Nowhere near the ceiling."
    }
  ];

  function alternateFor(text) {
    var hit = null;
    ALTERNATES.forEach(function (alt) {
      if (!hit && alt.match.test(text)) { hit = alt.text; }
    });
    return hit || "Second pass, same answer in fewer words: " + text;
  }

  function redo(msg, chatId) {
    var next = alternateFor(msg.text);
    stream(chatId, next, msg.hue || null, msg.lane || null, function () {
      msg.text = next;
      msg.ts = now();
      return msg.id;
    });
    return { ok: true, chatId: chatId };
  }

  function findMessage(chatId, messageId) {
    var list = store[chatId] || [];
    var found = null;
    list.forEach(function (m) { if (m.id === messageId) { found = m; } });
    return found;
  }

  /* ── the demo script ── */

  function handle(text) {
    var t = text.trim();
    var low = t.toLowerCase();
    var m;

    m = low.match(/^honesty\s+(\d{1,3})$/);
    if (m) {
      speak("Honesty is fixed at ninety.", "local", null);
      return;
    }

    m = low.match(/^(humor|vernacular|discretion|trust)\s+(\d{1,3})$/);
    if (m) {
      var name = m[1];
      var value = Math.max(0, Math.min(100, parseInt(m[2], 10)));
      dials[name] = value;
      speak(name.charAt(0).toUpperCase() + name.slice(1) + " adjusted to " + words(value) + " percent.", "local", null);
      return;
    }

    if (low === "stand down" || low === "exit") {
      speak("Standing down.", "local", null, function () {
        setState("OFF", "local", null);
        emit({ type: "close" });
      });
      return;
    }

    if (low === "status" || low.indexOf("status") === 0) {
      speak("Uptime four hours eleven minutes. Eight keys healthy, ultra key at eighteen percent. RAM three hundred twelve megabytes of the two gigabyte ceiling. Vault six megabytes, disk two hundred nine gigabytes free.", "local", null);
      return;
    }

    if (/^(shutdown|restart|sleep|delete\b|close\b)/.test(low)) {
      actionSeq += 1;
      var target = low.split(/\s+/).slice(1).join(" ") || "this machine";
      var summary = /^(shutdown|restart|sleep)/.test(low)
        ? "Confirm: " + low.split(/\s+/)[0] + " in 30 seconds."
        : "That deletes " + target + ". Type YES to confirm.";
      emit({ type: "action", actionId: "a" + actionSeq, kind: "red-verb", summary: summary, target: target });
      return;
    }

    if (low.indexOf("search") === 0 || low.indexOf("search") > -1) {
      spendKey(0, 3);
      speak("Three results. One: Ashish Chanchlani Vines, latest upload, eleven minutes. Two: Ashish Chanchlani, interview clip, twenty-two minutes. Three: Ashish Chanchlani, shorts compilation, eight minutes. Say open the second to play it.", "cloud", "fast");
      return;
    }

    if (/open (the )?(second|2nd|two)/.test(low)) {
      speak("Opening result two. Ashish Chanchlani, interview clip.", "local", null);
      return;
    }

    if (low.indexOf("explain") > -1 || low.length > 120) {
      spendKey(2, 5);
      emit({ type: "error", code: "lane_timeout", line: "That brain didn't answer. Trying another key." });
      spendKey(3, 5);
      speak("Projectile motion is two independent motions at once: constant velocity along the horizontal, constant acceleration downward along the vertical. Split the launch velocity into components, solve each axis separately, and the time of flight is the bridge between them.", "cloud", "smart");
      return;
    }

    spendKey(1, 2);
    speak("Ready, Cooper.", "cloud", "fast");
  }

  /* ── the ten bridge methods ── */

  var api = {
    send: function (text) {
      armIdle();
      var chat = ensureChat(text.length > 34 ? text.slice(0, 34) : text);
      record("cooper", text, null, null);
      handle(text);
      return Promise.resolve({ chatId: chat.id });
    },

    get_state: function () {
      return Promise.resolve(notice());
    },

    set_dial: function (name, value) {
      armIdle();
      if (name === "honesty") {
        emit(notice());
        return Promise.resolve({ ok: false, line: "Honesty is fixed at ninety." });
      }
      if (!Object.prototype.hasOwnProperty.call(dials, name)) {
        return Promise.resolve({ ok: false, line: "Something went wrong. TARS is still here." });
      }
      dials[name] = Math.max(0, Math.min(100, value));
      emit(notice());
      return Promise.resolve({
        ok: true,
        line: name.charAt(0).toUpperCase() + name.slice(1) + " adjusted to " + words(dials[name]) + " percent."
      });
    },

    confirm: function (actionId, yes) {
      armIdle();
      if (!yes) {
        return Promise.resolve({ ok: false, line: "Cancelled. Nothing changed." });
      }
      return Promise.resolve({ ok: true, line: "Confirmed. " + actionId + " executing." });
    },

    voice_ptt: function (phase) {
      armIdle();
      if (phase === "start") {
        pttCount += 1;
        setState("LISTENING", "local", null);
        return Promise.resolve();
      }
      if (pttCount % 2 === 1) {
        audience = "cooper";
        emit({ type: "transcript", who: "cooper", text: "TARS, what is the RAM sitting at?" });
        speak("Three hundred twelve megabytes. Well under the ceiling.", "local", null);
      } else {
        audience = "guest";
        emit({ type: "transcript", who: "guest", text: "TARS, humor one hundred." });
        speak("Voice not recognized. Guest rules: formal mode, no personal access. How can I help?", "local", null);
      }
      return Promise.resolve();
    },

    get_status: function () {
      armIdle();
      setState("IDLE", "local", null);
      return Promise.resolve({
        keys: keys.map(function (k) { return { index: k.index, lane: k.lane, remainingPct: k.remainingPct, state: k.state }; }),
        ram: { mb: 312, ceiling: 2000 },
        storage: { vaultMb: 6, brainMb: 21, diskFreeGb: 209 },
        uptimeS: 15060,
        powerNote: null,
        windowsUpdate: "Up to date. Last checked today, 09:12."
      });
    },

    list_chats: function () {
      return Promise.resolve(chats.map(function (c) {
        return { id: c.id, title: c.title, ts: c.ts, lastHue: c.lastHue };
      }));
    },

    open_chat: function (id) {
      var found = chats.filter(function (c) { return c.id === id; })[0];
      if (found) { current = found; }
      return Promise.resolve((store[id] || []).slice());
    },

    new_chat: function () {
      var chat = newChat("New chat");
      armIdle();
      return Promise.resolve({ id: chat.id });
    },

    quick_action: function (name, payload) {
      armIdle();

      /* enroll_voice: the demo path only. Real enrollment is CORE P-CORE-4; the button
         proves the channel and the mock answers with the §22 failure line. */
      if (name === "enroll_voice") {
        var enrollChat = ensureChat("Voice enrollment");
        record("cooper", "run enrollment", null, null);
        speak("Voiceprint unclear. Quiet room, one more round.", "local", null);
        return Promise.resolve({ chatId: enrollChat.id });
      }

      if (name === "read_aloud" || name === "redo") {
        var target = (payload && payload.chatId) ? payload.chatId : (current ? current.id : null);
        var msg = target ? findMessage(target, payload && payload.messageId) : null;
        if (!msg) { return Promise.resolve({ ok: false, line: "That message is gone." }); }
        return Promise.resolve(name === "read_aloud" ? readAloud(msg) : redo(msg, target));
      }

      var scripted = {
        open: "open chrome",
        search: "search Ashish Chanchlani on YouTube",
        find_file: "find file physics notes",
        document: "document letter to the editor about power cuts",
        telesend: "telesend physics notes to Bhaiya",
        look: "look at my screen",
        status: "status",
        council: "council which laptop lasts longer"
      };
      var text = (payload && payload.text) ? payload.text : (scripted[name] || name);
      var chat = ensureChat(text);
      record("cooper", text, null, null);
      if (name === "status") {
        speak("Status report on the stage. Everything local.", "local", null);
      } else if (name === "look") {
        speak("Watching the screen. Say enough to stop. Frames go to the eyes lane, so the pill is amber.", "cloud", "eyes");
      } else if (name === "telesend") {
        actionSeq += 1;
        emit({
          type: "action", actionId: "a" + actionSeq, kind: "red-verb",
          summary: "TeleSend: physics-notes.pdf to Bhaiya on Telegram. Type YES to confirm.",
          target: "physics-notes.pdf"
        });
      } else if (name === "document") {
        speak("Drafting the letter, then writing a Word file to the Desktop.", "cloud", "smart");
      } else if (name === "council") {
        speak("Council convened. Two lanes answered, one abstained on quota.", "cloud", "council");
      } else {
        handle(text);
      }
      return Promise.resolve({ chatId: chat.id });
    }
  };

  host.tarsBridge = api;
  host.tarsBridgeIsMock = true;
  host.tarsMockPayloads = {
    members: members,
    brain: brain,
    brainText: brainText,
    enrollPhrases: enrollPhrases,
    enrollRounds: 3
  };

  host.setTimeout(function () {
    ensureChat("First contact");
    setState("IDLE", "local", null);
    speak("TARS online. Honesty: ninety. Humor: " + words(dials.humor) + ". Vernacular: " + words(dials.vernacular) + ".", "local", null);
    armIdle();
  }, 120);

}(typeof window !== "undefined" ? window : globalThis));
