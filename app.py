import streamlit as st
import fitz
import re, io
import numpy as np
from PIL import Image

st.set_page_config(
    page_title="Lunawat Gem Catalog",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stMain"] {
    font-family: 'Inter', sans-serif !important;
    background: #ECEEF3 !important;
}
#MainMenu, footer, header,
[data-testid="stDecoration"],
[data-testid="stToolbar"],
[data-testid="stSidebar"] { display: none !important; }

.block-container { max-width: 100% !important; padding: 0 !important; }

/* ── Card ── */
[data-testid="stMainBlockContainer"]
  [data-testid="stHorizontalBlock"]:first-of-type {
    border-radius: 0 !important;
    overflow: hidden !important;
    box-shadow: none !important;
    gap: 0 !important;
    align-items: stretch !important;
    min-height: 100vh !important;
}

/* LEFT sidebar */
[data-testid="stMainBlockContainer"]
  [data-testid="stHorizontalBlock"]:first-of-type
  > [data-testid="stColumn"]:first-child {
    background: #151C2C !important;
    min-width: 240px !important;
    max-width: 240px !important;
    flex-shrink: 0 !important;
}
[data-testid="stMainBlockContainer"]
  [data-testid="stHorizontalBlock"]:first-of-type
  > [data-testid="stColumn"]:first-child
  > [data-testid="stVerticalBlock"] {
    padding: 40px 24px !important;
    gap: 0 !important;
}

/* RIGHT content */
[data-testid="stMainBlockContainer"]
  [data-testid="stHorizontalBlock"]:first-of-type
  > [data-testid="stColumn"]:last-child {
    background: #ffffff !important;
    flex: 1 !important;
}
[data-testid="stMainBlockContainer"]
  [data-testid="stHorizontalBlock"]:first-of-type
  > [data-testid="stColumn"]:last-child
  > [data-testid="stVerticalBlock"] {
    padding: 40px 48px 40px !important;
    gap: 0 !important;
}

/* Reset all nested columns */
[data-testid="stMainBlockContainer"]
  [data-testid="stHorizontalBlock"]:first-of-type
  > [data-testid="stColumn"]:last-child
  [data-testid="stHorizontalBlock"] {
    border-radius: 0 !important; box-shadow: none !important;
    overflow: visible !important; min-height: unset !important; gap: 8px !important;
}
[data-testid="stMainBlockContainer"]
  [data-testid="stHorizontalBlock"]:first-of-type
  > [data-testid="stColumn"]:last-child
  [data-testid="stColumn"] {
    background: transparent !important;
    min-width: unset !important; max-width: unset !important; flex-shrink: 1 !important;
}
[data-testid="stMainBlockContainer"]
  [data-testid="stHorizontalBlock"]:first-of-type
  > [data-testid="stColumn"]:last-child
  [data-testid="stColumn"] > [data-testid="stVerticalBlock"] { padding: 0 !important; }

[data-testid="stVerticalBlock"] { gap: 0 !important; }
.stMarkdown { margin-bottom: 0 !important; }

/* ── Sidebar ── */
.sb-brand { font-size:10px;font-weight:700;letter-spacing:.2em;color:#3E5270;
            text-transform:uppercase;margin-bottom:20px;display:block; }
.sb-title { font-size:18px;font-weight:700;color:#fff;
            line-height:1.3;margin-bottom:28px;display:block; }

.sb-divider { height:1px;background:#1E2D45;margin:20px 0; }

/* Steps */
.step { display:flex;align-items:center;gap:11px;padding:9px 0;position:relative; }
.step:not(:last-child)::after {
    content:'';position:absolute;left:9px;top:32px;width:2px;height:18px;background:#1E2D45; }
.d-a{width:18px;height:18px;border-radius:50%;flex-shrink:0;
     background:#3B82F6;box-shadow:0 0 0 3px rgba(59,130,246,.22);}
.d-d{width:18px;height:18px;border-radius:50%;flex-shrink:0;
     background:transparent;border:2px solid #3B82F6;}
.d-p{width:18px;height:18px;border-radius:50%;flex-shrink:0;
     background:#1C2B40;border:2px solid #26394F;}
.l-a{font-size:12px;font-weight:600;color:#fff;}
.l-d{font-size:12px;font-weight:500;color:#4B7BCA;}
.l-p{font-size:12px;font-weight:400;color:#334E6A;}

/* ── Top Tabs Switcher ── */
.top-tabs-container {
    display: flex;
    background: #F8FAFC;
    padding: 6px;
    border-radius: 12px;
    margin-bottom: 24px;
    position: relative;
    border: 1px solid #E2E8F0;
    gap: 8px;
}
.top-tab {
    flex: 1;
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 10px 16px;
    border-radius: 8px;
    transition: all 0.2s ease;
    user-select: none;
    background: transparent;
}
.top-tab.active {
    background: #ffffff;
    box-shadow: 0 4px 12px rgba(15, 23, 42, 0.06);
}
.top-tab-icon {
    font-size: 20px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #F1F5F9;
    width: 36px;
    height: 36px;
    border-radius: 6px;
}
.top-tab.active .top-tab-icon {
    background: #EFF6FF;
}
.top-tab-text-container {
    display: flex;
    flex-direction: column;
}
.top-tab-label {
    font-size: 13px;
    font-weight: 700;
    color: #475569;
}
.top-tab.active .top-tab-label {
    color: #0F172A;
}
.top-tab-sub {
    font-size: 11px;
    color: #94A3B8;
    margin-top: 1px;
}
.top-tab.active .top-tab-sub {
    color: #2563EB;
}

/* Position Streamlit buttons to overlay the top-tabs */
div[data-testid="stMainBlockContainer"]
  [data-testid="stHorizontalBlock"]:first-of-type
  > [data-testid="stColumn"]:last-child
  > [data-testid="stVerticalBlock"]
  > [data-testid="stHorizontalBlock"]:first-of-type {
    margin-bottom: 24px !important;
}
div[data-testid="stMainBlockContainer"]
  [data-testid="stHorizontalBlock"]:first-of-type
  > [data-testid="stColumn"]:last-child
  > [data-testid="stVerticalBlock"]
  > [data-testid="stHorizontalBlock"]:first-of-type
  .stButton {
    position: relative;
    margin-top: -92px !important; /* Pull up to overlay the top-tabs */
    opacity: 0 !important;
    height: 68px !important;
}
div[data-testid="stMainBlockContainer"]
  [data-testid="stHorizontalBlock"]:first-of-type
  > [data-testid="stColumn"]:last-child
  > [data-testid="stVerticalBlock"]
  > [data-testid="stHorizontalBlock"]:first-of-type
  .stButton button {
    height: 68px !important;
    cursor: pointer !important;
}

/* ── Right panel ── */
.rp-eye   { font-size:10px;font-weight:700;letter-spacing:.16em;color:#3B82F6;
             text-transform:uppercase;display:block;margin-bottom:6px; }
.rp-title { font-size:22px;font-weight:700;color:#0F172A;
             letter-spacing:-.02em;display:block;margin-bottom:4px; }
.rp-sub   { font-size:13px;color:#94A3B8;display:block;margin-bottom:24px; }
.rp-label { font-size:10px;font-weight:700;letter-spacing:.12em;color:#B8C5D4;
             text-transform:uppercase;display:block;margin-bottom:7px; }
.rp-divider { height:1px;background:#F1F5F9;margin:20px 0; }
.rp-row   { display:flex;justify-content:space-between;align-items:center;margin-bottom:9px; }
.rp-pill  { display:inline-flex;align-items:center;gap:4px;background:#EFF6FF;color:#1D4ED8;
             font-size:11px;font-weight:600;padding:3px 10px;border-radius:999px; }
.rp-note  { font-size:13px;color:#64748B;margin:6px 0 14px;line-height:1.5; }

/* Scan animation */
.scan-row { display:flex;align-items:center;gap:8px;font-size:13px;color:#475569;margin-bottom:8px; }
.scan-dot { width:7px;height:7px;border-radius:50%;background:#3B82F6;
            flex-shrink:0;animation:sdot 1s ease-in-out infinite; }
@keyframes sdot{0%,100%{opacity:1}50%{opacity:.2}}
.prog-track { height:4px;background:#EEF2FF;border-radius:999px;overflow:hidden; }
.prog-bar   { height:4px;width:45%;border-radius:999px;
              background:linear-gradient(90deg,#3B82F6,#818CF8);
              animation:pbar 1.8s ease-in-out infinite; }
@keyframes pbar{0%{transform:translateX(-120%)}100%{transform:translateX(300%)}}
.pg-count { font-size:11px;color:#94A3B8;margin-top:4px; }

/* Widgets */
[data-testid="stFileUploader"] {
    border:1.5px solid #E2E8F0 !important;border-radius:9px !important;
    background:#FAFBFC !important;padding:2px 10px !important;margin-bottom:12px !important;
}
[data-testid="stFileUploader"] section { padding:4px 0 !important; }

[data-testid="stTextInput"] input {
    border:1.5px solid #E2E8F0 !important;border-radius:8px !important;
    font-size:13px !important;padding:10px 14px !important;background:#FAFBFC !important;
    color:#0F172A !important;
}
[data-testid="stTextInput"] input:focus {
    border-color:#3B82F6 !important;box-shadow:0 0 0 3px rgba(59,130,246,.1) !important;
}

[data-testid="stMultiSelect"]>div>div {
    border:1.5px solid #E2E8F0 !important;border-radius:8px !important;
    font-size:13px !important;min-height:42px !important;background:#FAFBFC !important;
}
[data-testid="stMultiSelect"]>div>div:focus-within {
    border-color:#3B82F6 !important;box-shadow:0 0 0 3px rgba(59,130,246,.1) !important;
}

[data-testid="stCheckbox"] label { font-size:13px !important;color:#334155 !important; }

/* Primary button */
[data-testid="stButton"]>button {
    background:#2563EB !important;color:#fff !important;border:none !important;
    border-radius:8px !important;font-size:13px !important;font-weight:600 !important;
    height:42px !important;width:100% !important;transition:background .15s !important;
}
[data-testid="stButton"]>button:hover { background:#1D4ED8 !important; }

/* Secondary */
.btn-sec [data-testid="stButton"]>button {
    background:#F1F5F9 !important;color:#475569 !important;
    min-width:100px !important;width:100px !important;
}
.btn-sec [data-testid="stButton"]>button:hover { background:#E2E8F0 !important; }

/* Download */
[data-testid="stDownloadButton"]>button {
    background:#059669 !important;color:#fff !important;border:none !important;
    border-radius:8px !important;font-size:13px !important;font-weight:600 !important;
    height:42px !important;width:100% !important;
}
[data-testid="stDownloadButton"]>button:hover { background:#047857 !important; }

[data-testid="stImage"] img {
    border-radius:8px !important;box-shadow:0 2px 12px rgba(0,0,0,.09) !important;
}
[data-testid="stImage"]>div>div {
    font-size:11px !important;color:#94A3B8 !important;
    text-align:center !important;margin-top:5px !important;
}
[data-testid="stAlert"]   { border-radius:8px !important;font-size:13px !important; }
[data-testid="stSpinner"] > div { display:none !important; }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════
# CORE LOGIC — unchanged
# ═══════════════════════════════════════════════════════
GRID_X, GRID_Y, RENDER_ZOOM = 360, 277, 2.5

# Session state
for k, v in {
    "gem_registry":   {},
    "selected_snos":  [],
    "cover_page_jpg": None,
    "upload_fname":   "",
}.items():
    if k not in st.session_state:
        st.session_state[k] = v


def _remove_border(arr: np.ndarray, dark: int = 40) -> np.ndarray:
    h, w = arr.shape[:2]
    gray = arr.mean(axis=2)
    rd   = (gray < dark).sum(axis=1)
    cd   = (gray < dark).sum(axis=0)
    frac = 0.40
    tr = np.where((rd > w*frac) & (np.arange(h) < h*.45))[0]
    br = np.where((rd > w*frac) & (np.arange(h) > h*.55))[0]
    lc = np.where((cd > h*frac) & (np.arange(w) < w*.45))[0]
    rc = np.where((cd > h*frac) & (np.arange(w) > w*.55))[0]
    t = int(tr.max())+2 if len(tr) else 0
    b = int(br.min())   if len(br) else h
    l = int(lc.max())+2 if len(lc) else 0
    r = int(rc.min())   if len(rc) else w
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


def build_pdf(pages_jpg: list[bytes]) -> bytes:
    """Turn a list of JPEG byte strings into a PDF, each image full-bleed A4."""
    out = fitz.open()
    for jpg in pages_jpg:
        # Match page size to image aspect ratio to avoid any letterboxing.
        # Decode image dims, then create a page that exactly matches, so the
        # image fills edge-to-edge with no white borders whatsoever.
        img = Image.open(io.BytesIO(jpg))
        iw, ih = img.size
        # Scale to A4 width (595pt), adjust height proportionally
        scale = 595 / iw
        ph = round(ih * scale)
        pg = out.new_page(width=595, height=ph)
        pg.insert_image(fitz.Rect(0, 0, 595, ph), stream=jpg, keep_proportion=False)
    buf = io.BytesIO()
    out.save(buf)
    buf.seek(0)
    return buf.getvalue()


# ═══════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════
def make_sidebar(has_scan: bool, has_sel: bool, mode: str = "extract"):
    # Steps logic based on active mode
    if mode == "extract":
        steps = ["Upload PDF", "Select S.No", "Preview", "Export PDF"]
        def ss(i):
            if i == 0: return "done"   if has_scan  else "active"
            if i == 1:
                if has_sel:  return "done"
                if has_scan: return "active"
                return "pending"
            return "active" if has_sel else "pending"
    else:
        # Steps for combine mode
        steps = ["Upload Images", "Upload Cover", "Catalog Name", "Export PDF"]
        has_gems = bool(st.session_state.get("comb_gems"))
        has_name = bool(st.session_state.get("comb_name"))
        def ss(i):
            if i == 0: return "done" if has_gems else "active"
            if i == 1: return "done" if has_gems else "pending"
            if i == 2: return "active" if has_gems else "pending"
            return "active" if (has_gems and has_name) else "pending"

    dc = {"active":"d-a","done":"d-d","pending":"d-p"}
    lc = {"active":"l-a","done":"l-d","pending":"l-p"}

    steps_html = "".join(
        f'<div class="step"><div class="{dc[ss(i)]}"></div>'
        f'<span class="{lc[ss(i)]}">{lbl}</span></div>'
        for i, lbl in enumerate(steps)
    )

    return (
        f'<span class="sb-brand">Lunawat Gems</span>'
        f'<span class="sb-title">Gem Catalog<br>Builder</span>'
        f'<div class="sb-divider" style="margin-top:0;"></div>'
        f'{steps_html}'
    )


# ═══════════════════════════════════════════════════════
# TOP TABS GENERATOR
# ═══════════════════════════════════════════════════════
def make_top_tabs(mode: str = "extract"):
    def tab(key, icon, label, sub):
        cls = "top-tab active" if mode == key else "top-tab"
        return (
            f'<div class="{cls}">'
            f'<span class="top-tab-icon">{icon}</span>'
            f'<div class="top-tab-text-container">'
            f'<div class="top-tab-label">{label}</div>'
            f'<div class="top-tab-sub">{sub}</div>'
            f'</div>'
            f'</div>'
        )

    tabs_html = (
        tab("extract", "📂", "Extract Images", "Crop from catalog PDF")
        + tab("combine", "🖼️", "Combine Images", "Build PDF from images")
    )
    return f'<div class="top-tabs-container">{tabs_html}</div>'


# ═══════════════════════════════════════════════════════
# LAYOUT
# ═══════════════════════════════════════════════════════
reg      = st.session_state.gem_registry
has_scan = bool(reg)
has_sel  = bool(st.session_state.selected_snos) and has_scan

# Mode is tracked in query params
mode = st.query_params.get("mode", "extract")

col_sb, col_main = st.columns([16, 84], gap="small")

with col_sb:
    st.markdown(make_sidebar(has_scan, has_sel, mode), unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════
# RIGHT PANEL — switches on mode query param
# ═══════════════════════════════════════════════════════
with col_main:
    # ── Render top tabs selector ──
    st.markdown(make_top_tabs(mode), unsafe_allow_html=True)

    # Invisible buttons placed directly on top of the tab cards
    t_col1, t_col2 = st.columns(2, gap="small")
    with t_col1:
        if st.button("Extract Images", key="sw_extract", use_container_width=True):
            st.query_params["mode"] = "extract"
            st.rerun()
    with t_col2:
        if st.button("Combine Images", key="sw_combine", use_container_width=True):
            st.query_params["mode"] = "combine"
            st.rerun()

    # Content based on mode
    if mode == "extract":
        st.markdown(
            '<span class="rp-eye">Extract Mode</span>'
            '<span class="rp-title">Upload your PDF catalog</span>'
            '<span class="rp-sub">Auto-detects and crops gem entries from single and 4-up layouts.</span>'
            '<span class="rp-label">Catalog File</span>',
            unsafe_allow_html=True,
        )

        uploaded_file = st.file_uploader("PDF", type=["pdf"],
                                         key="ext_pdf", label_visibility="collapsed")

        c1, c2 = st.columns([5, 1], gap="small")
        with c1:
            scan_btn = st.button("Scan Catalog", key="scan_btn", use_container_width=True)
        with c2:
            st.markdown('<div class="btn-sec">', unsafe_allow_html=True)
            rescan_btn = st.button("Re-scan", key="rescan_btn", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        if uploaded_file:
            file_bytes = uploaded_file.read()
            fname      = uploaded_file.name

            if fname != st.session_state.upload_fname:
                st.session_state.upload_fname   = fname
                st.session_state.gem_registry   = {}
                st.session_state.selected_snos  = []
                st.session_state.cover_page_jpg = None

            if rescan_btn:
                st.session_state.gem_registry   = {}
                st.session_state.selected_snos  = []
                st.session_state.cover_page_jpg = None
                st.rerun()

            needs_scan = (scan_btn or not st.session_state.gem_registry) and bool(file_bytes)

            if needs_scan:
                st.markdown('<div class="rp-divider"></div>', unsafe_allow_html=True)
                st.markdown(
                    '<div class="scan-row"><div class="scan-dot"></div>'
                    'Scanning pages and removing borders…</div>'
                    '<div class="prog-track"><div class="prog-bar"></div></div>',
                    unsafe_allow_html=True,
                )
                counter  = st.empty()
                doc      = fitz.open(stream=file_bytes, filetype="pdf")
                total    = len(doc)
                registry = {}

                # Cover page from doc[0] before loop
                cover_pix = doc[0].get_pixmap(matrix=fitz.Matrix(RENDER_ZOOM, RENDER_ZOOM))
                cover_arr = np.frombuffer(cover_pix.samples, dtype=np.uint8).reshape(
                    cover_pix.height, cover_pix.width, cover_pix.n)
                cover_buf = io.BytesIO()
                Image.fromarray(cover_arr[:, :, :3]).save(cover_buf, "JPEG", quality=92)
                st.session_state.cover_page_jpg = cover_buf.getvalue()

                for pn in range(total):
                    counter.markdown(
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
                counter.empty()
                st.session_state.gem_registry = registry
                st.rerun()

            reg = st.session_state.gem_registry

            if not reg:
                st.warning("No S.No entries detected in this PDF.")
            else:
                st.markdown('<div class="rp-divider"></div>', unsafe_allow_html=True)
                st.markdown(
                    f'<div class="rp-row">'
                    f'<span class="rp-label" style="margin-bottom:0">Select Serial Numbers</span>'
                    f'<span class="rp-pill">💎 {len(reg)} entries found</span>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
                selected = st.multiselect(
                    "s", options=sorted(reg.keys()),
                    default=[s for s in st.session_state.selected_snos if s in reg],
                    format_func=lambda x: f"S.No {x}",
                    placeholder="Type to search or click to select…",
                    label_visibility="collapsed",
                )
                st.session_state.selected_snos = selected

                if selected:
                    st.markdown('<div class="rp-divider"></div>', unsafe_allow_html=True)
                    st.markdown(
                        f'<div class="rp-row">'
                        f'<span class="rp-label" style="margin-bottom:0">Preview</span>'
                        f'<span class="rp-pill">{len(selected)} selected</span>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )
                    for pair in [selected[i:i+2] for i in range(0, len(selected), 2)]:
                        img_cols = st.columns(len(pair), gap="small")
                        for col, sno in zip(img_cols, pair):
                            with col:
                                st.image(reg[sno], caption=f"S.No {sno}",
                                         use_container_width=True)

                    st.markdown('<div class="rp-divider"></div>', unsafe_allow_html=True)
                    st.markdown('<span class="rp-label">Export</span>', unsafe_allow_html=True)

                    # Catalog name input
                    base_name = st.session_state.upload_fname.removesuffix(".pdf").removesuffix(".PDF")
                    catalog_name = st.text_input(
                        "Catalog name (used as PDF filename)",
                        value=base_name,
                        placeholder="e.g. Ruby Mozambique Geneve 2026",
                        label_visibility="collapsed",
                    )
                    st.markdown(
                        '<div class="rp-label" style="margin-top:4px;margin-bottom:10px;">'
                        'Catalog Name — used as the downloaded filename</div>',
                        unsafe_allow_html=True,
                    )

                    include_cover = st.checkbox(
                        "Include cover page (first page of PDF)",
                        value=True,
                    )

                    st.markdown('<p class="rp-note" style="margin-top:10px;">'
                                f'{len(selected)} entr{"y" if len(selected)==1 else "ies"} '
                                f'selected — one per page, full-bleed.</p>',
                                unsafe_allow_html=True)

                    if st.button("📄 Generate Selection PDF", key="gen_extract",
                                 use_container_width=True):
                        with st.spinner(""):
                            pages = []
                            if include_cover and st.session_state.cover_page_jpg:
                                pages.append(st.session_state.cover_page_jpg)
                            pages.extend(reg[sno] for sno in selected)
                            pdf_bytes = build_pdf(pages)

                        dl_name = f"{catalog_name.strip() or base_name} Selection Catalog.pdf"
                        st.download_button(
                            "⬇️ Download Catalog PDF",
                            data=pdf_bytes,
                            file_name=dl_name,
                            mime="application/pdf",
                            use_container_width=True,
                        )
                        st.markdown('<div style="margin-top:8px;"></div>', unsafe_allow_html=True)
                        st.markdown('<div class="btn-sec">', unsafe_allow_html=True)
                        if st.button("🗑️ Clear All & Start Over", key="clear_extract",
                                     use_container_width=True):
                            st.session_state.gem_registry   = {}
                            st.session_state.selected_snos  = []
                            st.session_state.cover_page_jpg = None
                            st.session_state.upload_fname   = ""
                            st.rerun()
                        st.markdown('</div>', unsafe_allow_html=True)

    elif mode == "combine":
        st.markdown(
            '<span class="rp-eye">Combine Mode</span>'
            '<span class="rp-title">Build a PDF from images</span>'
            '<span class="rp-sub">Upload multiple images in any order — each becomes one full-bleed page.</span>',
            unsafe_allow_html=True,
        )

        # ── Step 1: Gem images ─────────────────────────
        st.markdown('<span class="rp-label">Gem Images</span>', unsafe_allow_html=True)
        gem_images = st.file_uploader(
            "Upload gem images (PNG, JPG, WEBP)",
            type=["png", "jpg", "jpeg", "webp"],
            accept_multiple_files=True,
            key="comb_gems",
            label_visibility="collapsed",
        )

        st.markdown('<div class="rp-divider"></div>', unsafe_allow_html=True)

        # ── Step 2: Optional cover page ────────────────
        st.markdown(
            '<span class="rp-label">Cover Page (Optional)</span>'
            '<p class="rp-note" style="margin-bottom:10px;">'
            'Upload a single image — it will be inserted as the very first page.</p>',
            unsafe_allow_html=True,
        )
        cover_img = st.file_uploader(
            "Upload cover image",
            type=["png", "jpg", "jpeg", "webp"],
            key="comb_cover",
            label_visibility="collapsed",
        )

        if cover_img:
            st.image(cover_img, caption="Cover page preview", width=240)

        st.markdown('<div class="rp-divider"></div>', unsafe_allow_html=True)

        # ── Step 3: Catalog name ────────────────────────
        st.markdown(
            '<span class="rp-label">Catalog Name</span>'
            '<p class="rp-note" style="margin-bottom:10px;">'
            'This name will be the downloaded filename.</p>',
            unsafe_allow_html=True,
        )
        comb_catalog_name = st.text_input(
            "Name your catalog PDF",
            placeholder="e.g. Ruby Mozambique Collection 2026",
            key="comb_name",
            label_visibility="collapsed",
        )

        if gem_images:
            st.markdown(
                f'<p class="rp-note">'
                f'{len(gem_images)} image{"s" if len(gem_images)>1 else ""} ready'
                f'{" + cover page" if cover_img else ""}. '
                f'Each image becomes one full-bleed A4 page.</p>',
                unsafe_allow_html=True,
            )

            # Preview thumbnails in rows of 4
            st.markdown('<div class="rp-divider"></div>', unsafe_allow_html=True)
            st.markdown('<span class="rp-label">Preview Order</span>', unsafe_allow_html=True)
            for row_imgs in [gem_images[i:i+4] for i in range(0, len(gem_images), 4)]:
                thumb_cols = st.columns(len(row_imgs), gap="small")
                for col, f in zip(thumb_cols, row_imgs):
                    with col:
                        st.image(f, caption=f.name, use_container_width=True)

            st.markdown('<div class="rp-divider"></div>', unsafe_allow_html=True)

            if st.button("📄 Generate Combined PDF", key="gen_combine",
                         use_container_width=True):
                with st.spinner(""):
                    pages_jpg = []

                    # Cover page first
                    if cover_img:
                        cover_img.seek(0)
                        pil_cover = Image.open(cover_img).convert("RGB")
                        cb = io.BytesIO()
                        pil_cover.save(cb, "JPEG", quality=92)
                        pages_jpg.append(cb.getvalue())

                    # Gem images in upload order
                    for f in gem_images:
                        f.seek(0)
                        pil_img = Image.open(f).convert("RGB")
                        gb = io.BytesIO()
                        pil_img.save(gb, "JPEG", quality=92)
                        pages_jpg.append(gb.getvalue())

                    pdf_bytes = build_pdf(pages_jpg)

                dl_name = f"{comb_catalog_name.strip() or 'Gem Catalog'}.pdf"
                st.download_button(
                    "⬇️ Download Combined PDF",
                    data=pdf_bytes,
                    file_name=dl_name,
                    mime="application/pdf",
                    use_container_width=True,
                )
                st.markdown('<div style="margin-top:8px;"></div>', unsafe_allow_html=True)
                st.markdown('<div class="btn-sec">', unsafe_allow_html=True)
                if st.button("🗑️ Clear All & Start Over", key="clear_combine",
                             use_container_width=True):
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("Upload gem images above to get started.")
