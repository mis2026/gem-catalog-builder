import streamlit as st
import fitz  # PyMuPDF
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

/* ── Hard reset ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body {
    font-family: 'Inter', sans-serif;
    height: 100%;
    overflow: hidden;
}

/* Kill all streamlit chrome */
#MainMenu, footer, header, [data-testid="stDecoration"],
[data-testid="stToolbar"], [data-testid="stSidebar"] { display: none !important; }

/* Full-viewport container */
[data-testid="stAppViewContainer"] {
    height: 100vh;
    overflow: hidden;
    padding: 0 !important;
}
[data-testid="stMain"] {
    height: 100vh;
    overflow: hidden;
    padding: 0 !important;
}
.block-container {
    height: 100vh;
    max-width: 100% !important;
    padding: 0 !important;
    overflow: hidden;
}

/* ── The two-column wrapper ── */
[data-testid="stHorizontalBlock"] {
    height: 100vh !important;
    gap: 0 !important;
    align-items: stretch !important;
}

/* ── LEFT PANEL ── */
[data-testid="stHorizontalBlock"] > div:nth-child(1) {
    background: #151C2C !important;
    height: 100vh !important;
    overflow: hidden !important;
    padding: 0 !important;
    flex-shrink: 0 !important;
}
[data-testid="stHorizontalBlock"] > div:nth-child(1) > div {
    height: 100% !important;
    padding: 0 !important;
}

/* ── RIGHT PANEL ── */
[data-testid="stHorizontalBlock"] > div:nth-child(2) {
    background: #F0F2F6 !important;
    height: 100vh !important;
    overflow-y: auto !important;
    padding: 0 !important;
}
[data-testid="stHorizontalBlock"] > div:nth-child(2) > div {
    padding: 0 !important;
}

/* ── Sidebar HTML block fills column ── */
.sidebar-wrap {
    background: #151C2C;
    height: 100vh;
    width: 100%;
    padding: 40px 28px;
    display: flex;
    flex-direction: column;
}
.sidebar-logo {
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.16em;
    color: #5B6B8A;
    text-transform: uppercase;
    margin-bottom: 24px;
}
.sidebar-title {
    font-size: 20px;
    font-weight: 700;
    color: #FFFFFF;
    line-height: 1.3;
    margin-bottom: 40px;
}
.step-list { display: flex; flex-direction: column; }
.step-row {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 10px 0;
    position: relative;
}
.step-row:not(:last-child)::after {
    content: '';
    position: absolute;
    left: 9px;
    top: 34px;
    width: 2px;
    height: 20px;
    background: #263047;
}
.dot-active {
    width: 20px; height: 20px; border-radius: 50%; flex-shrink: 0;
    background: #3B82F6;
    box-shadow: 0 0 0 4px rgba(59,130,246,0.18);
}
.dot-done {
    width: 20px; height: 20px; border-radius: 50%; flex-shrink: 0;
    background: transparent;
    border: 2px solid #3B82F6;
}
.dot-pending {
    width: 20px; height: 20px; border-radius: 50%; flex-shrink: 0;
    background: #263047;
    border: 2px solid #374158;
}
.lbl-active { font-size: 13px; font-weight: 600; color: #FFFFFF; }
.lbl-done   { font-size: 13px; font-weight: 500; color: #4B7BCA; }
.lbl-pending{ font-size: 13px; font-weight: 400; color: #3D4F6A; }

/* ── Right content inner padding ── */
.content-wrap {
    padding: 36px 48px;
    max-width: 860px;
}
.eyebrow {
    font-size: 10px; font-weight: 700; letter-spacing: 0.14em;
    color: #3B82F6; text-transform: uppercase; margin-bottom: 6px;
}
.page-title {
    font-size: 24px; font-weight: 700; color: #0F172A;
    letter-spacing: -0.02em; margin-bottom: 4px;
}
.page-sub { font-size: 13px; color: #64748B; margin-bottom: 24px; }

/* ── Card ── */
.card {
    background: #FFFFFF;
    border-radius: 14px;
    padding: 24px 28px;
    box-shadow: 0 1px 2px rgba(0,0,0,0.05), 0 2px 10px rgba(0,0,0,0.04);
    margin-bottom: 16px;
}
.card-label {
    font-size: 10px; font-weight: 700; letter-spacing: 0.12em;
    color: #94A3B8; text-transform: uppercase; margin-bottom: 14px;
}
.card-row {
    display: flex; justify-content: space-between;
    align-items: center; margin-bottom: 14px;
}
.pill {
    display: inline-flex; align-items: center; gap: 5px;
    background: #EFF6FF; color: #1D4ED8;
    font-size: 11px; font-weight: 600;
    padding: 4px 10px; border-radius: 999px;
}
.export-note {
    font-size: 13px; color: #64748B; margin-bottom: 16px; line-height: 1.5;
}

/* ── File uploader ── */
[data-testid="stFileUploader"] {
    background: #F8FAFC;
    border: 1.5px dashed #CBD5E1;
    border-radius: 10px;
    padding: 4px 8px;
}
[data-testid="stFileUploader"]:hover { border-color: #3B82F6; }
[data-testid="stFileUploader"] section { padding: 8px 0 !important; }

/* ── Multiselect ── */
[data-testid="stMultiSelect"] > div > div {
    border-radius: 8px !important;
    border: 1.5px solid #E2E8F0 !important;
    font-size: 13px !important;
    min-height: 40px !important;
}

/* ── Primary button ── */
[data-testid="stButton"] > button {
    background: #1D4ED8 !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 8px !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    padding: 10px 20px !important;
    height: 42px !important;
    transition: background 0.15s !important;
    width: 100% !important;
}
[data-testid="stButton"] > button:hover {
    background: #1E40AF !important;
}

/* ── Download button ── */
[data-testid="stDownloadButton"] > button {
    background: #0F9B5E !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 8px !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    height: 42px !important;
    width: 100% !important;
}
[data-testid="stDownloadButton"] > button:hover {
    background: #0A7A4A !important;
}

/* Re-scan secondary */
.rescan [data-testid="stButton"] > button {
    background: #E2E8F0 !important;
    color: #334155 !important;
    font-size: 12px !important;
    height: 42px !important;
}
.rescan [data-testid="stButton"] > button:hover {
    background: #CBD5E1 !important;
}

/* ── Images ── */
[data-testid="stImage"] img {
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.10);
}

/* Alert */
[data-testid="stAlert"] { border-radius: 8px !important; font-size: 13px !important; }

/* Spinner */
[data-testid="stSpinner"] { font-size: 13px !important; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# UNCHANGED CORE LOGIC
# ══════════════════════════════════════════════════════════════════════════════
GRID_X      = 360
GRID_Y      = 277
RENDER_ZOOM = 2.5

if "gem_registry"   not in st.session_state: st.session_state.gem_registry   = {}
if "selected_snos"  not in st.session_state: st.session_state.selected_snos  = []

def _crop_and_render(page: fitz.Page, rect: fitz.Rect) -> bytes:
    mat = fitz.Matrix(RENDER_ZOOM, RENDER_ZOOM)
    pix = page.get_pixmap(matrix=mat, clip=rect)
    return pix.tobytes("jpg")

def _quadrant_rect(page: fitz.Page, text_bbox) -> fitz.Rect:
    pw, ph   = page.rect.width, page.rect.height
    left     = text_bbox[0] < GRID_X
    top      = text_bbox[1] < GRID_Y
    if left  and top:     return fitz.Rect(0,      0,      GRID_X, GRID_Y)
    if not left and top:  return fitz.Rect(GRID_X, 0,      pw,     GRID_Y)
    if left  and not top: return fitz.Rect(0,      GRID_Y, GRID_X, ph)
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
                line_text = "".join(s["text"] for s in line["spans"])
                m = re.search(r'S\.No[-\s]*(\d+)', line_text, re.IGNORECASE)
                if m:
                    sno_lines.append((m.group(1), line["bbox"]))
        if not sno_lines: continue
        is_multi = len(sno_lines) > 1
        for s_no, bbox in sno_lines:
            crop_rect      = _quadrant_rect(page, bbox) if is_multi else _single_page_rect(page, bbox)
            registry[s_no] = _crop_and_render(page, crop_rect)
    doc.close()
    return registry


# ══════════════════════════════════════════════════════════════════════════════
# STEP STATE
# ══════════════════════════════════════════════════════════════════════════════
registry = st.session_state.gem_registry
has_scan = bool(registry)
has_sel  = bool(st.session_state.selected_snos) and has_scan

def ss(i):                   # "active" | "done" | "pending"
    if i == 0: return "done"   if has_scan else "active"
    if i == 1:
        if has_sel:  return "done"
        if has_scan: return "active"
        return "pending"
    if i == 2: return "active" if has_sel else "pending"
    if i == 3: return "active" if has_sel else "pending"

steps = ["Upload", "Select S.No", "Preview", "Export PDF"]


# ══════════════════════════════════════════════════════════════════════════════
# LAYOUT
# ══════════════════════════════════════════════════════════════════════════════
left_col, right_col = st.columns([22, 78], gap="small")

# ── LEFT: sidebar ─────────────────────────────────────────────────────────────
with left_col:
    dot_cls = {s: f"dot-{s}" for s in ("active","done","pending")}
    lbl_cls = {s: f"lbl-{s}" for s in ("active","done","pending")}

    rows_html = ""
    for i, label in enumerate(steps):
        s = ss(i)
        rows_html += f"""
        <div class="step-row">
            <div class="{dot_cls[s]}"></div>
            <span class="{lbl_cls[s]}">{label}</span>
        </div>"""

    st.markdown(f"""
    <div class="sidebar-wrap">
        <div class="sidebar-logo">Lunawat Gems</div>
        <div class="sidebar-title">Gem Catalog<br>Builder</div>
        <div class="step-list">{rows_html}</div>
    </div>""", unsafe_allow_html=True)

# ── RIGHT: content ────────────────────────────────────────────────────────────
with right_col:
    st.markdown('<div class="content-wrap">', unsafe_allow_html=True)

    # Header
    st.markdown("""
    <div class="eyebrow">Catalog Builder</div>
    <div class="page-title">Upload your PDF catalog</div>
    <div class="page-sub">Supports single-item and multi-item (4-up) layouts automatically.</div>
    """, unsafe_allow_html=True)

    # ── Upload card ───────────────────────────────────────────────────────────
    st.markdown('<div class="card"><div class="card-label">Catalog File</div>', unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "PDF", type=["pdf"], label_visibility="collapsed"
    )

    c1, c2 = st.columns([4, 1], gap="small")
    with c1:
        scan_btn = st.button("Scan Catalog", use_container_width=True)
    with c2:
        st.markdown('<div class="rescan">', unsafe_allow_html=True)
        rescan_btn = st.button("🔄 Re-scan", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)  # /card

    # ── Scan logic ────────────────────────────────────────────────────────────
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

        # auto-scan on first upload
        if not st.session_state.gem_registry and file_bytes:
            with st.spinner("Scanning pages…"):
                st.session_state.gem_registry = scan_pdf(file_bytes)
            st.rerun()

        registry = st.session_state.gem_registry

        if not registry:
            st.warning("No S.No entries detected in this PDF.")
        else:
            # ── Select card ───────────────────────────────────────────────────
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown(f"""
            <div class="card-row">
                <div class="card-label" style="margin-bottom:0">Select Serial Numbers</div>
                <div class="pill">💎 {len(registry)} entries found</div>
            </div>""", unsafe_allow_html=True)

            selected = st.multiselect(
                "snos", options=sorted(registry.keys()),
                default=[s for s in st.session_state.selected_snos if s in registry],
                format_func=lambda x: f"S.No {x}",
                placeholder="Type to search or click to select…",
                label_visibility="collapsed",
            )
            st.session_state.selected_snos = selected
            st.markdown('</div>', unsafe_allow_html=True)  # /card

            # ── Preview card ──────────────────────────────────────────────────
            if selected:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.markdown(f"""
                <div class="card-row">
                    <div class="card-label" style="margin-bottom:0">Preview</div>
                    <div class="pill">{len(selected)} selected</div>
                </div>""", unsafe_allow_html=True)

                for pair in [selected[i:i+2] for i in range(0, len(selected), 2)]:
                    cols = st.columns(len(pair), gap="small")
                    for col, sno in zip(cols, pair):
                        with col:
                            st.image(registry[sno], caption=f"S.No {sno}",
                                     use_container_width=True)

                st.markdown('</div>', unsafe_allow_html=True)  # /card

                # ── Export card ───────────────────────────────────────────────
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.markdown('<div class="card-label">Export</div>', unsafe_allow_html=True)
                st.markdown(
                    f'<p class="export-note">Generate a single PDF with '
                    f'<strong>{len(selected)}</strong> selected gem entr'
                    f'{"y" if len(selected)==1 else "ies"}, one per page.</p>',
                    unsafe_allow_html=True,
                )

                if st.button("📄 Generate Selection PDF", use_container_width=True):
                    with st.spinner("Building PDF…"):
                        out = fitz.open()
                        for sno in selected:
                            pg = out.new_page(width=595, height=842)
                            pg.insert_text(fitz.Point(40,45),
                                           f"Lunawat Gems — S.No {sno}",
                                           fontsize=14, color=(0,0,0))
                            pg.insert_image(fitz.Rect(40,65,555,780),
                                            stream=registry[sno])
                        buf = io.BytesIO()
                        out.save(buf); buf.seek(0)

                    st.download_button(
                        "⬇️  Download Catalog PDF",
                        data=buf,
                        file_name="LGC_Selection_Catalog.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                    )

                st.markdown('</div>', unsafe_allow_html=True)  # /card

    st.markdown('</div>', unsafe_allow_html=True)  # /content-wrap
