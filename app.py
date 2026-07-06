import streamlit as st
import fitz
import re, io
import numpy as np
from PIL import Image

st.set_page_config(
    page_title="Lunawat Gem Catalog",
    layout="wide",                   # <-- wide so card fills the screen
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

.block-container {
    max-width: 100% !important;
    padding: 0 !important;
}

/* ── Card: the outer columns row ── */
[data-testid="stMainBlockContainer"]
  [data-testid="stHorizontalBlock"]:first-of-type {
    border-radius: 14px !important;
    overflow: hidden !important;
    box-shadow: 0 4px 28px rgba(0,0,0,0.13) !important;
    gap: 0 !important;
    align-items: stretch !important;
    min-height: calc(100vh - 100px) !important;
}

/* ── LEFT: dark sidebar ── */
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
    padding: 44px 28px !important;
    gap: 0 !important;
}

/* ── RIGHT: white content ── */
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
    padding: 44px 52px 40px !important;
    gap: 0 !important;
}

/* ── Nested columns inside right panel: reset ALL ── */
[data-testid="stMainBlockContainer"]
  [data-testid="stHorizontalBlock"]:first-of-type
  > [data-testid="stColumn"]:last-child
  [data-testid="stHorizontalBlock"] {
    border-radius: 0 !important;
    box-shadow: none !important;
    overflow: visible !important;
    min-height: unset !important;
    gap: 8px !important;
}
[data-testid="stMainBlockContainer"]
  [data-testid="stHorizontalBlock"]:first-of-type
  > [data-testid="stColumn"]:last-child
  [data-testid="stColumn"] {
    background: transparent !important;
    min-width: unset !important;
    max-width: unset !important;
    flex-shrink: 1 !important;
}
[data-testid="stMainBlockContainer"]
  [data-testid="stHorizontalBlock"]:first-of-type
  > [data-testid="stColumn"]:last-child
  [data-testid="stColumn"]
  > [data-testid="stVerticalBlock"] {
    padding: 0 !important;
    max-width: unset !important;
}

/* ── Global ── */
[data-testid="stVerticalBlock"] { gap: 0 !important; }
.stMarkdown { margin-bottom: 0 !important; }

/* ── Sidebar text ── */
.sb-brand {
    font-size:10px; font-weight:700; letter-spacing:.2em;
    color:#3E5270; text-transform:uppercase;
    margin-bottom:20px; display:block;
}
.sb-title {
    font-size:20px; font-weight:700; color:#fff;
    line-height:1.3; margin-bottom:40px; display:block;
}
.step { display:flex; align-items:center; gap:12px; padding:10px 0; position:relative; }
.step:not(:last-child)::after {
    content:''; position:absolute; left:9px; top:34px;
    width:2px; height:20px; background:#1E2D45;
}
.d-a { width:20px;height:20px;border-radius:50%;flex-shrink:0;
        background:#3B82F6;box-shadow:0 0 0 4px rgba(59,130,246,.2); }
.d-d { width:20px;height:20px;border-radius:50%;flex-shrink:0;
        background:transparent;border:2px solid #3B82F6; }
.d-p { width:20px;height:20px;border-radius:50%;flex-shrink:0;
        background:#1C2B40;border:2px solid #26394F; }
.l-a { font-size:13px;font-weight:600;color:#fff; }
.l-d { font-size:13px;font-weight:500;color:#4B7BCA; }
.l-p { font-size:13px;font-weight:400;color:#334E6A; }

/* ── Right panel typography ── */
.rp-eye   { font-size:10px;font-weight:700;letter-spacing:.16em;color:#3B82F6;
             text-transform:uppercase;display:block;margin-bottom:6px; }
.rp-title { font-size:24px;font-weight:700;color:#0F172A;
             letter-spacing:-.02em;display:block;margin-bottom:4px; }
.rp-sub   { font-size:13px;color:#94A3B8;display:block;margin-bottom:28px; }
.rp-label { font-size:10px;font-weight:700;letter-spacing:.12em;color:#B8C5D4;
             text-transform:uppercase;display:block;margin-bottom:8px; }
.rp-divider { height:1px;background:#F1F5F9;margin:22px 0; }
.rp-row   { display:flex;justify-content:space-between;align-items:center;margin-bottom:10px; }
.rp-pill  { display:inline-flex;align-items:center;gap:4px;background:#EFF6FF;color:#1D4ED8;
             font-size:11px;font-weight:600;padding:3px 10px;border-radius:999px; }
.rp-note  { font-size:13px;color:#64748B;margin:6px 0 16px;line-height:1.5; }

/* ── Scan animation ── */
.scan-row { display:flex;align-items:center;gap:8px;
             font-size:13px;color:#475569;margin-bottom:8px; }
.scan-dot { width:7px;height:7px;border-radius:50%;background:#3B82F6;
             flex-shrink:0;animation:sdot 1s ease-in-out infinite; }
@keyframes sdot{0%,100%{opacity:1}50%{opacity:.2}}
.prog-track { height:4px;background:#EEF2FF;border-radius:999px;overflow:hidden; }
.prog-bar   { height:4px;width:45%;border-radius:999px;
               background:linear-gradient(90deg,#3B82F6,#818CF8);
               animation:pbar 1.8s ease-in-out infinite; }
@keyframes pbar{0%{transform:translateX(-120%)}100%{transform:translateX(300%)}}
.pg-count { font-size:11px;color:#94A3B8;margin-top:4px; }

/* ── Widgets ── */
[data-testid="stFileUploader"] {
    border:1.5px solid #E2E8F0 !important; border-radius:9px !important;
    background:#FAFBFC !important; padding:2px 10px !important; margin-bottom:14px !important;
}
[data-testid="stFileUploader"] section { padding:4px 0 !important; }

[data-testid="stMultiSelect"]>div>div {
    border:1.5px solid #E2E8F0 !important; border-radius:8px !important;
    font-size:13px !important; min-height:42px !important; background:#FAFBFC !important;
}
[data-testid="stMultiSelect"]>div>div:focus-within {
    border-color:#3B82F6 !important; box-shadow:0 0 0 3px rgba(59,130,246,.1) !important;
}

/* Primary button */
[data-testid="stButton"]>button {
    background:#2563EB !important; color:#fff !important; border:none !important;
    border-radius:8px !important; font-size:13px !important; font-weight:600 !important;
    height:42px !important; width:100% !important; transition:background .15s !important;
}
[data-testid="stButton"]>button:hover { background:#1D4ED8 !important; }

/* Secondary (Re-scan) — fixed width, never clips */
.btn-sec [data-testid="stButton"]>button {
    background:#F1F5F9 !important; color:#475569 !important;
    width:100px !important; min-width:100px !important;
}
.btn-sec [data-testid="stButton"]>button:hover { background:#E2E8F0 !important; }

/* Download */
[data-testid="stDownloadButton"]>button {
    background:#059669 !important; color:#fff !important; border:none !important;
    border-radius:8px !important; font-size:13px !important; font-weight:600 !important;
    height:42px !important; width:100% !important;
}
[data-testid="stDownloadButton"]>button:hover { background:#047857 !important; }

[data-testid="stImage"] img {
    border-radius:8px !important; box-shadow:0 2px 12px rgba(0,0,0,.09) !important;
}
[data-testid="stImage"]>div>div {
    font-size:11px !important; color:#94A3B8 !important;
    text-align:center !important; margin-top:5px !important;
}
[data-testid="stAlert"]   { border-radius:8px !important; font-size:13px !important; }
[data-testid="stSpinner"] > div { display:none !important; }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════
# UNCHANGED CORE LOGIC
# ═══════════════════════════════════════════════════════
GRID_X, GRID_Y, RENDER_ZOOM = 360, 277, 2.5

if "gem_registry"   not in st.session_state: st.session_state.gem_registry   = {}
if "selected_snos"  not in st.session_state: st.session_state.selected_snos  = []
if "cover_page_jpg" not in st.session_state: st.session_state.cover_page_jpg = None
if "upload_fname"   not in st.session_state: st.session_state.upload_fname   = ""


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


# ═══════════════════════════════════════════════════════
# STEP STATES
# ═══════════════════════════════════════════════════════
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
    dc = {"active":"d-a","done":"d-d","pending":"d-p"}
    lc = {"active":"l-a","done":"l-d","pending":"l-p"}
    rows = "".join(
        f'<div class="step"><div class="{dc[ss(i)]}"></div>'
        f'<span class="{lc[ss(i)]}">{lbl}</span></div>'
        for i, lbl in enumerate(STEPS)
    )
    return (
        f'<span class="sb-brand">Lunawat Gems</span>'
        f'<span class="sb-title">Gem Catalog<br>Builder</span>'
        f'{rows}'
    )


# ═══════════════════════════════════════════════════════
# LAYOUT  — columns ratio gives ~240px left on wide layout
# ═══════════════════════════════════════════════════════
col_sb, col_main = st.columns([16, 84], gap="small")

with col_sb:
    st.markdown(make_sidebar(), unsafe_allow_html=True)

with col_main:
    st.markdown(
        '<span class="rp-eye">Catalog Builder</span>'
        '<span class="rp-title">Upload your PDF catalog</span>'
        '<span class="rp-sub">Supports single-item and multi-item (4-up) layouts.</span>'
        '<span class="rp-label">Catalog File</span>',
        unsafe_allow_html=True,
    )

    uploaded_file = st.file_uploader("PDF", type=["pdf"], label_visibility="collapsed")

    c1, c2 = st.columns([5, 1], gap="small")
    with c1:
        scan_btn = st.button("Scan Catalog", use_container_width=True)
    with c2:
        st.markdown('<div class="btn-sec">', unsafe_allow_html=True)
        rescan_btn = st.button("Re-scan", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    if uploaded_file:
        file_bytes = uploaded_file.read()
        fname      = uploaded_file.name

        # Detect file change → clear all previous state immediately
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

            # Render cover page from the already-open doc (page 0)
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
                "s",
                options=sorted(reg.keys()),
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
                st.markdown(
                    f'<span class="rp-label">Export</span>'
                    f'<p class="rp-note"><strong>{len(selected)}</strong> '
                    f'entr{"y" if len(selected)==1 else "ies"} selected — '
                    f'one per page, full-bleed, no header text.</p>',
                    unsafe_allow_html=True,
                )

                include_cover = st.checkbox(
                    "Include cover page (first page of PDF)",
                    value=True,
                )

                if st.button("📄 Generate Selection PDF", use_container_width=True):
                    with st.spinner(""):
                        out = fitz.open()

                        # Optional cover page
                        if include_cover and st.session_state.cover_page_jpg:
                            pg = out.new_page(width=595, height=842)
                            pg.insert_image(fitz.Rect(0, 0, 595, 842),
                                            stream=st.session_state.cover_page_jpg)

                        # One gem per page, image fills entire page, no text
                        for sno in selected:
                            pg = out.new_page(width=595, height=842)
                            pg.insert_image(fitz.Rect(0, 0, 595, 842),
                                            stream=reg[sno])

                        buf = io.BytesIO()
                        out.save(buf); buf.seek(0)

                    # Build filename: "<original_name> Selection Catalog.pdf"
                    base = st.session_state.upload_fname
                    if base.lower().endswith(".pdf"):
                        base = base[:-4]
                    dl_name = f"{base} Selection Catalog.pdf"

                    st.download_button(
                        "⬇️ Download Catalog PDF",
                        data=buf,
                        file_name=dl_name,
                        mime="application/pdf",
                        use_container_width=True,
                    )
