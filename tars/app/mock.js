/* TARS Bridge app — the Mock bridge (contract v1.0 §6).
   Activates ONLY when a real window.tarsBridge is absent, so opening index.html in any
   browser gives a living demo with zero backend. Implements all nine bridge methods and
   plays the canon demo script on natural triggers:
     load                      -> boot line
     "humor 60"                -> "Humor adjusted to sixty percent."
     "honesty 50"              -> "Honesty is fixed at ninety."
     "status" / Status chip    -> LOCAL-hue gauges
     "search ..." -> 3 results -> "open the second"
     "explain ..."             -> cloud failure line, then the smart-lane answer
     "shutdown"                -> red-verb action gate -> cancel -> "Cancelled. Nothing changed."
     push-to-talk twice        -> Cooper's voice, then the unrecognized-voice guest line
     10 idle minutes           -> "Standing down." + close
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

  var keys = [
    { index: 0, lane: "fast", remainingPct: 94, state: "healthy" },
    { index: 1, lane: "fast", remainingPct: 88, state: "healthy" },
    { index: 2, lane: "smart", remainingPct: 71, state: "healthy" },
    { index: 3, lane: "smart", remainingPct: 46, state: "healthy" },
    { index: 4, lane: "eyes", remainingPct: 97, state: "healthy" },
    { index: 5, lane: "ears", remainingPct: 82, state: "healthy" },
    { index: 6, lane: "ultra", remainingPct: 18, state: "warn" },
    { index: 7, lane: "council", remainingPct: 62, state: "healthy" }
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
    store[chat.id].push({
      id: chat.id + "-m" + store[chat.id].length,
      who: who,
      text: text,
      ts: now(),
      hue: msgHue || null,
      lane: msgLane || null,
      actions: ["copy", "read_aloud", "redo"]
    });
    if (who === "tars") { chat.lastHue = msgHue || chat.lastHue; }
    chat.ts = now();
  }

  function speak(text, replyHue, replyLane, after) {
    var chat = ensureChat(null);
    setState("THINKING", replyHue, replyLane);
    var pieces = text.match(/\S+\s*/g) || [text];
    var groups = [];
    var buf = "";
    pieces.forEach(function (piece, i) {
      buf += piece;
      if ((i + 1) % 4 === 0) { groups.push(buf); buf = ""; }
    });
    if (buf) { groups.push(buf); }

    setState("SPEAKING", replyHue, replyLane);
    groups.forEach(function (g, i) {
      host.setTimeout(function () {
        emit({ type: "chunk", chatId: chat.id, seq: i, text: g });
      }, TICK * (i + 1));
    });
    host.setTimeout(function () {
      emit({ type: "done", chatId: chat.id, hue: replyHue, lane: replyLane });
      record("tars", text, replyHue, replyLane);
      setState("IDLE", replyHue, replyLane);
      if (typeof after === "function") { after(); }
    }, TICK * (groups.length + 1));
  }

  function spendKey(index, cost) {
    var key = keys[index];
    key.remainingPct = Math.max(0, key.remainingPct - cost);
    key.state = key.remainingPct === 0 ? "spent" : (key.remainingPct <= 20 ? "warn" : "healthy");
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

  /* ── the nine bridge methods ── */

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
        powerNote: null
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
        speak("Watching the screen. Say enough to stop. Frames go to the eyes lane, so the pill is ochre.", "cloud", "eyes");
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

  host.setTimeout(function () {
    ensureChat("First contact");
    setState("IDLE", "local", null);
    speak("TARS online. Honesty: ninety. Humor: " + words(dials.humor) + ". Vernacular: " + words(dials.vernacular) + ".", "local", null);
    armIdle();
  }, 120);

}(typeof window !== "undefined" ? window : globalThis));
