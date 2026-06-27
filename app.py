import streamlit as st
import fitz
import re
import io

st.set_page_config(
    page_title="Lunawat Gem Catalog",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body {
    font-family: 'Inter', sans-serif;
    background: #EDEEF2;
    min-height: 100vh;
}

/* Kill streamlit chrome */
#MainMenu, footer, header,
[data-testid="stDecoration"],
[data-testid="stToolbar"],
[data-testid="stSidebar"]          { display: none !important; }

[data-testid="stAppViewContainer"] { background: #EDEEF2; }
[data-testid="stMain"]             { background: #EDEEF2; }

.block-container {
    max-width: 100% !important;
    padding: 0 !important;
}

/* ── Outer page: center the card vertically + horizontally ── */
.outer {
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 40px 24px;
}

/* ── The floating card shell ── */
.shell {
    display: flex;
    width: 100%;
    max-width: 940px;
    min-height: 520px;
    border-radius: 20px;
    overflow: hidden;
    box-shadow: 0 8px 40px rgba(0,0,0,0.14);
}

/* ── Left dark panel ── */
.panel-left {
    width: 240px;
    min-width: 240px;
    background: #151C2C;
    padding: 40px 28px;
    display: flex;
    flex-direction: column;
}
.brand {
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.16em;
    color: #4B6084;
    text-transform: uppercase;
    margin-bottom: 20px;
}
.panel-title {
    font-size: 19px;
    font-weight: 700;
    color: #fff;
    line-height: 1.3;
    margin-bottom: 36px;
}
.steps { display: flex; flex-direction: column; gap: 0; }
.step-row {
    display: flex; align-items: center; gap: 12px;
    padding: 10px 0; position: relative;
}
.step-row:not(:last-child)::after {
    content: '';
    position: absolute;
    left: 9px; top: 34px;
    width: 2px; height: 20px;
    background: #243046;
}
.d-active {
    width:20px;height:20px;border-radius:50%;flex-shrink:0;
    background:#3B82F6;
    box-shadow:0 0 0 4px rgba(59,130,246,0.2);
}
.d-done {
    width:20px;height:20px;border-radius:50%;flex-shrink:0;
    background:transparent; border:2px solid #3B82F6;
}
.d-pending {
    width:20px;height:20px;border-radius:50%;flex-shrink:0;
    background:#1E2D45; border:2px solid #2E3D55;
}
.l-active { font-size:13px;font-weight:600;color:#fff; }
.l-done   { font-size:13px;font-weight:500;color:#4B7BCA; }
.l-pending{ font-size:13px;font-weight:400;color:#3A4F6A; }

/* ── Right white panel ── */
.panel-right {
    flex: 1;
    background: #fff;
    padding: 40px 40px 36px;
    display: flex;
    flex-direction: column;
    overflow-y: auto;
}
.pane-title {
    font-size: 20px; font-weight: 700; color: #0F172A;
    letter-spacing: -0.02em; margin-bottom: 4px;
}
.pane-sub {
    font-size: 13px; color: #94A3B8; margin-bottom: 28px;
}
.field-label {
    font-size: 11px; font-weight: 700; letter-spacing: 0.1em;
    color: #CBD5E1; text-transform: uppercase; margin-bottom: 8px;
}
.row-space { margin-bottom: 20px; }
.pill {
    display:inline-flex;align-items:center;gap:5px;
    background:#EFF6FF;color:#1D4ED8;
    font-size:11px;font-weight:600;
    padding:3px 10px;border-radius:999px;
}
.hrow {
    display:flex;justify-content:space-between;
    align-items:center;margin-bottom:10px;
}

/* ── Inputs & widgets ── */
[data-testid="stFileUploader"] {
    border: 1.5px solid #E2E8F0 !important;
    border-radius: 10px !important;
    background: #FAFBFC !important;
    padding: 4px 10px !important;
}
[data-testid="stFileUploader"] section { padding: 6px 0 !important; }

[data-testid="stMultiSelect"] > div > div {
    border: 1.5px solid #E2E8F0 !important;
    border-radius: 8px !important;
    font-size: 13px !important;
    min-height: 40px !important;
    background: #FAFBFC !important;
}
[data-testid="stMultiSelect"] > div > div:focus-within {
    border-color: #3B82F6 !important;
    box-shadow: 0 0 0 3px rgba(59,130,246,0.1) !important;
}

/* Primary button */
[data-testid="stButton"] > button {
    background: #2563EB !important;
    color: #fff !important;
    border: none !important;
    border-radius: 8px !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    height: 42px !important;
    width: 100% !important;
    letter-spacing: 0.01em !important;
    transition: background 0.15s !important;
}
[data-testid="stButton"] > button:hover { background: #1D4ED8 !important; }

/* Secondary (re-scan) */
.sec [data-testid="stButton"] > button {
    background: #F1F5F9 !important;
    color: #475569 !important;
    font-size: 12px !important;
}
.sec [data-testid="stButton"] > button:hover { background: #E2E8F0 !important; }

/* Download */
[data-testid="stDownloadButton"] > button {
    background: #059669 !important;
    color: #fff !important;
    border: none !important;
    border-radius: 8px !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    height: 42px !important;
    width: 100% !important;
}
[data-testid="stDownloadButton"] > button:hover { background: #047857 !important; }

[data-testid="stImage"] img {
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.09);
}
[data-testid="stAlert"] { border-radius: 8px !important; font-size: 13px !important; }
hr { border-color: #F1F5F9; margin: 18px 0; }

/* Divider between sections */
.divider { height:1px;background:#F1F5F9;margin:20px 0; }

/* Export note */
.exp-note { font-size:13px;color:#64748B;margin-bottom:16px;line-height:1.5; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# CORE LOGIC — UNCHANGED
# ══════════════════════════════════════════════════════════════════════════════
GRID_X      = 360
GRID_Y      = 277
RENDER_ZOOM = 2.5

if "gem_registry"  not in st.session_state: st.session_state.gem_registry  = {}
if "selected_snos" not in st.session_state: st.session_state.selected_snos = []

def _crop_and_render(page: fitz.Page, rect: fitz.Rect) -> bytes:
    mat = fitz.Matrix(RENDER_ZOOM, RENDER_ZOOM)
    pix = page.get_pixmap(matrix=mat, clip=rect)
    return pix.tobytes("jpg")

def _quadrant_rect(page: fitz.Page, text_bbox) -> fitz.Rect:
    pw, ph = page.rect.width, page.rect.height
    left   = text_bbox[0] < GRID_X
    top    = text_bbox[1] < GRID_Y
    if left  and top:      return fitz.Rect(0,      0,      GRID_X, GRID_Y)
    if not left and top:   return fitz.Rect(GRID_X, 0,      pw,     GRID_Y)
    if left  and not top:  return fitz.Rect(0,      GRID_Y, GRID_X, ph)
    return fitz.Rect(GRID_X, GRID_Y, pw, ph)

def _single_page_rect(page: fitz.Page, text_bbox) -> fitz.Rect:
    return page.rect

def scan_pdf(file_bytes: bytes) -> dict:
    registry = {}
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    for page_num in range(len(doc)):
        page      = doc[page_num]
        sno_lines = []
        for block in page.get_text("dict")["blocks"]:
            if block["type"] != 0: continue
            for line in block["lines"]:
                txt = "".join(s["text"] for s in line["spans"])
                m = re.search(r'S\.No[-\s]*(\d+)', txt, re.IGNORECASE)
                if m:
                    sno_lines.append((m.group(1), line["bbox"]))
        if not sno_lines: continue
        is_multi = len(sno_lines) > 1
        for s_no, bbox in sno_lines:
            rect           = _quadrant_rect(page, bbox) if is_multi else _single_page_rect(page, bbox)
            registry[s_no] = _crop_and_render(page, rect)
    doc.close()
    return registry


# ══════════════════════════════════════════════════════════════════════════════
# STEP STATE
# ══════════════════════════════════════════════════════════════════════════════
reg      = st.session_state.gem_registry
has_scan = bool(reg)
has_sel  = bool(st.session_state.selected_snos) and has_scan

def ss(i):
    if i == 0: return "done"   if has_scan  else "active"
    if i == 1:
        if has_sel:  return "done"
        if has_scan: return "active"
        return "pending"
    if i == 2: return "active" if has_sel else "pending"
    if i == 3: return "active" if has_sel else "pending"

steps = ["Upload", "Select S.No", "Preview", "Export PDF"]


# ══════════════════════════════════════════════════════════════════════════════
# BUILD SIDEBAR HTML
# ══════════════════════════════════════════════════════════════════════════════
rows_html = ""
for i, label in enumerate(steps):
    s = ss(i)
    dot = f"d-{s}"
    lbl = f"l-{s}"
    rows_html += f"""
      <div class="step-row">
        <div class="{dot}"></div>
        <span class="{lbl}">{label}</span>
      </div>"""

sidebar_html = f"""
<div class="panel-left">
  <div class="brand">Lunawat Gems</div>
  <div class="panel-title">Gem Catalog<br>Builder</div>
  <div class="steps">{rows_html}</div>
</div>"""


# ══════════════════════════════════════════════════════════════════════════════
# RENDER — outer wrapper opens in HTML, Streamlit widgets go inside st.columns
# Strategy: render shell via HTML, then use a single centered column for widgets
# ══════════════════════════════════════════════════════════════════════════════

# We inject the left panel as pure HTML alongside a Streamlit right panel.
# Use st.columns to place sidebar html | widget area side by side.

_, center, _ = st.columns([1, 5, 1])

with center:
    st.markdown(f"""
    <div style="display:flex;border-radius:20px;overflow:hidden;
                box-shadow:0 8px 40px rgba(0,0,0,0.14);
                min-height:520px;margin:40px 0 24px;">
      {sidebar_html}
      <div style="flex:1;background:#fff;padding:0;">
    """, unsafe_allow_html=True)

    # Right panel content lives inside a padded sub-column
    _, inner, _ = st.columns([1, 20, 1])
    with inner:
        st.markdown('<div style="padding:36px 8px 32px;">', unsafe_allow_html=True)

        # Title
        st.markdown("""
        <div style="font-size:10px;font-weight:700;letter-spacing:0.14em;
                    color:#3B82F6;text-transform:uppercase;margin-bottom:6px;">
          Catalog Builder
        </div>
        <div style="font-size:20px;font-weight:700;color:#0F172A;
                    letter-spacing:-0.02em;margin-bottom:4px;">
          Upload your PDF catalog
        </div>
        <div style="font-size:13px;color:#94A3B8;margin-bottom:24px;">
          Supports single-item and multi-item (4-up) layouts automatically.
        </div>
        """, unsafe_allow_html=True)

        # ── Upload section ────────────────────────────────────────────────────
        st.markdown('<div style="font-size:11px;font-weight:700;letter-spacing:0.1em;color:#CBD5E1;text-transform:uppercase;margin-bottom:8px;">Catalog File</div>', unsafe_allow_html=True)

        uploaded_file = st.file_uploader(
            "PDF", type=["pdf"], label_visibility="collapsed"
        )

        c1, c2 = st.columns([4, 1], gap="small")
        with c1:
            scan_btn = st.button("Scan Catalog", use_container_width=True)
        with c2:
            st.markdown('<div class="sec">', unsafe_allow_html=True)
            rescan_btn = st.button("🔄 Re-scan", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # ── Logic ─────────────────────────────────────────────────────────────
        if uploaded_file:
            file_bytes = uploaded_file.read()

            if rescan_btn:
                st.session_state.gem_registry  = {}
                st.session_state.selected_snos = []
                st.rerun()

            if scan_btn and file_bytes:
                with st.spinner("Scanning pages…"):
                    st.session_state.gem_registry = scan_pdf(file_bytes)
                st.rerun()

            if not st.session_state.gem_registry and file_bytes:
                with st.spinner("Scanning pages…"):
                    st.session_state.gem_registry = scan_pdf(file_bytes)
                st.rerun()

            reg = st.session_state.gem_registry

            if not reg:
                st.warning("No S.No entries detected in this PDF.")

            else:
                # ── Divider ───────────────────────────────────────────────────
                st.markdown('<div style="height:1px;background:#F1F5F9;margin:20px 0;"></div>', unsafe_allow_html=True)

                # ── Select section ────────────────────────────────────────────
                st.markdown(f"""
                <div style="display:flex;justify-content:space-between;
                            align-items:center;margin-bottom:10px;">
                  <div style="font-size:11px;font-weight:700;letter-spacing:0.1em;
                              color:#CBD5E1;text-transform:uppercase;">Select Serial Numbers</div>
                  <div class="pill">💎 {len(reg)} entries found</div>
                </div>""", unsafe_allow_html=True)

                selected = st.multiselect(
                    "snos",
                    options=sorted(reg.keys()),
                    default=[s for s in st.session_state.selected_snos if s in reg],
                    format_func=lambda x: f"S.No {x}",
                    placeholder="Type to search or click to select…",
                    label_visibility="collapsed",
                )
                st.session_state.selected_snos = selected

                # ── Preview section ───────────────────────────────────────────
                if selected:
                    st.markdown('<div style="height:1px;background:#F1F5F9;margin:20px 0;"></div>', unsafe_allow_html=True)
                    st.markdown(f"""
                    <div style="display:flex;justify-content:space-between;
                                align-items:center;margin-bottom:12px;">
                      <div style="font-size:11px;font-weight:700;letter-spacing:0.1em;
                                  color:#CBD5E1;text-transform:uppercase;">Preview</div>
                      <div class="pill">{len(selected)} selected</div>
                    </div>""", unsafe_allow_html=True)

                    for pair in [selected[i:i+2] for i in range(0, len(selected), 2)]:
                        cols = st.columns(len(pair), gap="small")
                        for col, sno in zip(cols, pair):
                            with col:
                                st.image(reg[sno], caption=f"S.No {sno}",
                                         use_container_width=True)

                    # ── Export section ────────────────────────────────────────
                    st.markdown('<div style="height:1px;background:#F1F5F9;margin:20px 0;"></div>', unsafe_allow_html=True)
                    st.markdown('<div style="font-size:11px;font-weight:700;letter-spacing:0.1em;color:#CBD5E1;text-transform:uppercase;margin-bottom:8px;">Export</div>', unsafe_allow_html=True)
                    st.markdown(
                        f'<p style="font-size:13px;color:#64748B;margin-bottom:14px;line-height:1.5;">'
                        f'Generate a PDF with <strong>{len(selected)}</strong> '
                        f'selected entr{"y" if len(selected)==1 else "ies"}, one per page.</p>',
                        unsafe_allow_html=True,
                    )

                    if st.button("📄 Generate Selection PDF", use_container_width=True):
                        with st.spinner("Building PDF…"):
                            out = fitz.open()
                            for sno in selected:
                                pg = out.new_page(width=595, height=842)
                                pg.insert_text(fitz.Point(40, 45),
                                               f"Lunawat Gems — S.No {sno}",
                                               fontsize=14, color=(0,0,0))
                                pg.insert_image(fitz.Rect(40,65,555,780),
                                                stream=reg[sno])
                            buf = io.BytesIO()
                            out.save(buf); buf.seek(0)

                        st.download_button(
                            "⬇️  Download Catalog PDF",
                            data=buf,
                            file_name="LGC_Selection_Catalog.pdf",
                            mime="application/pdf",
                            use_container_width=True,
                        )

        st.markdown('</div>', unsafe_allow_html=True)  # /inner padding

    st.markdown('</div></div>', unsafe_allow_html=True)  # /panel-right /shell
