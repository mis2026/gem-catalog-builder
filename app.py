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
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stMain"] {
    font-family: 'Inter', sans-serif !important;
    background: #E4E6ED !important;
}
#MainMenu, footer, header,
[data-testid="stDecoration"],
[data-testid="stToolbar"],
[data-testid="stSidebar"] { display: none !important; }

.block-container {
    max-width: 860px !important;
    padding: 52px 20px 60px !important;
}

/* ════════════════════════════════════════════════
   CARD: the outermost columns row only
   We use a wrapper class set on the container
   ════════════════════════════════════════════════ */
.card-row [data-testid="stHorizontalBlock"] {
    border-radius: 16px !important;
    overflow: hidden !important;
    box-shadow: 0 4px 32px rgba(0,0,0,0.15) !important;
    gap: 0 !important;
    align-items: stretch !important;
}

/* LEFT col — DARK sidebar */
.card-row [data-testid="stHorizontalBlock"]
  > [data-testid="stColumn"]:first-child {
    background: #151C2C !important;
    min-width: 200px !important;
    max-width: 200px !important;
    flex-shrink: 0 !important;
}
.card-row [data-testid="stHorizontalBlock"]
  > [data-testid="stColumn"]:first-child > div {
    padding: 36px 22px !important;
    gap: 0 !important;
}

/* RIGHT col — WHITE content */
.card-row [data-testid="stHorizontalBlock"]
  > [data-testid="stColumn"]:last-child {
    background: #ffffff !important;
    flex: 1 !important;
}
.card-row [data-testid="stHorizontalBlock"]
  > [data-testid="stColumn"]:last-child > div {
    padding: 36px 36px 32px !important;
    gap: 0 !important;
}

/* Fix: all nested columns inside right panel = transparent */
.card-row [data-testid="stHorizontalBlock"]
  > [data-testid="stColumn"]:last-child
  [data-testid="stHorizontalBlock"] {
    border-radius: 0 !important;
    box-shadow: none !important;
    overflow: visible !important;
    background: transparent !important;
}
.card-row [data-testid="stHorizontalBlock"]
  > [data-testid="stColumn"]:last-child
  [data-testid="stColumn"] {
    background: transparent !important;
    padding: 0 !important;
    min-width: unset !important;
    max-width: unset !important;
    flex-shrink: 1 !important;
}
.card-row [data-testid="stHorizontalBlock"]
  > [data-testid="stColumn"]:last-child
  [data-testid="stColumn"] > div {
    padding: 0 4px !important;
}

/* Remove streamlit default gaps */
[data-testid="stVerticalBlock"] { gap: 0 !important; }
.stMarkdown { margin: 0 !important; }
div[data-testid="stVerticalBlockBorderWrapper"] { padding: 0 !important; }

/* ── Sidebar ── */
.sb-brand {
    font-size: 9px; font-weight: 700; letter-spacing: .18em;
    color: #3A506B; text-transform: uppercase;
    margin-bottom: 18px; display: block;
}
.sb-title {
    font-size: 17px; font-weight: 700; color: #fff;
    line-height: 1.3; margin-bottom: 32px; display: block;
}
.step {
    display: flex; align-items: center; gap: 11px;
    padding: 9px 0; position: relative;
}
.step:not(:last-child)::after {
    content: ''; position: absolute; left: 9px; top: 32px;
    width: 2px; height: 18px; background: #1E2D45;
}
.da { width:18px;height:18px;border-radius:50%;flex-shrink:0;
      background:#3B82F6;box-shadow:0 0 0 3px rgba(59,130,246,.22); }
.dd { width:18px;height:18px;border-radius:50%;flex-shrink:0;
      background:transparent;border:2px solid #3B82F6; }
.dp { width:18px;height:18px;border-radius:50%;flex-shrink:0;
      background:#1C2B40;border:2px solid #263A55; }
.la { font-size:12px;font-weight:600;color:#fff; }
.ld { font-size:12px;font-weight:500;color:#4B7BCA; }
.lp { font-size:12px;font-weight:400;color:#324560; }

/* ── Right panel text ── */
.ey { font-size:9px;font-weight:700;letter-spacing:.16em;
      color:#3B82F6;text-transform:uppercase;margin-bottom:5px;display:block; }
.pt { font-size:19px;font-weight:700;color:#0F172A;
      letter-spacing:-.02em;margin-bottom:4px;display:block; }
.ps { font-size:12px;color:#94A3B8;margin-bottom:20px;display:block; }
.lbl { font-size:9px;font-weight:700;letter-spacing:.12em;
       color:#B0BCCC;text-transform:uppercase;margin-bottom:7px;display:block; }
.divl { height:1px;background:#F1F5F9;margin:16px 0; }
.hrow { display:flex;justify-content:space-between;align-items:center;margin-bottom:9px; }
.pill { display:inline-flex;align-items:center;gap:4px;
        background:#EFF6FF;color:#1D4ED8;
        font-size:10px;font-weight:600;padding:3px 9px;border-radius:999px; }

/* ── Scan animation ── */
.scan-msg { font-size:12px;color:#64748B;
            display:flex;align-items:center;gap:8px;margin-bottom:8px; }
.scan-dot { width:7px;height:7px;border-radius:50%;background:#3B82F6;
            flex-shrink:0;animation:sdot 1.1s ease-in-out infinite; }
@keyframes sdot { 0%,100%{opacity:1;transform:scale(1);}
                   50%{opacity:.3;transform:scale(.65);} }
.prog-track { height:5px;background:#F1F5F9;border-radius:999px;overflow:hidden; }
.prog-bar { height:5px;background:linear-gradient(90deg,#3B82F6,#818CF8);
            border-radius:999px;animation:pbar 1.8s ease-in-out infinite;width:45%; }
@keyframes pbar { 0%{transform:translateX(-110%);} 100%{transform:translateX(280%);} }
.pg-count { font-size:11px;color:#94A3B8;margin-top:5px; }

/* ── Widgets ── */
[data-testid="stFileUploader"] {
    border:1.5px solid #E2E8F0 !important;border-radius:9px !important;
    background:#FAFBFC !important;padding:2px 8px !important;margin-bottom:10px !important;
}
[data-testid="stFileUploader"] section { padding:4px 0 !important; }

[data-testid="stMultiSelect"] > div > div {
    border:1.5px solid #E2E8F0 !important;border-radius:8px !important;
    font-size:13px !important;min-height:40px !important;background:#FAFBFC !important;
}
[data-testid="stMultiSelect"] > div > div:focus-within {
    border-color:#3B82F6 !important;box-shadow:0 0 0 3px rgba(59,130,246,.1) !important;
}

[data-testid="stButton"] > button {
    background:#2563EB !important;color:#fff !important;border:none !important;
    border-radius:8px !important;font-size:13px !important;font-weight:600 !important;
    height:40px !important;width:100% !important;transition:background .15s !important;
}
[data-testid="stButton"] > button:hover { background:#1D4ED8 !important; }

.sec [data-testid="stButton"] > button {
    background:#F1F5F9 !important;color:#475569 !important;font-size:12px !important;
}
.sec [data-testid="stButton"] > button:hover { background:#E2E8F0 !important; }

[data-testid="stDownloadButton"] > button {
    background:#059669 !important;color:#fff !important;border:none !important;
    border-radius:8px !important;font-size:13px !important;font-weight:600 !important;
    height:40px !important;width:100% !important;
}
[data-testid="stDownloadButton"] > button:hover { background:#047857 !important; }

[data-testid="stImage"] img {
    border-radius:8px !important;box-shadow:0 2px 10px rgba(0,0,0,.1) !important;
    display:block !important;
}
[data-testid="stImage"] > div > div {
    font-size:11px !important;color:#94A3B8 !important;
    text-align:center !important;margin-top:5px !important;
}
[data-testid="stAlert"] { border-radius:8px !important;font-size:13px !important; }
[data-testid="stSpinner"] > div { display:none !important; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# CORE LOGIC — unchanged + border removal
# ══════════════════════════════════════════════════════════════════════════════
GRID_X, GRID_Y, RENDER_ZOOM = 360, 277, 2.5

if "gem_registry"  not in st.session_state: st.session_state.gem_registry  = {}
if "selected_snos" not in st.session_state: st.session_state.selected_snos = []


def _remove_border(arr: np.ndarray, dark: int = 40) -> np.ndarray:
    h, w = arr.shape[:2]
    gray = arr.mean(axis=2)
    rd   = (gray < dark).sum(axis=1)
    cd   = (gray < dark).sum(axis=0)
    frac = 0.40
    tr = np.where((rd > w * frac) & (np.arange(h) < h * .45))[0]
    br = np.where((rd > w * frac) & (np.arange(h) > h * .55))[0]
    lc = np.where((cd > h * frac) & (np.arange(w) < w * .45))[0]
    rc = np.where((cd > h * frac) & (np.arange(w) > w * .55))[0]
    t = int(tr.max()) + 2 if len(tr) else 0
    b = int(br.min())     if len(br) else h
    l = int(lc.max()) + 2 if len(lc) else 0
    r = int(rc.min())     if len(rc) else w
    return arr[t:b, l:r]


def _render_clean(page: fitz.Page, rect: fitz.Rect) -> bytes:
    pix   = page.get_pixmap(matrix=fitz.Matrix(RENDER_ZOOM, RENDER_ZOOM), clip=rect)
    arr   = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
    clean = _remove_border(arr[:, :, :3])
    buf   = io.BytesIO()
    Image.fromarray(clean).save(buf, "JPEG", quality=88)
    return buf.getvalue()


def _quadrant_rect(page: fitz.Page, bbox) -> fitz.Rect:
    pw, ph = page.rect.width, page.rect.height
    l, t   = bbox[0] < GRID_X, bbox[1] < GRID_Y
    if l and t:      return fitz.Rect(0,      0,      GRID_X, GRID_Y)
    if not l and t:  return fitz.Rect(GRID_X, 0,      pw,     GRID_Y)
    if l and not t:  return fitz.Rect(0,      GRID_Y, GRID_X, ph)
    return fitz.Rect(GRID_X, GRID_Y, pw, ph)


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

def make_sidebar():
    dc = {"active":"da","done":"dd","pending":"dp"}
    lc = {"active":"la","done":"ld","pending":"lp"}
    rows = "".join(
        f'<div class="step"><div class="{dc[ss(i)]}"></div>'
        f'<span class="{lc[ss(i)]}">{lbl}</span></div>'
        for i, lbl in enumerate(STEPS)
    )
    return f"""
<span class="sb-brand">Lunawat Gems</span>
<span class="sb-title">Gem Catalog<br>Builder</span>
{rows}"""


# ══════════════════════════════════════════════════════════════════════════════
# LAYOUT — wrap in .card-row so CSS targets only this columns block
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="card-row">', unsafe_allow_html=True)

col_left, col_right = st.columns([22, 78], gap="small")

with col_left:
    st.markdown(make_sidebar(), unsafe_allow_html=True)

with col_right:
    st.markdown("""
    <span class="ey">Catalog Builder</span>
    <span class="pt">Upload your PDF catalog</span>
    <span class="ps">Supports single-item and multi-item (4-up) layouts.</span>
    <span class="lbl">Catalog File</span>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader("PDF", type=["pdf"], label_visibility="collapsed")

    c1, c2 = st.columns([4, 1], gap="small")
    with c1:
        scan_btn = st.button("Scan Catalog", use_container_width=True)
    with c2:
        st.markdown('<div class="sec">', unsafe_allow_html=True)
        rescan_btn = st.button("🔄 Re-scan", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    if uploaded_file:
        file_bytes = uploaded_file.read()

        if rescan_btn:
            st.session_state.gem_registry  = {}
            st.session_state.selected_snos = []
            st.rerun()

        needs_scan = (scan_btn or not st.session_state.gem_registry) and bool(file_bytes)

        if needs_scan:
            st.markdown('<div class="divl"></div>', unsafe_allow_html=True)
            st.markdown("""
            <div class="scan-msg">
              <div class="scan-dot"></div>
              Scanning pages and removing borders…
            </div>
            <div class="prog-track"><div class="prog-bar"></div></div>
            """, unsafe_allow_html=True)

            pg_counter = st.empty()
            doc        = fitz.open(stream=file_bytes, filetype="pdf")
            total      = len(doc)
            registry   = {}

            for pn in range(total):
                pg_counter.markdown(
                    f'<div class="pg-count">Page {pn+1} of {total}</div>',
                    unsafe_allow_html=True,
                )
                page  = doc[pn]
                lines = []
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
            pg_counter.empty()
            st.session_state.gem_registry = registry
            st.rerun()

        reg = st.session_state.gem_registry

        if not reg:
            st.warning("No S.No entries detected.")
        else:
            st.markdown('<div class="divl"></div>', unsafe_allow_html=True)
            st.markdown(f"""
            <div class="hrow">
              <span class="lbl" style="margin-bottom:0">Select Serial Numbers</span>
              <span class="pill">💎 {len(reg)} entries found</span>
            </div>""", unsafe_allow_html=True)

            selected = st.multiselect(
                "s",
                options=sorted(reg.keys()),
                default=[s for s in st.session_state.selected_snos if s in reg],
                format_func=lambda x: f"S.No {x}",
                placeholder="Type to search or click to select…",
                label_visibility="collapsed",
            )
            st.session_state.selected_snos = selected

            if selected:
                st.markdown('<div class="divl"></div>', unsafe_allow_html=True)
                st.markdown(f"""
                <div class="hrow">
                  <span class="lbl" style="margin-bottom:0">Preview</span>
                  <span class="pill">{len(selected)} selected</span>
                </div>""", unsafe_allow_html=True)

                for pair in [selected[i:i+2] for i in range(0, len(selected), 2)]:
                    img_cols = st.columns(len(pair), gap="small")
                    for col, sno in zip(img_cols, pair):
                        with col:
                            st.image(reg[sno], caption=f"S.No {sno}",
                                     use_container_width=True)

                st.markdown('<div class="divl"></div>', unsafe_allow_html=True)
                st.markdown(
                    f'<span class="lbl">Export</span>'
                    f'<p style="font-size:12px;color:#64748B;margin:6px 0 12px;">'
                    f'Generate a PDF with <strong>{len(selected)}</strong> '
                    f'entr{"y" if len(selected)==1 else "ies"}, one per page.</p>',
                    unsafe_allow_html=True,
                )

                if st.button("📄 Generate Selection PDF", use_container_width=True):
                    with st.spinner(""):
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

st.markdown('</div>', unsafe_allow_html=True)  # close .card-row
