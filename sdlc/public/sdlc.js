// The agent SDLC page: theme, reveal, the drawn figures, and the template
// form. Plain JavaScript, no dependencies. Every animation starts when its
// figure scrolls into view and stops when it leaves. With reduced motion,
// each figure draws its final state once.

(() => {
  "use strict";

  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const NS = "http://www.w3.org/2000/svg";
  const $ = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));

  /** @param {string} tag @param {Record<string, string | number>} [attrs] @param {Element} [parent] */
  function svg(tag, attrs = {}, parent) {
    const el = document.createElementNS(NS, tag);
    for (const [k, v] of Object.entries(attrs)) el.setAttribute(k, String(v));
    if (parent) parent.appendChild(el);
    return el;
  }

  /** Run `start` while `el` is on screen and `stop` when it leaves. */
  function whileVisible(el, start, stop) {
    if (!("IntersectionObserver" in window)) return start();
    new IntersectionObserver((entries) => {
      for (const e of entries) (e.isIntersecting ? start : stop)();
    }, { threshold: 0.15 }).observe(el);
  }

  // Theme ------------------------------------------------------------------
  const toggle = $("[data-theme-toggle]");
  if (toggle) {
    toggle.addEventListener("click", () => {
      const root = document.documentElement;
      const now = root.dataset.theme || (matchMedia("(prefers-color-scheme: light)").matches ? "light" : "dark");
      const next = now === "light" ? "dark" : "light";
      root.dataset.theme = next;
      try { localStorage.setItem("sdlc-theme", next); } catch (e) { /* storage can be blocked */ }
    });
  }

  // Reveal on scroll ---------------------------------------------------------
  const reveals = $$(".reveal");
  if (reduce || !("IntersectionObserver" in window)) {
    reveals.forEach((el) => el.classList.add("in"));
  } else {
    const io = new IntersectionObserver((entries) => {
      for (const e of entries) if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); }
    }, { threshold: 0.12, rootMargin: "0px 0px -40px 0px" });
    reveals.forEach((el) => io.observe(el));
  }

  // Hero: the waiting clocks and the stack of changes -------------------------
  const clocks = $$("[data-wait]");
  const fmtWait = (s) => {
    const d = Math.floor(s / 86400), h = Math.floor((s % 86400) / 3600), m = Math.floor((s % 3600) / 60);
    return d > 0 ? `${d}d ${h}h ${String(m).padStart(2, "0")}m` : `${h}h ${String(m).padStart(2, "0")}m`;
  };
  clocks.forEach((c) => { c.textContent = fmtWait(Number(c.dataset.wait)); });
  const pile = $("[data-pile]");
  if (pile) for (let k = 0; k < 12; k++) {
    const sheet = document.createElement("i");
    sheet.style.bottom = `${k * 7}px`;
    sheet.style.left = `${(k % 3) * 3}px`;
    pile.appendChild(sheet);
  }
  if (clocks.length && !reduce) {
    let timer = 0;
    // Each real second adds one minute of waiting.
    whileVisible(clocks[0].closest(".queue"), () => {
      if (timer) return;
      timer = window.setInterval(() => {
        clocks.forEach((c) => { c.dataset.wait = String(Number(c.dataset.wait) + 60); c.textContent = fmtWait(Number(c.dataset.wait)); });
      }, 1000);
    }, () => { window.clearInterval(timer); timer = 0; });
  }

  // One week, 168 hours ------------------------------------------------------
  const week = $("[data-week-grid]");
  if (week) {
    const days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
    const cells = [];
    days.forEach((d, di) => {
      const label = document.createElement("span");
      label.className = "d";
      label.textContent = d;
      week.appendChild(label);
      for (let h = 0; h < 24; h++) {
        const cell = document.createElement("span");
        cell.className = "h";
        const work = di < 5 && h >= 9 && h < 17;
        cell.dataset.work = work ? "1" : "0";
        week.appendChild(cell);
        cells.push(cell);
      }
    });
    const spacer = document.createElement("span");
    week.appendChild(spacer);
    ["12 am", "6 am", "12 pm", "6 pm"].forEach((t) => {
      const s = document.createElement("span");
      s.className = "hours";
      s.textContent = t;
      week.appendChild(s);
    });
    const caption = $("[data-week-caption]");
    const show = (mode) => {
      $$("[data-week]").forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.week === mode)));
      cells.forEach((cell, i) => {
        const on = mode === "agent" || cell.dataset.work === "1";
        const apply = () => cell.classList.toggle("person", on);
        if (reduce) apply(); else window.setTimeout(apply, (i % 24) * 12 + Math.floor(i / 24) * 30);
      });
      if (caption) {
        caption.textContent = mode === "agent"
          ? "An agent can work all 168 hours."
          : "A 40-hour work week covers 40 of the 168 hours.";
      }
    };
    $$("[data-week]").forEach((b) => b.addEventListener("click", () => show(b.dataset.week)));
    show("person");
  }

  // Same agents, same day, two processes ------------------------------------
  const simEls = $$("[data-sim]");
  if (simEls.length) {
    const COLS = {
      old: ["Code", "Queue", "Human review", "Merges"],
      new: ["Code", "Checks", "Agent review", "Merges"],
    };
    const X0 = 92, WIDTHS = [190, 190, 190, 312], GAP = 6, LANE_Y = [44, 92, 140], BAR_Y = 218;
    const START = 8 * 60, DAY = 24 * 60;
    const xOf = (col) => X0 + WIDTHS.slice(0, col).reduce((a, w) => a + w + GAP, 0);
    const END = xOf(3) + WIDTHS[3];
    const tX = (min) => X0 + ((min - START) / DAY) * (END - X0);
    const dur = (a, n) => 35 + ((a * 7 + n * 13) % 16);

    function build(el, kind) {
      el.textContent = "";
      COLS[kind].forEach((c, i) => {
        svg("text", { x: xOf(i) + 6, y: 22, class: "col-label" }, el).textContent = c;
        svg("rect", { x: xOf(i), y: 32, width: WIDTHS[i], height: 150, rx: 8, class: "col" }, el);
      });
      const lanes = LANE_Y.map((y, a) => {
        svg("text", { x: 4, y: y + 24, class: "lane-label" }, el).textContent = `Agent ${a + 1}`;
        const g = svg("g", { transform: `translate(${xOf(0) + 8} ${y + 6})` }, el);
        const box = svg("rect", { width: WIDTHS[0] - 16, height: 28, rx: 6, class: "tok" }, g);
        const label = svg("text", { x: 12, y: 18.5, class: "tok-text" }, g);
        const done = svg("g", {}, el);
        return { y, g, box, label, done };
      });
      // The 24-hour bar, starting at 8 am.
      const bar = svg("g", {}, el);
      const band = (from, to, text) => {
        svg("rect", { x: tX(from), y: BAR_Y - 9, width: tX(to) - tX(from), height: 18, rx: 3, class: "band" }, bar);
        svg("text", { x: tX(from) + 8, y: BAR_Y + 4, class: "band-label" }, bar).textContent = text;
      };
      if (kind === "old") band(9 * 60, 17 * 60, "Reviewer hours");
      else band(START, START + DAY, "Agent and check hours");
      svg("rect", { x: X0, y: BAR_Y - 9, width: END - X0, height: 18, rx: 3, class: "clockbar" }, bar);
      [8, 12, 16, 20, 24, 28, 32].forEach((h) => {
        const hh = h % 24;
        const t = hh === 0 ? "12 am" : hh === 12 ? "12 pm" : hh < 12 ? `${hh} am` : `${hh - 12} pm`;
        svg("text", { x: tX(h * 60), y: BAR_Y + 28, class: "band-label", "text-anchor": h === 8 ? "start" : h === 32 ? "end" : "middle" }, bar).textContent = t;
      });
      if (kind === "new") {
        svg("line", { x1: tX(9 * 60), x2: tX(9 * 60), y1: BAR_Y - 16, y2: BAR_Y + 10, class: "now", "stroke-dasharray": "3 2" }, bar);
        svg("text", { x: tX(9 * 60) + 6, y: BAR_Y - 19, class: "band-label" }, bar).textContent = "Record read at 9 am";
      }
      const now = svg("line", { x1: X0, x2: X0, y1: BAR_Y - 13, y2: BAR_Y + 13, class: "now" }, el);
      const time = svg("text", { x: 4, y: BAR_Y + 5, class: "time" }, el);
      return { kind, lanes, now, time };
    }

    /** A fresh day for one process. */
    function state(kind) {
      return {
        kind,
        agents: [0, 1, 2].map((a) => ({ a, st: "write", until: START + 12 + a * 14, n: 0, since: 0, merged: 0 })),
        queue: [],
        reading: null,
      };
    }

    /** Move one process forward to minute `t`. */
    function step(s, t) {
      const h = (t / 60) % 24;
      for (const ag of s.agents) {
        if (ag.until > t) continue;
        if (s.kind === "old") {
          if (ag.st === "write") { ag.st = "queue"; ag.since = t; ag.until = Infinity; s.queue.push(ag); }
          else if (ag.st === "read") { ag.merged++; ag.n++; ag.st = "write"; ag.until = t + dur(ag.a, ag.n); s.reading = null; }
        } else {
          if (ag.st === "write") { ag.st = "check"; ag.until = t + 12; }
          else if (ag.st === "check") { ag.st = "review"; ag.until = t + 8; }
          else if (ag.st === "review") { ag.merged++; ag.n++; ag.st = "write"; ag.until = t + dur(ag.a, ag.n); }
        }
      }
      if (s.kind === "old" && !s.reading && s.queue.length && h >= 9 && h < 17) {
        const ag = s.queue.shift();
        ag.st = "read"; ag.until = t + 45; s.reading = ag;
      }
    }

    const COL_OF = { write: 0, queue: 1, read: 2, check: 1, review: 2 };
    const clock = (t) => {
      const m = Math.floor(t) % DAY, hh = Math.floor(m / 60), mm = m % 60;
      const h12 = hh % 12 === 0 ? 12 : hh % 12;
      return `${h12}:${String(mm).padStart(2, "0")} ${hh < 12 ? "am" : "pm"}`;
    };

    function draw(view, s, t) {
      s.agents.forEach((ag, i) => {
        const lane = view.lanes[i];
        const col = COL_OF[ag.st];
        lane.g.setAttribute("transform", `translate(${xOf(col) + 8} ${lane.y + 6})`);
        const waiting = ag.st === "queue";
        lane.box.classList.toggle("wait", waiting);
        lane.label.classList.toggle("wait", waiting);
        const text = {
          write: "Draft",
          queue: `Idle ${Math.floor((t - ag.since) / 60)}h ${String(Math.floor(t - ag.since) % 60).padStart(2, "0")}m`,
          read: "Human review",
          check: "Checks",
          review: "Agent review",
        }[ag.st];
        if (lane.label.textContent !== text) lane.label.textContent = text;
        while (lane.done.childNodes.length < ag.merged) {
          const k = lane.done.childNodes.length;
          svg("rect", {
            x: xOf(3) + 10 + (k % 36) * 8,
            y: lane.y + 8 + Math.floor(k / 36) * 9,
            width: 6, height: 6, rx: 1, class: "done",
          }, lane.done);
        }
      });
      const x = tX(Math.min(t, START + DAY));
      view.now.setAttribute("x1", x);
      view.now.setAttribute("x2", x);
      view.time.textContent = clock(t);
    }

    const views = simEls.map((el) => build(el, el.dataset.sim));
    let states = views.map((v) => state(v.kind));
    let t = START;
    let running = false, raf = 0, last = 0, hold = 0;
    const PER_SEC = 60; // simulated minutes per real second

    const reset = () => {
      states = views.map((v) => state(v.kind));
      views.forEach((v) => v.lanes.forEach((l) => { l.done.textContent = ""; }));
      t = START;
    };
    const advance = (to) => {
      for (let m = Math.floor(t) + 1; m <= Math.floor(to); m++) states.forEach((s) => step(s, m));
      t = to;
      views.forEach((v, i) => draw(v, states[i], t));
    };

    if (reduce) {
      advance(START + DAY);
    } else {
      const frame = (now) => {
        if (!running) return;
        const dt = last ? (now - last) / 1000 : 0;
        last = now;
        if (hold > 0) {
          hold -= dt;
          if (hold <= 0) reset();
        } else {
          const next = Math.min(t + dt * PER_SEC, START + DAY);
          advance(next);
          if (next >= START + DAY) hold = 3;
        }
        raf = requestAnimationFrame(frame);
      };
      const btn = $("[data-sim-toggle]");
      let paused = false;
      const start = () => { if (running || paused) return; running = true; last = 0; raf = requestAnimationFrame(frame); };
      const stop = () => { running = false; cancelAnimationFrame(raf); };
      advance(START);
      whileVisible(simEls[0].closest(".sim-grid"), start, stop);
      btn?.addEventListener("click", () => {
        paused = !paused;
        btn.textContent = paused ? "Play" : "Pause";
        if (paused) stop(); else start();
      });
    }
  }

  // The ten stages, as a loop ------------------------------------------------
  const loop = $("[data-loop]");
  if (loop) {
    const STAGES = ["Issue", "Triage", "Claim", "Build", "Check", "Review", "Merge", "Release", "Watch", "Learn"];
    const C = 280, R = 192;
    const at = (deg, r = R) => {
      const a = (deg * Math.PI) / 180;
      return [C + r * Math.cos(a), C + r * Math.sin(a)];
    };
    svg("circle", { cx: C, cy: C, r: R + 46, class: "ring-outer" }, loop);
    svg("circle", { cx: C, cy: C, r: R, class: "ring" }, loop);

    // People meet the loop at three points.
    const people = [
      { label: "Rules", x: 470, y: 44, to: 0 },
      { label: "Decisions", x: 470, y: 520, to: 5 },
      { label: "Record", x: 90, y: 44, to: 9 },
    ];
    for (const p of people) {
      const g = svg("g", { class: "person" }, loop);
      const [nx, ny] = at(-90 + p.to * 36);
      svg("line", { x1: p.x, y1: p.y, x2: nx, y2: ny }, g);
      svg("rect", { x: p.x - 50, y: p.y - 16, width: 100, height: 32, rx: 16 }, g);
      svg("text", { x: p.x, y: p.y + 4 }, g).textContent = p.label;
      svg("text", { x: p.x, y: p.y - 22, class: "who-label" }, g).textContent = "People";
    }

    svg("text", { x: C, y: C - 6, class: "center-big" }, loop).textContent = "168 hours";
    svg("text", { x: C, y: C + 20, class: "center-small" }, loop).textContent = "Agents run every stage";

    const nodes = STAGES.map((name, i) => {
      const [x, y] = at(-90 + i * 36);
      const g = svg("g", {
        class: "node", tabindex: 0, role: "link",
        "aria-label": `Stage ${i + 1}: ${name}`, transform: `translate(${x} ${y})`,
      }, loop);
      svg("rect", { x: -54, y: -19, width: 108, height: 38, rx: 10 }, g);
      svg("text", { x: -35, y: 4.5, class: "num" }, g).textContent = String(i + 1).padStart(2, "0");
      svg("text", { x: 11, y: 5.5 }, g).textContent = name;
      const go = () => {
        const card = document.getElementById(`stage-${name.toLowerCase()}`);
        if (!card) return;
        card.scrollIntoView({ behavior: reduce ? "auto" : "smooth", block: "center" });
        card.classList.add("flash");
        window.setTimeout(() => card.classList.remove("flash"), 1600);
      };
      g.addEventListener("click", go);
      g.addEventListener("keydown", (e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); go(); } });
      return g;
    });
    const pulse = svg("circle", { r: 6, class: "pulse" }, loop);

    const PERIOD = 14000;
    let raf = 0, t0 = 0;
    const paint = (deg) => {
      const [x, y] = at(deg);
      pulse.setAttribute("cx", x);
      pulse.setAttribute("cy", y);
      const rel = ((deg + 90) % 360 + 360) % 360;
      const idx = Math.floor((rel + 18) / 36) % 10;
      nodes.forEach((n, i) => n.classList.toggle("on", i === idx));
    };
    if (reduce) {
      paint(-90);
    } else {
      const frame = (now) => {
        if (!t0) t0 = now;
        paint(-90 + (((now - t0) % PERIOD) / PERIOD) * 360);
        raf = requestAnimationFrame(frame);
      };
      whileVisible(loop, () => { if (!raf) raf = requestAnimationFrame(frame); }, () => { cancelAnimationFrame(raf); raf = 0; });
    }
  }

  // Changes merged by hour of day --------------------------------------------
  const chart = $("[data-chart]");
  if (chart) {
    // Pacific time, pull requests merged September 1 to 29, 2026.
    const BY_HOUR = [63, 30, 17, 20, 22, 19, 14, 12, 15, 35, 34, 75, 50, 65, 68, 64, 45, 67, 69, 53, 54, 55, 51, 67];
    const L = 44, Rr = 990, T = 34, B = 250;
    const step = (Rr - L) / 24, bw = step * 0.64, max = 80;
    const y = (v) => B - (v / max) * (B - T);
    const hourLabel = (h) => (h === 0 ? "12 am" : h === 12 ? "12 pm" : h < 12 ? `${h} am` : `${h - 12} pm`);
    svg("rect", { x: L + 9 * step, y: T - 22, width: 9 * step, height: B - T + 22, class: "band" }, chart);
    svg("text", { x: L + 9 * step + 8, y: T - 8, class: "band-label" }, chart).textContent = "Work hours (9 am to 6 pm)";
    [0, 20, 40, 60, 80].forEach((v) => {
      svg("line", { x1: L, x2: Rr, y1: y(v), y2: y(v), class: "axis", "stroke-dasharray": v ? "2 4" : "" }, chart);
      svg("text", { x: L - 8, y: y(v) + 4, class: "tick", "text-anchor": "end" }, chart).textContent = String(v);
    });
    const bars = BY_HOUR.map((v, h) => {
      const g = svg("g", { class: "bar-g", tabindex: 0, "aria-label": `${hourLabel(h)}: ${v} changes merged` }, chart);
      const x = L + h * step + (step - bw) / 2;
      const rect = svg("rect", { x, y: B, width: bw, height: 0, rx: 2, class: "bar" }, g);
      const label = svg("text", { x: x + bw / 2, y: B - 6, class: "val", opacity: 0 }, g);
      label.textContent = String(v);
      if (h % 3 === 0) svg("text", { x: L + h * step + step / 2, y: B + 22, class: "tick", "text-anchor": "middle" }, chart).textContent = hourLabel(h);
      return { rect, label, v };
    });
    const tbody = $("[data-chart-table] tbody");
    if (tbody) BY_HOUR.forEach((v, h) => {
      const tr = document.createElement("tr");
      tr.innerHTML = `<td>${hourLabel(h)}</td><td>${v}</td>`;
      tbody.appendChild(tr);
    });
    const grow = (p) => bars.forEach(({ rect, label, v }, i) => {
      const k = Math.min(1, Math.max(0, p * 1.6 - i * 0.025));
      const e = 1 - Math.pow(1 - k, 3);
      rect.setAttribute("y", y(v * e));
      rect.setAttribute("height", B - y(v * e));
      label.setAttribute("y", y(v * e) - 6);
      label.setAttribute("opacity", k >= 1 ? 1 : 0);
    });
    if (reduce || !("IntersectionObserver" in window)) grow(1);
    else {
      let done = false;
      new IntersectionObserver((entries, obs) => {
        if (done || !entries.some((e) => e.isIntersecting)) return;
        done = true; obs.disconnect();
        const t0 = performance.now();
        const frame = (now) => { const p = (now - t0) / 1400; grow(p); if (p < 1.3) requestAnimationFrame(frame); else grow(2); };
        requestAnimationFrame(frame);
      }, { threshold: 0.3 }).observe(chart);
    }
  }

  // The template form --------------------------------------------------------
  const forms = $$("[data-make]");
  if (forms.length) {
    const params = new URLSearchParams(location.search);
    let gate = false;
    const setGate = (on) => {
      gate = on;
      forms.forEach((f) => {
        const box = $("[data-lead-fields]", f);
        if (box) box.hidden = !on;
        ["firstName", "lastName", "email"].forEach((n) => { const i = f.elements.namedItem(n); if (i) i.required = on; });
      });
    };
    fetch("/api/config", { cache: "no-store" })
      .then((r) => (r.ok ? r.json() : { gate: false }))
      .then((c) => setGate(Boolean(c.gate)))
      .catch(() => { /* the server still enforces the gate */ });

    forms.forEach((form) => {
      const company = form.elements.namedItem("company");
      if (params.get("company") && company) company.value = params.get("company");
      const fmt = params.get("format");
      if (fmt) { const r = form.querySelector(`input[name="format"][value="${CSS.escape(fmt)}"]`); if (r) r.checked = true; }

      const status = $("[data-status]", form);
      const gdocs = $("[data-gdocs]", form);
      const button = $("button[type=submit]", form);
      const say = (text, kind) => { if (status) { status.textContent = text; status.dataset.kind = kind || ""; } };

      form.addEventListener("submit", async (e) => {
        e.preventDefault();
        const data = new FormData(form);
        const chosen = String(data.get("format") || "docx");
        const body = new URLSearchParams();
        data.forEach((v, k) => body.append(k, String(v)));
        if (chosen === "gdoc") body.set("format", "docx");
        if (gdocs) gdocs.hidden = true;
        say("Making your file.");
        if (button) button.disabled = true;
        try {
          const res = await fetch("/api/template", { method: "POST", body });
          const type = res.headers.get("content-type") || "";
          if (!res.ok || type.includes("text/html")) {
            if (gate) setGate(true);
            say(gate ? "Add your name and work email, then try again." : "That did not work. Try again, or write to hello@oxagen.sh.", "error");
            return;
          }
          const blob = await res.blob();
          const cd = res.headers.get("content-disposition") || "";
          const name = (cd.match(/filename="([^"]+)"/) || [])[1] || "agent-sdlc";
          const url = URL.createObjectURL(blob);
          const a = document.createElement("a");
          a.href = url; a.download = name; document.body.appendChild(a); a.click(); a.remove();
          window.setTimeout(() => URL.revokeObjectURL(url), 30000);
          say(`Downloaded ${name}.`);
          if (chosen === "gdoc" && gdocs) gdocs.hidden = false;
        } catch (err) {
          // Fall back to a plain form post. The server answers with the file.
          form.submit();
        } finally {
          if (button) button.disabled = false;
        }
      });
    });
    if (params.get("company") && location.hash === "#template") {
      const first = forms[forms.length - 1].elements.namedItem("firstName");
      if (first) window.setTimeout(() => first.focus(), 400);
    }
  }
})();
