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

html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
    font-family: 'Inter', sans-serif !important;
    background: #F7F8FA !important;
}
#MainMenu, footer, header,
[data-testid="stDecoration"],
[data-testid="stToolbar"],
[data-testid="stSidebar"] { display: none !important; }

.block-container { max-width: 720px !important; padding: 48px 24px 64px !important; }

/* File uploader */
[data-testid="stFileUploader"] {
    border: 1.5px solid #E2E8F0 !important;
    border-radius: 10px !important;
    background: #fff !important;
    padding: 4px 12px !important;
}

/* Multiselect */
[data-testid="stMultiSelect"] > div > div {
    border: 1.5px solid #E2E8F0 !important;
    border-radius: 8px !important;
    font-size: 14px !important;
    background: #fff !important;
}
[data-testid="stMultiSelect"] > div > div:focus-within {
    border-color: #3B82F6 !important;
    box-shadow: 0 0 0 3px rgba(59,130,246,.1) !important;
}

/* All buttons */
[data-testid="stButton"] > button {
    border-radius: 8px !important;
    font-size: 14px !important;
    font-weight: 600 !important;
    height: 42px !important;
    border: none !important;
    background: #2563EB !important;
    color: #fff !important;
    width: 100% !important;
    transition: background .15s !important;
}
[data-testid="stButton"] > button:hover { background: #1D4ED8 !important; }

/* Secondary button override via wrapper */
.btn-secondary [data-testid="stButton"] > button {
    background: #F1F5F9 !important;
    color: #334155 !important;
}
.btn-secondary [data-testid="stButton"] > button:hover {
    background: #E2E8F0 !important;
}

/* Download button */
[data-testid="stDownloadButton"] > button {
    border-radius: 8px !important;
    font-size: 14px !important;
    font-weight: 600 !important;
    height: 42px !important;
    border: none !important;
    background: #059669 !important;
    color: #fff !important;
    width: 100% !important;
}
[data-testid="stDownloadButton"] > button:hover { background: #047857 !important; }

/* Images */
[data-testid="stImage"] img {
    border-radius: 10px !important;
    box-shadow: 0 2px 12px rgba(0,0,0,.08) !important;
}

/* Alert */
[data-testid="stAlert"] { border-radius: 8px !important; }

/* Progress text */
.pg-count { font-size: 12px; color: #94A3B8; margin-top: 4px; }
.scan-msg { font-size: 13px; color: #475569; margin-bottom: 6px; }
.prog-track { height: 4px; background: #E2E8F0; border-radius: 999px; overflow: hidden; margin-bottom: 4px; }
.prog-bar {
    height: 4px;
    background: linear-gradient(90deg, #3B82F6, #818CF8);
    border-radius: 999px;
    animation: pbar 1.8s ease-in-out infinite;
    width: 45%;
}
@keyframes pbar {
    0%   { transform: translateX(-120%); }
    100% { transform: translateX(280%); }
}
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
# UI
# ══════════════════════════════════════════════════════════════════════════════
st.title("💎 Gem Catalog Builder")
st.caption("Upload a catalog PDF, select S.No(s), preview and export.")

st.divider()

# ── Upload ────────────────────────────────────────────────────────────────────
uploaded_file = st.file_uploader("Upload catalog PDF", type=["pdf"],
                                 label_visibility="collapsed")

c1, c2 = st.columns([4, 1], gap="small")
with c1:
    scan_btn = st.button("Scan Catalog", use_container_width=True)
with c2:
    st.markdown('<div class="btn-secondary">', unsafe_allow_html=True)
    rescan_btn = st.button("Re-scan", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ── Scan ──────────────────────────────────────────────────────────────────────
if uploaded_file:
    file_bytes = uploaded_file.read()

    if rescan_btn:
        st.session_state.gem_registry  = {}
        st.session_state.selected_snos = []
        st.rerun()

    needs_scan = (scan_btn or not st.session_state.gem_registry) and bool(file_bytes)

    if needs_scan:
        st.markdown('<p class="scan-msg">Scanning pages…</p>', unsafe_allow_html=True)
        st.markdown('<div class="prog-track"><div class="prog-bar"></div></div>',
                    unsafe_allow_html=True)
        counter = st.empty()

        doc      = fitz.open(stream=file_bytes, filetype="pdf")
        total    = len(doc)
        registry = {}

        for pn in range(total):
            counter.markdown(
                f'<div class="pg-count">Page {pn+1} / {total}</div>',
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
        st.divider()

        # ── Select ────────────────────────────────────────────────────────────
        col_a, col_b = st.columns([1, 1])
        with col_a:
            st.markdown(f"**Select S.No** &nbsp; `{len(reg)} entries found`",
                        unsafe_allow_html=True)

        selected = st.multiselect(
            "Select",
            options=sorted(reg.keys()),
            default=[s for s in st.session_state.selected_snos if s in reg],
            format_func=lambda x: f"S.No {x}",
            placeholder="Type to search or click to select…",
            label_visibility="collapsed",
        )
        st.session_state.selected_snos = selected

        if selected:
            st.divider()

            # ── Preview ───────────────────────────────────────────────────────
            st.markdown(f"**Preview** &nbsp; `{len(selected)} selected`",
                        unsafe_allow_html=True)
            st.write("")

            for pair in [selected[i:i+2] for i in range(0, len(selected), 2)]:
                cols = st.columns(len(pair), gap="medium")
                for col, sno in zip(cols, pair):
                    with col:
                        st.image(reg[sno], caption=f"S.No {sno}",
                                 use_container_width=True)

            st.divider()

            # ── Export ────────────────────────────────────────────────────────
            st.markdown(
                f"**Export PDF** — {len(selected)} "
                f"entr{'y' if len(selected)==1 else 'ies'}, one per page.",
            )
            st.write("")

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
