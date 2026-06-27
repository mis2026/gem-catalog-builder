import streamlit as st
import fitz
import re
import io

st.set_page_config(
    page_title="Lunawat Gem Catalog",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
    font-family: 'Inter', sans-serif;
    background: #E8EAF0 !important;
    min-height: 100vh;
}

#MainMenu, footer, header,
[data-testid="stDecoration"],
[data-testid="stToolbar"],
[data-testid="stSidebar"] { display: none !important; }

/* Centered layout */
.block-container {
    max-width: 900px !important;
    padding: 48px 16px !important;
}

/* ════════════════════════════════════
   THE CARD — row flex, sidebar + form
   ════════════════════════════════════ */
.card-shell {
    display: flex;
    border-radius: 18px;
    overflow: hidden;
    box-shadow: 0 4px 32px rgba(0,0,0,0.13);
    min-height: 480px;
}

/* LEFT dark sidebar */
.sidebar {
    width: 220px;
    min-width: 220px;
    background: #151C2C;
    padding: 36px 24px;
    display: flex;
    flex-direction: column;
}
.brand {
    font-size: 9px; font-weight: 700; letter-spacing: 0.18em;
    color: #3D5070; text-transform: uppercase; margin-bottom: 18px;
}
.sidebar-title {
    font-size: 17px; font-weight: 700; color: #fff;
    line-height: 1.3; margin-bottom: 32px;
}
.step { display:flex; align-items:center; gap:11px; padding:9px 0; position:relative; }
.step:not(:last-child)::after {
    content:''; position:absolute; left:9px; top:32px;
    width:2px; height:18px; background:#1E2D45;
}
.da { width:19px;height:19px;border-radius:50%;flex-shrink:0;
      background:#3B82F6;box-shadow:0 0 0 4px rgba(59,130,246,.18); }
.dd { width:19px;height:19px;border-radius:50%;flex-shrink:0;
      background:transparent;border:2px solid #3B82F6; }
.dp { width:19px;height:19px;border-radius:50%;flex-shrink:0;
      background:#1C2B40;border:2px solid #2A3D57; }
.la { font-size:12px;font-weight:600;color:#fff; }
.ld { font-size:12px;font-weight:500;color:#4B7BCA; }
.lp { font-size:12px;font-weight:400;color:#344A63; }

/* RIGHT white form area */
.form-area {
    flex: 1;
    background: #fff;
    padding: 36px 36px 32px;
    display: flex;
    flex-direction: column;
    min-width: 0;
}
.eyebrow {
    font-size:9px;font-weight:700;letter-spacing:0.16em;
    color:#3B82F6;text-transform:uppercase;margin-bottom:5px;
}
.form-title {
    font-size:19px;font-weight:700;color:#0F172A;
    letter-spacing:-0.02em;margin-bottom:3px;
}
.form-sub { font-size:12px;color:#94A3B8;margin-bottom:22px; }
.lbl {
    font-size:9px;font-weight:700;letter-spacing:0.12em;
    color:#C0CCDA;text-transform:uppercase;margin-bottom:7px;
}
.divline { height:1px;background:#F1F5F9;margin:18px 0; }
.hrow { display:flex;justify-content:space-between;align-items:center;margin-bottom:9px; }
.pill {
    display:inline-flex;align-items:center;gap:4px;
    background:#EFF6FF;color:#1D4ED8;
    font-size:10px;font-weight:600;
    padding:3px 9px;border-radius:999px;
}

/* ── Streamlit widget overrides ── */
[data-testid="stFileUploader"] {
    border: 1.5px solid #E2E8F0 !important;
    border-radius: 9px !important;
    background: #FAFBFC !important;
    padding: 2px 8px !important;
    margin-bottom: 12px !important;
}
[data-testid="stFileUploader"] section { padding:4px 0 !important; }

[data-testid="stMultiSelect"] > div > div {
    border: 1.5px solid #E2E8F0 !important;
    border-radius: 8px !important;
    font-size: 13px !important;
    min-height: 40px !important;
    background: #FAFBFC !important;
}
[data-testid="stMultiSelect"] > div > div:focus-within {
    border-color: #3B82F6 !important;
    box-shadow: 0 0 0 3px rgba(59,130,246,.1) !important;
}

[data-testid="stButton"] > button {
    background: #2563EB !important;
    color: #fff !important;
    border: none !important;
    border-radius: 8px !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    height: 40px !important;
    width: 100% !important;
    transition: background .15s !important;
}
[data-testid="stButton"] > button:hover { background:#1D4ED8 !important; }

.sec [data-testid="stButton"] > button {
    background: #F1F5F9 !important;
    color: #475569 !important;
    font-size: 12px !important;
}
.sec [data-testid="stButton"] > button:hover { background:#E2E8F0 !important; }

[data-testid="stDownloadButton"] > button {
    background: #059669 !important; color:#fff !important;
    border:none !important; border-radius:8px !important;
    font-size:13px !important; font-weight:600 !important;
    height:40px !important; width:100% !important;
}
[data-testid="stDownloadButton"] > button:hover { background:#047857 !important; }

[data-testid="stImage"] img { border-radius:7px; box-shadow:0 2px 8px rgba(0,0,0,.09); }
[data-testid="stAlert"] { border-radius:8px !important; font-size:13px !important; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# UNCHANGED CORE LOGIC
# ══════════════════════════════════════════════════════════════════════════════
GRID_X      = 360
GRID_Y      = 277
RENDER_ZOOM = 2.5

if "gem_registry"  not in st.session_state: st.session_state.gem_registry  = {}
if "selected_snos" not in st.session_state: st.session_state.selected_snos = []

def _crop_and_render(page, rect):
    pix = page.get_pixmap(matrix=fitz.Matrix(RENDER_ZOOM, RENDER_ZOOM), clip=rect)
    return pix.tobytes("jpg")

def _quadrant_rect(page, bbox):
    pw, ph = page.rect.width, page.rect.height
    l, t   = bbox[0] < GRID_X, bbox[1] < GRID_Y
    if l  and t:  return fitz.Rect(0,      0,      GRID_X, GRID_Y)
    if not l and t: return fitz.Rect(GRID_X, 0,    pw,     GRID_Y)
    if l  and not t: return fitz.Rect(0,    GRID_Y, GRID_X, ph)
    return fitz.Rect(GRID_X, GRID_Y, pw, ph)

def _single_page_rect(page, bbox):
    return page.rect

def scan_pdf(file_bytes):
    registry, doc = {}, fitz.open(stream=file_bytes, filetype="pdf")
    for pn in range(len(doc)):
        page, lines = doc[pn], []
        for block in page.get_text("dict")["blocks"]:
            if block["type"] != 0: continue
            for line in block["lines"]:
                txt = "".join(s["text"] for s in line["spans"])
                m = re.search(r'S\.No[-\s]*(\d+)', txt, re.IGNORECASE)
                if m: lines.append((m.group(1), line["bbox"]))
        if not lines: continue
        multi = len(lines) > 1
        for sno, bbox in lines:
            registry[sno] = _crop_and_render(
                page, _quadrant_rect(page, bbox) if multi else _single_page_rect(page, bbox)
            )
    doc.close()
    return registry


# ══════════════════════════════════════════════════════════════════════════════
# STEP STATES
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
    return "active" if has_sel else "pending"

STEPS = ["Upload", "Select S.No", "Preview", "Export PDF"]

# Build sidebar inner HTML
steps_html = ""
for i, lbl in enumerate(STEPS):
    s = ss(i)
    dc = {"active":"da","done":"dd","pending":"dp"}[s]
    lc = {"active":"la","done":"ld","pending":"lp"}[s]
    steps_html += f'<div class="step"><div class="{dc}"></div><span class="{lc}">{lbl}</span></div>'

sidebar = f"""
<div class="sidebar">
  <div class="brand">Lunawat Gems</div>
  <div class="sidebar-title">Gem Catalog<br>Builder</div>
  {steps_html}
</div>"""


# ══════════════════════════════════════════════════════════════════════════════
# RENDER
# The trick: open .card-shell and .sidebar in HTML, then .form-area in HTML,
# then render Streamlit widgets (they appear inside the DOM flow naturally),
# then close tags.
# ══════════════════════════════════════════════════════════════════════════════

st.markdown(f'<div class="card-shell">{sidebar}<div class="form-area">', unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="eyebrow">Catalog Builder</div>
<div class="form-title">Upload your PDF catalog</div>
<div class="form-sub">Supports single-item and multi-item (4-up) layouts automatically.</div>
<div class="lbl">Catalog File</div>
""", unsafe_allow_html=True)

# ── Upload widget ─────────────────────────────────────────────────────────────
uploaded_file = st.file_uploader("PDF", type=["pdf"], label_visibility="collapsed")

col1, col2 = st.columns([4, 1], gap="small")
with col1:
    scan_btn = st.button("Scan Catalog", use_container_width=True)
with col2:
    st.markdown('<div class="sec">', unsafe_allow_html=True)
    rescan_btn = st.button("🔄 Re-scan", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ── Scan logic ────────────────────────────────────────────────────────────────
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
        st.warning("No S.No entries detected.")
    else:
        # ── Select ────────────────────────────────────────────────────────────
        st.markdown('<div class="divline"></div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="hrow">
          <div class="lbl" style="margin-bottom:0">Select Serial Numbers</div>
          <div class="pill">💎 {len(reg)} found</div>
        </div>""", unsafe_allow_html=True)

        selected = st.multiselect(
            "s", options=sorted(reg.keys()),
            default=[s for s in st.session_state.selected_snos if s in reg],
            format_func=lambda x: f"S.No {x}",
            placeholder="Type to search or click to select…",
            label_visibility="collapsed",
        )
        st.session_state.selected_snos = selected

        if selected:
            # ── Preview ───────────────────────────────────────────────────────
            st.markdown('<div class="divline"></div>', unsafe_allow_html=True)
            st.markdown(f"""
            <div class="hrow">
              <div class="lbl" style="margin-bottom:0">Preview</div>
              <div class="pill">{len(selected)} selected</div>
            </div>""", unsafe_allow_html=True)

            for pair in [selected[i:i+2] for i in range(0, len(selected), 2)]:
                cols = st.columns(len(pair), gap="small")
                for col, sno in zip(cols, pair):
                    with col:
                        st.image(reg[sno], caption=f"S.No {sno}", use_container_width=True)

            # ── Export ────────────────────────────────────────────────────────
            st.markdown('<div class="divline"></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="lbl">Export</div><p style="font-size:12px;color:#64748B;margin-bottom:12px;">Generate PDF with <strong>{len(selected)}</strong> entr{"y" if len(selected)==1 else "ies"}, one per page.</p>', unsafe_allow_html=True)

            if st.button("📄 Generate Selection PDF", use_container_width=True):
                with st.spinner("Building PDF…"):
                    out = fitz.open()
                    for sno in selected:
                        pg = out.new_page(width=595, height=842)
                        pg.insert_text(fitz.Point(40,45), f"Lunawat Gems — S.No {sno}", fontsize=14, color=(0,0,0))
                        pg.insert_image(fitz.Rect(40,65,555,780), stream=reg[sno])
                    buf = io.BytesIO()
                    out.save(buf); buf.seek(0)
                st.download_button("⬇️ Download Catalog PDF", data=buf,
                                   file_name="LGC_Selection_Catalog.pdf",
                                   mime="application/pdf", use_container_width=True)

st.markdown('</div></div>', unsafe_allow_html=True)  # close .form-area and .card-shell
