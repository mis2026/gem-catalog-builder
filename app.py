import streamlit as st
import fitz
import re, io
import numpy as np
from PIL import Image

st.set_page_config(
    page_title="Lunawat Gem Catalog",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stMain"] {
    font-family: 'Inter', sans-serif !important;
    background: #E5E7EE !important;
}
#MainMenu, footer, header,
[data-testid="stDecoration"],
[data-testid="stToolbar"],
[data-testid="stSidebar"] { display: none !important; }

.block-container {
    max-width: 860px !important;
    padding: 48px 20px 60px !important;
}

/* ── Floating card ── */
.shell {
    display: flex;
    border-radius: 18px;
    overflow: hidden;
    box-shadow: 0 6px 36px rgba(0,0,0,0.15);
    background: #fff;
}

/* ── Left dark sidebar ── */
.sb {
    width: 210px;
    min-width: 210px;
    background: #151C2C;
    padding: 36px 22px;
    display: flex;
    flex-direction: column;
    flex-shrink: 0;
}
.sb-brand { font-size:9px;font-weight:700;letter-spacing:.18em;
            color:#3A506B;text-transform:uppercase;margin-bottom:18px; }
.sb-title { font-size:17px;font-weight:700;color:#fff;
            line-height:1.3;margin-bottom:32px; }
.step { display:flex;align-items:center;gap:11px;padding:9px 0;position:relative; }
.step:not(:last-child)::after {
    content:'';position:absolute;left:9px;top:32px;
    width:2px;height:18px;background:#1E2D45; }
.da{width:19px;height:19px;border-radius:50%;flex-shrink:0;
    background:#3B82F6;box-shadow:0 0 0 4px rgba(59,130,246,.18);}
.dd{width:19px;height:19px;border-radius:50%;flex-shrink:0;
    background:transparent;border:2px solid #3B82F6;}
.dp{width:19px;height:19px;border-radius:50%;flex-shrink:0;
    background:#1C2B40;border:2px solid #283D57;}
.la{font-size:12px;font-weight:600;color:#fff;}
.ld{font-size:12px;font-weight:500;color:#4B7BCA;}
.lp{font-size:12px;font-weight:400;color:#324560;}

/* ── Right white panel ── */
.rp {
    flex:1;
    padding: 36px 36px 32px;
    min-width: 0;
    background: #fff;
}
.ey{font-size:9px;font-weight:700;letter-spacing:.16em;
    color:#3B82F6;text-transform:uppercase;margin-bottom:5px;}
.pt{font-size:19px;font-weight:700;color:#0F172A;
    letter-spacing:-.02em;margin-bottom:3px;}
.ps{font-size:12px;color:#94A3B8;margin-bottom:20px;}
.lbl{font-size:9px;font-weight:700;letter-spacing:.12em;
     color:#C0CCDA;text-transform:uppercase;margin-bottom:6px;}
.div{height:1px;background:#F1F5F9;margin:18px 0;}
.hr{display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;}
.pill{display:inline-flex;align-items:center;gap:4px;
      background:#EFF6FF;color:#1D4ED8;
      font-size:10px;font-weight:600;padding:3px 9px;border-radius:999px;}

/* ── Progress bar animation ── */
.progress-wrap {
    margin: 14px 0 6px;
    background: #F1F5F9;
    border-radius: 999px;
    height: 6px;
    overflow: hidden;
}
.progress-bar {
    height: 6px;
    background: linear-gradient(90deg, #3B82F6, #6366F1);
    border-radius: 999px;
    animation: prog 2.2s ease-in-out infinite;
    width: 40%;
}
@keyframes prog {
    0%   { margin-left: -40%; }
    100% { margin-left: 110%; }
}
.scan-msg {
    font-size:12px;color:#64748B;
    display:flex;align-items:center;gap:8px;margin-bottom:4px;
}
.scan-dot {
    display:inline-block;width:7px;height:7px;border-radius:50%;
    background:#3B82F6;
    animation: pulse 1.2s ease-in-out infinite;
}
@keyframes pulse {
    0%,100%{opacity:1;transform:scale(1);}
    50%{opacity:.4;transform:scale(.7);}
}

/* ── Widgets ── */
[data-testid="stFileUploader"]{
    border:1.5px solid #E2E8F0 !important;
    border-radius:9px !important;
    background:#FAFBFC !important;
    padding:2px 8px !important;
    margin-bottom:10px !important;
}
[data-testid="stFileUploader"] section{padding:4px 0 !important;}

[data-testid="stMultiSelect"] > div > div {
    border:1.5px solid #E2E8F0 !important;
    border-radius:8px !important;
    font-size:13px !important;
    min-height:40px !important;
    background:#FAFBFC !important;
}
[data-testid="stMultiSelect"] > div > div:focus-within{
    border-color:#3B82F6 !important;
    box-shadow:0 0 0 3px rgba(59,130,246,.1) !important;
}

/* Primary */
[data-testid="stButton"] > button {
    background:#2563EB !important;color:#fff !important;
    border:none !important;border-radius:8px !important;
    font-size:13px !important;font-weight:600 !important;
    height:40px !important;width:100% !important;
    transition:background .15s !important;
}
[data-testid="stButton"] > button:hover{background:#1D4ED8 !important;}

/* Secondary re-scan */
.sec [data-testid="stButton"] > button {
    background:#F1F5F9 !important;color:#475569 !important;font-size:12px !important;
}
.sec [data-testid="stButton"] > button:hover{background:#E2E8F0 !important;}

/* Download */
[data-testid="stDownloadButton"] > button {
    background:#059669 !important;color:#fff !important;
    border:none !important;border-radius:8px !important;
    font-size:13px !important;font-weight:600 !important;
    height:40px !important;width:100% !important;
}
[data-testid="stDownloadButton"] > button:hover{background:#047857 !important;}

[data-testid="stImage"] img{border-radius:8px;box-shadow:0 2px 10px rgba(0,0,0,.10);}
[data-testid="stAlert"]{border-radius:8px !important;font-size:13px !important;}
[data-testid="stSpinner"]{display:none !important;}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# CORE LOGIC — unchanged + border removal added
# ══════════════════════════════════════════════════════════════════════════════
GRID_X, GRID_Y, RENDER_ZOOM = 360, 277, 2.5

if "gem_registry"  not in st.session_state: st.session_state.gem_registry  = {}
if "selected_snos" not in st.session_state: st.session_state.selected_snos = []
if "scanning"      not in st.session_state: st.session_state.scanning      = False


def _remove_border(arr_rgb: np.ndarray, dark_thresh: int = 40) -> np.ndarray:
    """Strip the thin black rectangle border from a rendered gem image."""
    h, w  = arr_rgb.shape[:2]
    gray  = arr_rgb.mean(axis=2)
    row_d = (gray < dark_thresh).sum(axis=1)
    col_d = (gray < dark_thresh).sum(axis=0)

    # Rows / cols that are ≥40% dark → border lines
    frac = 0.40
    top_rows  = np.where((row_d > w * frac) & (np.arange(h) < h * 0.4))[0]
    bot_rows  = np.where((row_d > w * frac) & (np.arange(h) > h * 0.6))[0]
    lft_cols  = np.where((col_d > h * frac) & (np.arange(w) < w * 0.4))[0]
    rgt_cols  = np.where((col_d > h * frac) & (np.arange(w) > w * 0.6))[0]

    t = int(top_rows.max()) + 2 if len(top_rows) else 0
    b = int(bot_rows.min()) - 1 if len(bot_rows) else h
    l = int(lft_cols.max()) + 2 if len(lft_cols) else 0
    r = int(rgt_cols.min()) - 1 if len(rgt_cols) else w

    return arr_rgb[t:b, l:r]


def _render_clean(page: fitz.Page, rect: fitz.Rect) -> bytes:
    """Render a page region, remove border, return JPEG bytes."""
    mat = fitz.Matrix(RENDER_ZOOM, RENDER_ZOOM)
    pix = page.get_pixmap(matrix=mat, clip=rect)
    arr = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
    clean = _remove_border(arr[:, :, :3])
    buf = io.BytesIO()
    Image.fromarray(clean).save(buf, "JPEG", quality=88)
    return buf.getvalue()


def _quadrant_rect(page: fitz.Page, bbox) -> fitz.Rect:
    pw, ph = page.rect.width, page.rect.height
    l, t   = bbox[0] < GRID_X, bbox[1] < GRID_Y
    if l  and t:      return fitz.Rect(0,      0,      GRID_X, GRID_Y)
    if not l and t:   return fitz.Rect(GRID_X, 0,      pw,     GRID_Y)
    if l  and not t:  return fitz.Rect(0,      GRID_Y, GRID_X, ph)
    return fitz.Rect(GRID_X, GRID_Y, pw, ph)


def scan_pdf(file_bytes: bytes) -> dict:
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
            rect           = _quadrant_rect(page, bbox) if multi else page.rect
            registry[sno]  = _render_clean(page, rect)
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

steps_html = ""
for i, lbl in enumerate(STEPS):
    s   = ss(i)
    dc  = {"active":"da","done":"dd","pending":"dp"}[s]
    lc  = {"active":"la","done":"ld","pending":"lp"}[s]
    steps_html += f'<div class="step"><div class="{dc}"></div><span class="{lc}">{lbl}</span></div>'

sidebar_html = f"""
<div class="sb">
  <div class="sb-brand">Lunawat Gems</div>
  <div class="sb-title">Gem Catalog<br>Builder</div>
  {steps_html}
</div>"""


# ══════════════════════════════════════════════════════════════════════════════
# RENDER  — open shell + sidebar in HTML, widgets flow inside rp, close at end
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(
    f'<div class="shell">{sidebar_html}<div class="rp">',
    unsafe_allow_html=True
)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="ey">Catalog Builder</div>
<div class="pt">Upload your PDF catalog</div>
<div class="ps">Supports single-item and multi-item (4-up) layouts automatically.</div>
<div class="lbl">Catalog File</div>
""", unsafe_allow_html=True)

# ── File uploader ─────────────────────────────────────────────────────────────
uploaded_file = st.file_uploader("PDF", type=["pdf"], label_visibility="collapsed")

c1, c2 = st.columns([4, 1], gap="small")
with c1:
    scan_btn = st.button("Scan Catalog", use_container_width=True)
with c2:
    st.markdown('<div class="sec">', unsafe_allow_html=True)
    rescan_btn = st.button("🔄 Re-scan", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ── Scan ─────────────────────────────────────────────────────────────────────
if uploaded_file:
    file_bytes = uploaded_file.read()

    if rescan_btn:
        st.session_state.gem_registry  = {}
        st.session_state.selected_snos = []
        st.rerun()

    needs_scan = (scan_btn or not st.session_state.gem_registry) and bool(file_bytes)

    if needs_scan:
        # ── Scanning animation ────────────────────────────────────────────────
        st.markdown("""
        <div class="div"></div>
        <div class="scan-msg">
            <span class="scan-dot"></span>
            Scanning pages and cropping gem entries…
        </div>
        <div class="progress-wrap"><div class="progress-bar"></div></div>
        """, unsafe_allow_html=True)

        prog = st.empty()
        total_placeholder = st.empty()

        with st.spinner(""):
            doc        = fitz.open(stream=file_bytes, filetype="pdf")
            total_pgs  = len(doc)
            registry   = {}

            for pn in range(total_pgs):
                page, lines = doc[pn], []

                # Update mini progress
                pct = int((pn + 1) / total_pgs * 100)
                prog.markdown(
                    f'<div style="font-size:11px;color:#94A3B8;margin-top:4px;">'
                    f'Page {pn+1} of {total_pgs} — {pct}% complete</div>',
                    unsafe_allow_html=True
                )

                for block in page.get_text("dict")["blocks"]:
                    if block["type"] != 0: continue
                    for line in block["lines"]:
                        txt = "".join(s["text"] for s in line["spans"])
                        m   = re.search(r'S\.No[-\s]*(\d+)', txt, re.IGNORECASE)
                        if m: lines.append((m.group(1), line["bbox"]))

                if not lines: continue
                multi = len(lines) > 1
                for sno, bbox in lines:
                    rect          = _quadrant_rect(page, bbox) if multi else page.rect
                    registry[sno] = _render_clean(page, rect)

            doc.close()

        prog.empty()
        total_placeholder.empty()
        st.session_state.gem_registry = registry
        st.rerun()

    reg = st.session_state.gem_registry

    if not reg:
        st.warning("No S.No entries detected in this PDF.")

    else:
        # ── Select ────────────────────────────────────────────────────────────
        st.markdown('<div class="div"></div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="hr">
          <div class="lbl" style="margin-bottom:0">Select Serial Numbers</div>
          <div class="pill">💎 {len(reg)} entries found</div>
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
            st.markdown('<div class="div"></div>', unsafe_allow_html=True)
            st.markdown(f"""
            <div class="hr">
              <div class="lbl" style="margin-bottom:0">Preview</div>
              <div class="pill">{len(selected)} selected</div>
            </div>""", unsafe_allow_html=True)

            for pair in [selected[i:i+2] for i in range(0, len(selected), 2)]:
                cols = st.columns(len(pair), gap="small")
                for col, sno in zip(cols, pair):
                    with col:
                        st.image(reg[sno], caption=f"S.No {sno}",
                                 use_container_width=True)

            # ── Export ────────────────────────────────────────────────────────
            st.markdown('<div class="div"></div>', unsafe_allow_html=True)
            st.markdown(
                f'<div class="lbl">Export</div>'
                f'<p style="font-size:12px;color:#64748B;margin-bottom:12px;">'
                f'Generate a PDF with <strong>{len(selected)}</strong> '
                f'entr{"y" if len(selected)==1 else "ies"}, one per page.</p>',
                unsafe_allow_html=True,
            )

            if st.button("📄 Generate Selection PDF", use_container_width=True):
                with st.spinner("Building PDF…"):
                    out = fitz.open()
                    for sno in selected:
                        pg = out.new_page(width=595, height=842)
                        pg.insert_text(fitz.Point(40, 45),
                                       f"Lunawat Gems — S.No {sno}",
                                       fontsize=14, color=(0, 0, 0))
                        pg.insert_image(fitz.Rect(40, 65, 555, 780),
                                        stream=reg[sno])
                    buf = io.BytesIO()
                    out.save(buf); buf.seek(0)

                st.download_button(
                    "⬇️ Download Catalog PDF",
                    data=buf,
                    file_name="LGC_Selection_Catalog.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )

st.markdown('</div></div>', unsafe_allow_html=True)  # close .rp and .shell
