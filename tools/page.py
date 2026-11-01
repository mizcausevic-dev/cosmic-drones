"""Catalog page for Cosmic Drones.

The lab fetches the real MIDI files and draws them. It is not a picture of a
different score. Playback in the lab is a browser synth of those notes. The
MP3 further down is a separate recorded reading of study 01 only.
"""

from __future__ import annotations

import json
from pathlib import Path

from tools.article import PARAGRAPHS, SUBTITLE, TAG_LINE, TITLE
from tools.statements import AUDITION, ON_PICTURE, PREVIEW_LINE, PROGRAM, PUBLICATION, WARNING


def _client_catalog(catalog: dict) -> dict:
    return {
        "studies": [
            {
                "id": study["id"],
                "title": study["title"],
                "bpm": study["bpm"],
                "bars": study["bars"],
                "collection": study["collection_name"],
                "tonic": study["tonal_reference"],
                "identity": study["identity"],
                "limitations": study["limitations"],
                "seed": study["seed"],
            }
            for study in catalog["studies"]
        ],
        "parts": [
            {
                "id": part["id"],
                "study_id": part["study_id"],
                "role": part["role"],
                "variation": part["variation"],
                "path": part["path"],
                "notes": part["notes"],
            }
            for part in catalog["parts"]
        ],
    }


def render_page(catalog: dict, report: dict, preview: dict, film: dict) -> str:
    payload = json.dumps(_client_catalog(catalog), separators=(",", ":"))
    duration = f"{preview['score_seconds']:.3f}"
    encoded = f"{preview['seconds_encoded']:.3f}"
    article = "".join(f"<p>{paragraph}</p>" for paragraph in PARAGRAPHS)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Cosmic Drones</title>
  <meta name="description" content="Eight slow drone studies in note-only MIDI. Pick a study, read the file as three lanes, and play those notes.">
  <link rel="icon" href="art/mark.svg" type="image/svg+xml">
  <style>
    :root {{
      color-scheme: dark;
      --bg: #07060f;
      --bg-2: #12101c;
      --ink: #f4efe6;
      --muted: #b7adbf;
      --line: rgba(244, 239, 230, 0.16);
      --gold: #f0d7a2;
      --violet: #a99bff;
      --ice: #8fd8ff;
      --serif: "Iowan Old Style", Palatino, Georgia, serif;
      --sans: "Avenir Next", "Segoe UI", system-ui, sans-serif;
      --mono: ui-monospace, Menlo, Consolas, monospace;
    }}
    * {{ box-sizing: border-box; }}
    html {{ scroll-behavior: smooth; }}
    body {{
      margin: 0;
      background:
        radial-gradient(900px 420px at 100% -10%, rgba(169, 155, 255, 0.18), transparent 60%),
        radial-gradient(700px 380px at -10% 20%, rgba(143, 216, 255, 0.08), transparent 55%),
        var(--bg);
      color: var(--ink);
      font-family: var(--sans);
      line-height: 1.5;
    }}
    a {{ color: var(--gold); }}
    img, video, audio, canvas {{ max-width: 100%; }}
    .skip {{ position: absolute; left: 12px; top: -40px; background: var(--gold); color: #1a140c; padding: 8px 12px; }}
    .skip:focus {{ top: 12px; z-index: 6; }}
    .top {{
      position: sticky; top: 0; z-index: 4;
      display: flex; justify-content: space-between; gap: 16px; align-items: center;
      padding: 14px 28px; background: rgba(7, 6, 15, 0.84);
      border-bottom: 1px solid var(--line); backdrop-filter: blur(12px);
    }}
    .mark {{ font-family: var(--serif); letter-spacing: 0.12em; text-transform: uppercase; text-decoration: none; color: var(--ink); font-size: 0.82rem; }}
    .top nav {{ display: flex; gap: 16px; flex-wrap: wrap; }}
    .top nav a {{ color: var(--muted); text-decoration: none; }}
    .hero {{ display: grid; grid-template-columns: 1.1fr 0.9fr; min-height: calc(100vh - 58px); border-bottom: 1px solid var(--line); }}
    .hero-copy {{ padding: 64px 40px 80px; display: flex; flex-direction: column; justify-content: flex-end; }}
    .kicker {{ font-family: var(--mono); letter-spacing: 0.14em; text-transform: uppercase; color: var(--ice); font-size: 0.75rem; }}
    h1 {{ font-family: var(--serif); font-weight: 500; font-size: clamp(3rem, 7vw, 6.4rem); line-height: 0.9; margin: 8px 0 16px; }}
    h2 {{ font-family: var(--serif); font-weight: 500; font-size: clamp(1.8rem, 3vw, 2.6rem); line-height: 1.05; margin: 0; }}
    .lede {{ font-size: 1.15rem; max-width: 40rem; color: var(--muted); }}
    .hero img {{ width: 100%; height: 100%; object-fit: cover; min-height: 420px; }}
    .btn {{
      border: 0; border-radius: 999px; padding: 10px 16px; background: var(--gold); color: #1a140c;
      font-weight: 650; cursor: pointer; text-decoration: none; display: inline-flex;
    }}
    .btn.ghost {{ background: transparent; color: var(--ink); border: 1px solid var(--line); }}
    .actions {{ display: flex; gap: 10px; flex-wrap: wrap; margin-top: 22px; }}
    section {{ padding: 28px; }}
    .section-head {{ margin-bottom: 16px; }}
    .rail {{ display: flex; gap: 10px; overflow-x: auto; padding-bottom: 8px; }}
    .study {{
      flex: 0 0 220px; text-align: left; border: 1px solid var(--line); background: rgba(18, 16, 28, 0.7);
      color: var(--ink); border-radius: 16px; padding: 14px; cursor: pointer;
    }}
    .study[aria-current="true"] {{ border-color: var(--gold); }}
    .study b {{ display: block; font-family: var(--serif); font-size: 1.25rem; font-weight: 500; }}
    .study span {{ color: var(--muted); font-family: var(--mono); font-size: 0.75rem; }}
    .lab {{
      margin: 0 28px 28px; display: grid; grid-template-columns: 280px 1fr; gap: 18px;
      background: rgba(18, 16, 28, 0.72); border: 1px solid var(--line); border-radius: 20px; padding: 18px;
    }}
    .meta {{ color: var(--muted); min-height: 4.5rem; }}
    canvas {{ width: 100%; height: auto; background: #0b0a12; border-radius: 12px; }}
    .switch {{ display: flex; gap: 8px; margin: 12px 0; }}
    .silence {{ display: grid; grid-template-columns: repeat(8, 1fr); gap: 8px; margin-top: 18px; }}
    .silence div {{ background: var(--bg-2); border-radius: 8px; padding: 8px; }}
    .silence i {{ display: block; height: 72px; background: linear-gradient(to top, var(--violet), transparent); border-radius: 4px; transform-origin: bottom; }}
    .reading {{ display: grid; grid-template-columns: 1.2fr 0.8fr; gap: 18px; align-items: start; }}
    video, audio {{ width: 100%; background: #000; }}
    .warn {{ border-left: 3px solid var(--gold); padding-left: 12px; }}
    .checks {{ display: flex; gap: 8px; flex-wrap: wrap; }}
    .checks span {{ border: 1px solid var(--line); border-radius: 999px; padding: 6px 10px; color: var(--muted); font-size: 0.85rem; }}
    .transport {{
      position: sticky; bottom: 0; display: flex; justify-content: space-between; gap: 12px; align-items: center;
      padding: 12px 28px; background: rgba(7, 6, 15, 0.92); border-top: 1px solid var(--line);
    }}
    footer {{ padding: 28px; color: var(--muted); }}
    @media (max-width: 860px) {{
      .hero, .lab, .reading {{ grid-template-columns: 1fr; }}
      .hero-copy {{ padding: 32px 20px; }}
      section {{ padding: 20px; }}
    }}
    @media (prefers-reduced-motion: reduce) {{
      html {{ scroll-behavior: auto; }}
    }}
  </style>
</head>
<body>
  <a class="skip" href="#lab">Skip to the lanes</a>
  <header class="top">
    <a class="mark" href="#top">Cosmic Drones</a>
    <nav>
      <a href="#studies">Studies</a>
      <a href="#lab">Lanes</a>
      <a href="#reading">Recorded reading</a>
      <a href="#article">Draft</a>
    </nav>
  </header>
  <main id="top">
    <section class="hero">
      <div class="hero-copy">
        <p class="kicker">Note-only MIDI · 50 to 75 BPM</p>
        <h1>Eight drones that mostly wait.</h1>
        <p class="lede">Foundation, harmonic field, and distant signals. Two variations each. The lanes below are the MIDI file you download, not a drawing of a different piece.</p>
        <div class="actions">
          <button class="btn" type="button" id="hero-play">Play this study</button>
          <a class="btn ghost" href="midi/arrangement.mid">Arrangement</a>
        </div>
      </div>
      <img src="art/hero.jpg" width="1280" height="720" alt="Illustration of slow arcs and a pale dust field. Not a photograph of a studio or of performers.">
    </section>
    <section id="studies">
      <div class="section-head">
        <p class="kicker">Eight rooms</p>
        <h2>Each study is a different way of staying still.</h2>
      </div>
      <div class="rail" id="rail"></div>
    </section>
    <section class="lab" id="lab">
      <div>
        <p class="kicker" id="study-id">s01</p>
        <h2 id="study-title">Common Tone</h2>
        <p class="meta" id="study-meta"></p>
        <div class="switch">
          <button class="btn" type="button" id="var-a">Variation A</button>
          <button class="btn ghost" type="button" id="var-b">Variation B</button>
        </div>
        <p id="study-identity"></p>
        <p id="study-limits"></p>
      </div>
      <div>
        <canvas id="roll" width="1100" height="360" aria-label="Three lanes drawn from the selected MIDI files"></canvas>
        <div class="silence" id="silence" aria-label="How much of each study is silent in the foundation"></div>
      </div>
    </section>
    <section id="reading">
      <div class="section-head">
        <p class="kicker">Recorded reading</p>
        <h2>One file, separate from the lab.</h2>
        <p>This MP3 is study 01, variation A, all {duration} score seconds. The encoded file is {encoded} seconds. {PREVIEW_LINE}. The picture reads “{ON_PICTURE}”.</p>
        <p>{film['duration_relation']}</p>
      </div>
      <div class="reading">
        <video controls preload="metadata" poster="film/poster.jpg" width="1280" height="720">
          <source src="film/preview.mp4" type="video/mp4">
          <track kind="captions" src="film/preview.vtt" srclang="en" label="English" default>
        </video>
        <div>
          <audio controls preload="metadata" src="preview/preview.mp3"></audio>
          <p><a href="preview/preview-manifest-Cursor.txt">Preview manifest</a></p>
          <p>{PROGRAM}</p>
          <p class="warn">{WARNING}</p>
          <p><a href="midi/validation-Cursor.json">Validation report</a> · result {report['result']}.</p>
          <p>{AUDITION}</p>
        </div>
      </div>
    </section>
    <section id="checks">
      <div class="section-head">
        <p class="kicker">What was checked</p>
        <h2>The bytes were opened again.</h2>
      </div>
      <div class="checks">
        <span>PPQ 960</span>
        <span>4/4 and encoded tempo</span>
        <span>foundation at most 2 notes</span>
        <span>field at most 8</span>
        <span>signals at most 3</span>
        <span>no program changes</span>
      </div>
    </section>
    <section id="article">
      <div class="section-head">
        <p class="kicker">Draft</p>
        <h2>{TITLE}</h2>
        <p>{SUBTITLE}</p>
        <p>{TAG_LINE}</p>
        <p><a href="articles/medium-draft-Cursor.md">Markdown</a> · <a href="articles/medium-paste-Cursor.txt">Plain text</a></p>
      </div>
      {article}
    </section>
  </main>
  <div class="transport">
    <div>
      <strong id="now-title">s01 Common Tone</strong>
      <div id="now-meta" class="meta"></div>
    </div>
    <button class="btn" type="button" id="play">Play</button>
  </div>
  <footer>
    <p>{PUBLICATION}</p>
    <p>{AUDITION}</p>
  </footer>
  <script id="catalog" type="application/json">{payload}</script>
  <script>
    const ROLES = [
      ["foundation", "Foundation", "#f0d7a2", 28, 60],
      ["harmonic-field", "Field", "#a99bff", 36, 84],
      ["distant-signal", "Signals", "#8fd8ff", 60, 96]
    ];
    const data = JSON.parse(document.getElementById("catalog").textContent);
    const state = {{ study: data.studies[0], variation: "a", notes: [], ppq: 960, uspq: 500000, playing: false, ctx: null, timers: [] }};

    function byId(id) {{ return document.getElementById(id); }}
    function partPath(study, role, variation) {{
      const found = data.parts.find((part) => part.study_id === study.id && part.role === role && part.variation === variation);
      if (!found) throw new Error("missing " + role);
      return found.path;
    }}
    function renderRail() {{
      byId("rail").innerHTML = data.studies.map((study) => `
        <button class="study" type="button" data-id="${{study.id}}" aria-current="${{study.id === state.study.id}}">
          <span>${{study.id}} · ${{study.bpm}} BPM</span>
          <b>${{study.title}}</b>
          <span>${{study.bars}} bars · ${{study.collection}}</span>
        </button>`).join("");
    }}
    function renderSilence() {{
      byId("silence").innerHTML = data.studies.map((study) => {{
        const parts = data.parts.filter((part) => part.study_id === study.id && part.role === "foundation" && part.variation === "a");
        const density = parts.length ? Math.min(100, parts[0].notes * 12) : 10;
        return `<div><i style="transform:scaleY(${{density / 100}})"></i><span>${{study.id}}</span></div>`;
      }}).join("");
    }}
    async function loadStudy(id, variation) {{
      state.study = data.studies.find((study) => study.id === id);
      state.variation = variation;
      byId("study-id").textContent = state.study.id;
      byId("study-title").textContent = state.study.title;
      byId("study-meta").textContent = `${{state.study.collection}} · tonic ${{state.study.tonic}} · ${{state.study.bpm}} BPM · ${{state.study.bars}} bars · seed ${{state.study.seed}}`;
      byId("study-identity").textContent = state.study.identity;
      byId("study-limits").textContent = state.study.limitations;
      byId("now-title").textContent = `${{state.study.id}} ${{state.study.title}}`;
      byId("now-meta").textContent = `Variation ${{variation.toUpperCase()}} · synthesized from the MIDI notes · J and K change study`;
      byId("var-a").className = variation === "a" ? "btn" : "btn ghost";
      byId("var-b").className = variation === "b" ? "btn" : "btn ghost";
      renderRail();
      const parsed = [];
      for (const role of ROLES) {{
        const response = await fetch(partPath(state.study, role[0], variation));
        if (!response.ok) throw new Error(role[0]);
        const midi = parseMidi(new Uint8Array(await response.arrayBuffer()));
        state.ppq = midi.ppq;
        state.uspq = midi.uspq;
        for (const note of midi.notes) parsed.push({{ ...note, role: role[0] }});
      }}
      state.notes = parsed;
      draw();
    }}
    function draw() {{
      const canvas = byId("roll");
      const ctx = canvas.getContext("2d");
      const width = canvas.width;
      const height = canvas.height;
      ctx.clearRect(0, 0, width, height);
      ctx.fillStyle = "#0b0a12";
      ctx.fillRect(0, 0, width, height);
      const label = 92;
      const lane = (height - 16) / ROLES.length;
      const end = state.study.bars * 3840;
      ROLES.forEach((role, index) => {{
        const y = 8 + index * lane;
        ctx.fillStyle = index % 2 ? "#12101b" : "#0e0d16";
        ctx.fillRect(label, y, width - label - 8, lane - 4);
        ctx.fillStyle = role[2];
        ctx.font = "13px Georgia, serif";
        ctx.fillText(role[1], 12, y + lane * 0.55);
      }});
      for (const note of state.notes) {{
        const index = ROLES.findIndex((role) => role[0] === note.role);
        const role = ROLES[index];
        const y0 = 8 + index * lane;
        const span = Math.max(1, role[4] - role[3]);
        const pitchY = y0 + 8 + (1 - (note.pitch - role[3]) / span) * (lane - 24);
        const x = label + (note.start / end) * (width - label - 12);
        const w = Math.max(2, (note.duration / end) * (width - label - 12));
        ctx.globalAlpha = 0.45 + (note.velocity / 127) * 0.55;
        ctx.fillStyle = role[2];
        ctx.fillRect(x, pitchY, w, 8);
      }}
      ctx.globalAlpha = 1;
    }}
    function stopNotes() {{
      state.playing = false;
      for (const timer of state.timers) clearTimeout(timer);
      state.timers = [];
      if (state.ctx) state.ctx.close().catch(() => {{}});
      state.ctx = null;
      byId("play").textContent = "Play";
    }}
    function playNotes() {{
      stopNotes();
      const ctx = new AudioContext();
      state.ctx = ctx;
      state.playing = true;
      byId("play").textContent = "Stop";
      const start = ctx.currentTime + 0.05;
      for (const note of state.notes) {{
        const when = start + (note.start / state.ppq) * (state.uspq / 1000000);
        const dur = Math.max(0.05, (note.duration / state.ppq) * (state.uspq / 1000000));
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = note.role === "harmonic-field" ? "triangle" : "sine";
        osc.frequency.value = 440 * Math.pow(2, (note.pitch - 69) / 12);
        const amp = (note.velocity / 127) * (note.role === "distant-signal" ? 0.05 : 0.08);
        gain.gain.setValueAtTime(0.0001, when);
        gain.gain.exponentialRampToValueAtTime(amp, when + Math.min(0.4, dur * 0.3));
        gain.gain.exponentialRampToValueAtTime(0.0001, when + dur);
        osc.connect(gain).connect(ctx.destination);
        osc.start(when);
        osc.stop(when + dur + 0.05);
      }}
      const total = (state.study.bars * 3840 / state.ppq) * (state.uspq / 1000000) * 1000 + 200;
      state.timers.push(setTimeout(stopNotes, total));
    }}
    function toggle() {{
      if (state.playing) stopNotes();
      else playNotes();
    }}
    function parseMidi(bytes) {{
      const view = new DataView(bytes.buffer, bytes.byteOffset, bytes.byteLength);
      let offset = 0;
      const text = (count) => {{ let out = ""; for (let i = 0; i < count; i += 1) out += String.fromCharCode(bytes[offset++]); return out; }};
      const readVar = () => {{
        let value = 0, byte = 0;
        do {{ byte = bytes[offset++]; value = (value << 7) | (byte & 0x7f); }} while (byte & 0x80);
        return value;
      }};
      if (text(4) !== "MThd") throw new Error("MIDI");
      offset += 4;
      offset += 2; offset += 2;
      const division = view.getUint16(offset); offset += 2;
      if (text(4) !== "MTrk") throw new Error("track");
      const length = view.getUint32(offset); offset += 4;
      const end = offset + length;
      let tick = 0, status = 0, uspq = 500000;
      const open = new Map();
      const notes = [];
      while (offset < end) {{
        tick += readVar();
        let byte = bytes[offset];
        if (byte === 0xff) {{
          offset += 1;
          const type = bytes[offset++];
          const size = readVar();
          if (type === 0x51 && size === 3) uspq = (bytes[offset] << 16) | (bytes[offset + 1] << 8) | bytes[offset + 2];
          offset += size;
          continue;
        }}
        if (byte & 0x80) {{ status = byte; offset += 1; }}
        const kind = status & 0xf0;
        const data1 = bytes[offset++];
        const data2 = kind === 0xc0 || kind === 0xd0 ? 0 : bytes[offset++];
        const key = String(data1);
        if (kind === 0x90 && data2 > 0) {{
          if (!open.has(key)) open.set(key, []);
          open.get(key).push({{ start: tick, velocity: data2 }});
        }} else if (kind === 0x80 || (kind === 0x90 && data2 === 0)) {{
          const stack = open.get(key) || [];
          if (stack.length) {{
            const on = stack.shift();
            notes.push({{ pitch: data1, start: on.start, duration: tick - on.start, velocity: on.velocity }});
          }}
        }}
      }}
      return {{ ppq: division, uspq, notes }};
    }}
    document.addEventListener("click", (event) => {{
      const button = event.target.closest(".study");
      if (button) loadStudy(button.dataset.id, state.variation);
    }});
    byId("var-a").addEventListener("click", () => loadStudy(state.study.id, "a"));
    byId("var-b").addEventListener("click", () => loadStudy(state.study.id, "b"));
    byId("play").addEventListener("click", toggle);
    byId("hero-play").addEventListener("click", () => {{ loadStudy(state.study.id, state.variation).then(toggle); }});
    document.addEventListener("keydown", (event) => {{
      if (event.target.matches("input, textarea")) return;
      if (event.code === "Space") {{ event.preventDefault(); toggle(); }}
      if (event.key === "j" || event.key === "k" || event.key === "J" || event.key === "K") {{
        const index = data.studies.findIndex((study) => study.id === state.study.id);
        const next = event.key.toLowerCase() === "j" ? index - 1 : index + 1;
        if (next >= 0 && next < data.studies.length) loadStudy(data.studies[next].id, state.variation);
      }}
    }});
    renderSilence();
    loadStudy("s01", "a");
  </script>
</body>
</html>
"""


def write_page(path: Path, catalog: dict, report: dict, preview: dict, film: dict) -> None:
    path.write_text(render_page(catalog, report, preview, film), encoding="utf-8")
    media = path.with_name("media.html")
    media.write_text(
        """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Cosmic Drones, stills</title>
<style>
body{margin:0;background:#07060f;color:#f4efe6;font-family:Georgia,serif}
main{width:min(1100px,calc(100% - 2rem));margin:2rem auto}
a{color:#f0d7a2} img,video,audio{width:100%;background:#000}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:1rem}
</style></head><body><main>
<p><a href="index.html">Back to the lanes</a></p>
<h1>Stills, film, and the recorded reading</h1>
<img src="art/hero.jpg" width="1280" height="720" alt="Slow arcs and pale dust. Not a photograph.">
<div class="grid">
<img src="art/square.jpg" width="1080" height="1080" alt="Square still of the same illustration.">
<img src="social/instagram-Cursor/portrait.jpg" width="1080" height="1350" alt="Vertical crop of the illustration.">
<img src="social/x-Cursor/card.jpg" width="1600" height="900" alt="Wide card of the illustration.">
<img src="film/poster.jpg" width="1280" height="720" alt="Film poster reading preview, not master.">
</div>
<audio controls src="preview/preview.mp3"></audio>
<video controls poster="film/poster.jpg" src="film/preview.mp4"></video>
</main></body></html>
""",
        encoding="utf-8",
    )
