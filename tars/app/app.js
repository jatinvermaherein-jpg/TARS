/* TARS Bridge app — renderer.
   Contract v1.0 §3-§5: CORE owns state, hue and lane; this file only renders what it is told,
   and calls window.tarsBridge methods (never invents one). */

(function () {
  "use strict";

  var ONES = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine",
    "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen",
    "eighteen", "nineteen"];
  var TENS = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"];

  function numToWords(n) {
    if (n >= 100) { return "one hundred"; }
    if (n < 20) { return ONES[n]; }
    var t = TENS[Math.floor(n / 10)];
    var r = n % 10;
    return r === 0 ? t : t + "-" + ONES[r];
  }

  function el(id) { return document.getElementById(id); }

  var shell = el("shell");
  var stateDot = el("state-dot");
  var stateLabel = el("state-label");
  var idChip = el("id-chip");
  var mockTag = el("mock-tag");
  var chatList = el("chat-list");
  var chatTitle = el("chat-title");
  var huePill = el("hue-pill");
  var laneTag = el("lane-tag");
  var transcript = el("transcript");
  var hero = el("hero");
  var heroNote = el("hero-note");
  var messages = el("messages");
  var voiceStrip = el("voice-strip");
  var voiceLabel = el("voice-label");
  var voiceBars = el("voice-bars");
  var input = el("composer-input");
  var attachInput = el("attach-input");
  var viewChat = el("view-chat");
  var viewSettings = el("view-settings");
  var closedScreen = el("closed-screen");
  var modalScrim = el("modal-scrim");
  var modalSummary = el("modal-summary");
  var modalTarget = el("modal-target");
  var modalInput = el("modal-input");
  var modalConfirm = el("modal-confirm");
  var dialNotice = el("dial-notice");

  var DIALS = ["honesty", "humor", "vernacular", "discretion", "trust"];

  var currentChatId = null;
  var openStream = null;      // {chatId, textNode, box}
  var lastCooperText = "";
  var pttActive = false;
  var lastGaugeCard = null;
  var pendingActionId = null;
  var settled = { honesty: 90, humor: 5, vernacular: 30, discretion: 95, trust: 25 };

  function bridge() {
    return (typeof window.tarsBridge === "object" && window.tarsBridge) ? window.tarsBridge : null;
  }

  function call(method, args) {
    var b = bridge();
    if (!b || typeof b[method] !== "function") { return Promise.resolve(null); }
    return Promise.resolve(b[method].apply(b, args || []));
  }

  /* ── state / hue / lane rendering (CORE-owned values) ── */

  function renderState(notice) {
    if (!notice) { return; }
    var s = String(notice.state || "IDLE").toUpperCase();
    shell.setAttribute("data-state", s);
    stateLabel.textContent = s;
    stateDot.title = s;

    var voiceOn = (s === "LISTENING" || s === "SPEAKING" || pttActive);
    voiceStrip.hidden = !voiceOn;
    if (voiceOn) {
      voiceLabel.textContent = (s === "SPEAKING") ? "SPEAKING" : "LISTENING";
      voiceStrip.classList.toggle("is-cloud", notice.hue === "cloud");
    }

    if (notice.hue) { renderHue(notice.hue); }
    renderLane(notice.lane);

    if (notice.audience) {
      var a = String(notice.audience).toUpperCase();
      idChip.textContent = a;
      idChip.classList.toggle("is-guest", notice.audience !== "cooper");
    }

    if (notice.dials) { renderDials(notice.dials); }
    if (s === "OFF") { renderClosed(); }
  }

  function renderHue(hue) {
    var cloud = (hue === "cloud");
    huePill.textContent = cloud ? "CLOUD" : "LOCAL";
    huePill.classList.toggle("is-cloud", cloud);
    huePill.title = cloud ? "Data may leave this machine" : "Nothing leaves this machine";
  }

  function renderLane(lane) {
    laneTag.textContent = lane ? "LANE " + String(lane).toUpperCase() : "LANE —";
  }

  function renderDials(d) {
    DIALS.forEach(function (name) {
      if (typeof d[name] !== "number") { return; }
      var slider = el("dial-" + name);
      var value = el("val-" + name);
      settled[name] = d[name];
      if (slider) { slider.value = String(d[name]); }
      if (value) { value.textContent = String(d[name]); }
    });
    var humor = (typeof d.humor === "number") ? d.humor : 5;
    var vern = (typeof d.vernacular === "number") ? d.vernacular : 30;
    heroNote.textContent = "TARS online. Honesty: ninety. Humor: " + numToWords(humor) +
      ". Vernacular: " + numToWords(vern) + ".";
  }

  function renderClosed() {
    closedScreen.hidden = false;
    voiceStrip.hidden = true;
    modalScrim.hidden = true;
  }

  /* ── transcript rendering ── */

  function scrollDown() { transcript.scrollTop = transcript.scrollHeight; }

  function showHero(show) { hero.hidden = !show; }

  function addCooper(text) {
    showHero(false);
    var box = document.createElement("div");
    box.className = "msg msg-cooper";
    box.textContent = text;
    messages.appendChild(box);
    scrollDown();
  }

  function addTranscriptLine(who, text) {
    showHero(false);
    var box = document.createElement("div");
    box.className = "msg-transcript";
    box.textContent = String(who).toUpperCase() + " heard: " + text;
    messages.appendChild(box);
    scrollDown();
  }

  function makeTarsBox(hue, lane) {
    showHero(false);
    var box = document.createElement("div");
    box.className = "msg msg-tars";
    if (hue) { box.classList.add("hue-" + hue); }
    var body = document.createElement("div");
    body.className = "msg-text";
    box.appendChild(body);
    var foot = document.createElement("div");
    foot.className = "msg-foot";
    var note = document.createElement("span");
    note.className = "lane-note";
    note.textContent = lane ? String(lane).toUpperCase() : "";
    foot.appendChild(note);
    box.appendChild(foot);
    messages.appendChild(box);
    scrollDown();
    return { box: box, body: body, foot: foot, note: note };
  }

  function addActionButtons(parts, text) {
    var copyBtn = document.createElement("button");
    copyBtn.type = "button";
    copyBtn.className = "msg-act";
    copyBtn.textContent = "copy";
    copyBtn.addEventListener("click", function () {
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).catch(function () { selectText(parts.body); });
      } else {
        selectText(parts.body);
      }
    });
    parts.foot.appendChild(copyBtn);

    var redoBtn = document.createElement("button");
    redoBtn.type = "button";
    redoBtn.className = "msg-act";
    redoBtn.textContent = "redo";
    redoBtn.addEventListener("click", function () {
      if (lastCooperText) { submit(lastCooperText); }
    });
    parts.foot.appendChild(redoBtn);
  }

  function selectText(node) {
    var range = document.createRange();
    range.selectNodeContents(node);
    var sel = window.getSelection();
    sel.removeAllRanges();
    sel.addRange(range);
  }

  function addErrorLine(line) {
    var parts = makeTarsBox(null, null);
    parts.box.classList.add("is-error");
    parts.body.textContent = line;
  }

  /* ── streaming ── */

  function onChunk(d) {
    if (!openStream || openStream.chatId !== d.chatId) {
      openStream = { chatId: d.chatId, parts: makeTarsBox(null, null), text: "" };
    }
    openStream.text += d.text;
    openStream.parts.body.textContent = openStream.text;
    scrollDown();
  }

  function onDone(d) {
    if (!openStream) { return; }
    var parts = openStream.parts;
    if (d.hue) { parts.box.classList.add("hue-" + d.hue); }
    if (d.lane) { parts.note.textContent = String(d.lane).toUpperCase(); }
    addActionButtons(parts, openStream.text);
    openStream = null;
    scrollDown();
  }

  /* ── gauges (Watcher StatusReport + live gauge deltas) ── */

  function renderStatus(report) {
    if (!report) { return; }
    showHero(false);
    var card = document.createElement("div");
    card.className = "gauge-card";

    var title = document.createElement("h3");
    title.textContent = "KEY RING · RAM · STORAGE";
    card.appendChild(title);

    (report.keys || []).forEach(function (k) {
      card.appendChild(gaugeRow("key " + k.index + " · " + k.lane, k.remainingPct, "%", k.index));
    });

    if (report.ram) {
      card.appendChild(gaugeRow("ram headroom", Math.round(100 - (report.ram.mb / report.ram.ceiling) * 100),
        report.ram.mb + " / " + report.ram.ceiling + "MB", null));
    }
    if (report.storage) {
      card.appendChild(plainRow("storage", "vault " + report.storage.vaultMb + "MB · brain " +
        report.storage.brainMb + "MB · free " + report.storage.diskFreeGb + "GB"));
    }
    card.appendChild(plainRow("uptime", String(report.uptimeS) + "s"));
    if (report.powerNote) { card.appendChild(plainRow("power", report.powerNote)); }

    messages.appendChild(card);
    lastGaugeCard = card;
    scrollDown();
  }

  function gaugeRow(name, pct, suffix, keyIndex) {
    var row = document.createElement("div");
    row.className = "gauge-row";
    if (keyIndex !== null && keyIndex !== undefined) { row.setAttribute("data-key", String(keyIndex)); }

    var label = document.createElement("span");
    label.className = "g-name";
    label.textContent = name;
    row.appendChild(label);

    var track = document.createElement("span");
    track.className = "gauge-track";
    var fill = document.createElement("span");
    fill.className = "gauge-fill";
    track.appendChild(fill);
    row.appendChild(track);

    var num = document.createElement("span");
    num.className = "g-num";
    row.appendChild(num);

    setGauge(row, pct, suffix);
    return row;
  }

  function setGauge(row, pct, suffix) {
    var clamped = Math.max(0, Math.min(100, pct));
    var fill = row.querySelector(".gauge-fill");
    fill.style.width = clamped + "%";
    fill.classList.toggle("is-warn", clamped <= 20 && clamped > 0);
    fill.classList.toggle("is-over", clamped === 0);
    row.querySelector(".g-num").textContent = (suffix === "%") ? clamped + "%" : suffix;
  }

  function plainRow(name, text) {
    var row = document.createElement("div");
    row.className = "gauge-row";
    var label = document.createElement("span");
    label.className = "g-name";
    label.textContent = name;
    var val = document.createElement("span");
    val.textContent = text;
    row.appendChild(label);
    row.appendChild(val);
    return row;
  }

  function onGauge(d) {
    if (!lastGaugeCard) { return; }
    var row = lastGaugeCard.querySelector('[data-key="' + d.keyIndex + '"]');
    if (!row) { return; }
    row.querySelector(".g-name").textContent = "key " + d.keyIndex + " · " + d.lane;
    setGauge(row, d.remainingPct, "%");
  }

  /* ── red-verb confirm modal ── */

  function openAction(req) {
    pendingActionId = req.actionId;
    modalSummary.textContent = req.summary;
    modalTarget.textContent = req.target ? "target: " + req.target : "";
    modalInput.value = "";
    modalConfirm.disabled = true;
    modalScrim.hidden = false;
    modalInput.focus();
  }

  function closeAction() {
    modalScrim.hidden = true;
    pendingActionId = null;
  }

  function answerAction(yes) {
    if (pendingActionId === null) { return; }
    var id = pendingActionId;
    closeAction();
    call("confirm", [id, yes]).then(function (res) {
      if (res && res.line) { addErrorLine(res.line); }
    });
  }

  /* ── conversations ── */

  function renderChatList(list) {
    chatList.textContent = "";
    (list || []).forEach(function (c) {
      var li = document.createElement("li");
      var btn = document.createElement("button");
      btn.type = "button";
      btn.className = "chat-item" + (c.id === currentChatId ? " is-on" : "");

      var hueDot = document.createElement("span");
      hueDot.className = "ci-hue" + (c.lastHue ? " hue-" + c.lastHue : "");
      btn.appendChild(hueDot);

      var title = document.createElement("span");
      title.className = "ci-title";
      title.textContent = c.title;
      btn.appendChild(title);

      btn.addEventListener("click", function () { loadChat(c.id, c.title); });
      li.appendChild(btn);
      chatList.appendChild(li);
    });
  }

  function loadChat(id, title) {
    currentChatId = id;
    chatTitle.textContent = title || "Conversation";
    call("open_chat", [id]).then(function (msgs) {
      messages.textContent = "";
      openStream = null;
      lastGaugeCard = null;
      showHero(!msgs || msgs.length === 0);
      (msgs || []).forEach(function (m) {
        if (m.who === "cooper") {
          addCooper(m.text);
          lastCooperText = m.text;
        } else {
          var parts = makeTarsBox(m.hue, m.lane);
          parts.body.textContent = m.text;
          addActionButtons(parts, m.text);
        }
      });
      refreshChatList();
      scrollDown();
    });
  }

  function refreshChatList() {
    call("list_chats", []).then(renderChatList);
  }

  function startNewChat() {
    call("new_chat", []).then(function (res) {
      currentChatId = res ? res.id : null;
      chatTitle.textContent = "New chat";
      messages.textContent = "";
      openStream = null;
      lastGaugeCard = null;
      showHero(true);
      refreshChatList();
    });
  }

  /* ── sending ── */

  function submit(text) {
    var clean = String(text).trim();
    if (!clean) { return; }
    lastCooperText = clean;
    addCooper(clean);
    call("send", [clean]).then(function (res) {
      if (res && res.chatId) { currentChatId = res.chatId; }
      refreshChatList();
    });
  }

  function runQuick(name) {
    call("quick_action", [name, null]).then(function (res) {
      if (res && res.chatId) { currentChatId = res.chatId; }
      if (name === "status") { call("get_status", []).then(renderStatus); }
      refreshChatList();
    });
  }

  /* ── dials panel ── */

  function showSettings(show) {
    viewSettings.hidden = !show;
    viewChat.hidden = show;
    if (show) { dialNotice.textContent = ""; }
  }

  function wireDial(name) {
    var slider = el("dial-" + name);
    var value = el("val-" + name);
    slider.addEventListener("input", function () {
      var next = parseInt(slider.value, 10);
      value.textContent = String(next);
      call("set_dial", [name, next]).then(function (res) {
        if (!res) { settled[name] = next; return; }
        dialNotice.textContent = res.line || "";
        dialNotice.classList.toggle("is-refusal", res.ok === false);
        if (res.ok === false) {
          slider.value = String(settled[name]);
          value.textContent = String(settled[name]);
        } else {
          settled[name] = next;
        }
      });
    });
  }

  /* ── push to talk ── */

  function ptt(on) {
    if (pttActive === on) { return; }
    pttActive = on;
    call("voice_ptt", [on ? "start" : "stop"]);
    if (on) {
      voiceStrip.hidden = false;
      voiceLabel.textContent = "LISTENING";
    }
  }

  /* ── wiring ── */

  function buildVoiceBars() {
    var heights = [7, 13, 19, 11, 16, 8, 14, 20, 10, 15, 6, 12];
    heights.forEach(function (h) {
      var bar = document.createElement("i");
      bar.style.height = h + "px";
      voiceBars.appendChild(bar);
    });
  }

  function autoGrow() {
    input.style.height = "auto";
    input.style.height = Math.min(input.scrollHeight, 132) + "px";
  }

  function wire() {
    buildVoiceBars();

    el("collapse-btn").addEventListener("click", function () {
      shell.classList.toggle("is-collapsed");
    });

    el("new-chat-btn").addEventListener("click", startNewChat);
    el("settings-btn").addEventListener("click", function () { showSettings(true); });
    el("settings-back").addEventListener("click", function () { showSettings(false); });

    Array.prototype.forEach.call(document.querySelectorAll("[data-quick]"), function (btn) {
      btn.addEventListener("click", function () {
        showSettings(false);
        runQuick(btn.getAttribute("data-quick"));
      });
    });

    Array.prototype.forEach.call(document.querySelectorAll(".chip"), function (chip) {
      chip.addEventListener("click", function () {
        input.value = chip.getAttribute("data-fill");
        input.focus();
        autoGrow();
      });
    });

    Array.prototype.forEach.call(document.querySelectorAll(".preset"), function (btn) {
      btn.addEventListener("click", function () {
        var humor = parseInt(btn.getAttribute("data-humor"), 10);
        var vern = parseInt(btn.getAttribute("data-vernacular"), 10);
        call("set_dial", ["humor", humor]).then(function () {
          return call("set_dial", ["vernacular", vern]);
        }).then(function (res) {
          if (res) {
            dialNotice.textContent = res.line || "";
            dialNotice.classList.remove("is-refusal");
          }
          return call("get_state", []);
        }).then(renderState);
      });
    });

    DIALS.forEach(wireDial);

    el("send-btn").addEventListener("click", function () {
      submit(input.value);
      input.value = "";
      autoGrow();
    });

    input.addEventListener("input", autoGrow);
    input.addEventListener("keydown", function (ev) {
      if (ev.key === "Enter" && !ev.shiftKey) {
        ev.preventDefault();
        submit(input.value);
        input.value = "";
        autoGrow();
      }
    });

    el("attach-btn").addEventListener("click", function () { attachInput.click(); });
    attachInput.addEventListener("change", function () {
      if (!attachInput.files.length) { return; }
      submit("attach " + attachInput.files[0].name);
      attachInput.value = "";
    });

    ["mic-btn", "head-mic-btn"].forEach(function (id) {
      var btn = el(id);
      btn.addEventListener("pointerdown", function () { ptt(true); });
      btn.addEventListener("pointerup", function () { ptt(false); });
      btn.addEventListener("pointerleave", function () { if (pttActive) { ptt(false); } });
    });

    modalInput.addEventListener("input", function () {
      modalConfirm.disabled = (modalInput.value.trim().toUpperCase() !== "YES");
    });
    modalConfirm.addEventListener("click", function () { answerAction(true); });
    el("modal-cancel").addEventListener("click", function () { answerAction(false); });

    document.addEventListener("keydown", function (ev) {
      if (ev.key !== "Escape") { return; }
      if (!modalScrim.hidden) { answerAction(false); return; }
      if (!viewSettings.hidden) { showSettings(false); return; }
      submit("stand down");
    });
  }

  /* ── the event port CORE calls ── */

  window.__tarsEvent = function (detail) {
    if (!detail || !detail.type) { return; }
    switch (detail.type) {
      case "state": renderState(detail); break;
      case "chunk": onChunk(detail); break;
      case "done": onDone(detail); break;
      case "action": openAction(detail); break;
      case "transcript": addTranscriptLine(detail.who, detail.text); break;
      case "gauge": onGauge(detail); break;
      case "error": addErrorLine(detail.line); break;
      case "close": renderClosed(); break;
      default: break;
    }
  };

  function boot() {
    wire();
    mockTag.hidden = !window.tarsBridgeIsMock;
    call("get_state", []).then(renderState);
    refreshChatList();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
}());
