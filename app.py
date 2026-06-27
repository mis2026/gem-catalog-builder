import streamlit as st
import fitz  # PyMuPDF
import re
import io

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Lunawat Gem Catalog",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Reset & base ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [data-testid="stAppViewContainer"] {
    font-family: 'Inter', sans-serif;
    background: #F0F2F5;
}

/* Hide default streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stSidebar"] { display: none; }
[data-testid="stDecoration"] { display: none; }
.block-container {
    padding: 0 !important;
    max-width: 100% !important;
}

/* ── Layout shell ── */
.app-shell {
    display: flex;
    min-height: 100vh;
    background: #F0F2F5;
}

/* ── Left sidebar panel ── */
.sidebar-panel {
    width: 260px;
    min-width: 260px;
    background: #151C2C;
    padding: 48px 32px;
    display: flex;
    flex-direction: column;
    gap: 0;
}

.sidebar-logo {
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.18em;
    color: #6B7A99;
    text-transform: uppercase;
    margin-bottom: 40px;
}

.sidebar-title {
    font-size: 18px;
    font-weight: 700;
    color: #FFFFFF;
    margin-bottom: 48px;
    letter-spacing: -0.01em;
    line-height: 1.3;
}

.step-list {
    display: flex;
    flex-direction: column;
    gap: 0;
}

.step-item {
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 14px 0;
    position: relative;
}

.step-item:not(:last-child)::after {
    content: '';
    position: absolute;
    left: 9px;
    top: 38px;
    width: 2px;
    height: calc(100% - 14px);
    background: #263047;
}

.step-dot {
    width: 20px;
    height: 20px;
    border-radius: 50%;
    flex-shrink: 0;
    position: relative;
    z-index: 1;
}

.step-dot.active {
    background: #3B82F6;
    box-shadow: 0 0 0 4px rgba(59,130,246,0.2);
}

.step-dot.done {
    background: #1E3A5F;
    border: 2px solid #3B82F6;
}

.step-dot.pending {
    background: #263047;
    border: 2px solid #374158;
}

.step-label {
    font-size: 13px;
    font-weight: 500;
}

.step-label.active { color: #FFFFFF; }
.step-label.done   { color: #4B7BCA; }
.step-label.pending{ color: #4A5568; }

/* ── Right content panel ── */
.content-panel {
    flex: 1;
    padding: 56px 64px;
    display: flex;
    flex-direction: column;
}

.content-header {
    margin-bottom: 36px;
}

.content-eyebrow {
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.14em;
    color: #3B82F6;
    text-transform: uppercase;
    margin-bottom: 8px;
}

.content-title {
    font-size: 26px;
    font-weight: 700;
    color: #0F172A;
    letter-spacing: -0.02em;
    margin-bottom: 6px;
}

.content-sub {
    font-size: 14px;
    color: #64748B;
    font-weight: 400;
}

/* ── Card ── */
.card {
    background: #FFFFFF;
    border-radius: 16px;
    padding: 36px 40px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06), 0 4px 16px rgba(0,0,0,0.04);
    margin-bottom: 24px;
}

/* ── Upload zone ── */
[data-testid="stFileUploader"] {
    background: #F8FAFC;
    border: 2px dashed #CBD5E1;
    border-radius: 12px;
    padding: 8px;
    transition: border-color 0.2s;
}
[data-testid="stFileUploader"]:hover {
    border-color: #3B82F6;
}
[data-testid="stFileUploader"] label {
    font-size: 14px !important;
    font-weight: 600 !important;
    color: #0F172A !important;
}

/* ── Multiselect ── */
[data-testid="stMultiSelect"] > div > div {
    border-radius: 10px !important;
    border: 1.5px solid #E2E8F0 !important;
    font-size: 14px !important;
    background: #FAFAFA !important;
}
[data-testid="stMultiSelect"] > div > div:focus-within {
    border-color: #3B82F6 !important;
    box-shadow: 0 0 0 3px rgba(59,130,246,0.12) !important;
}

/* ── Buttons ── */
[data-testid="stButton"] > button,
[data-testid="stDownloadButton"] > button {
    background: #1D4ED8 !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 10px !important;
    font-size: 14px !important;
    font-weight: 600 !important;
    padding: 12px 28px !important;
    letter-spacing: 0.01em !important;
    transition: background 0.15s, transform 0.1s !important;
    width: 100% !important;
}
[data-testid="stButton"] > button:hover,
[data-testid="stDownloadButton"] > button:hover {
    background: #1E40AF !important;
    transform: translateY(-1px) !important;
}

/* Re-scan button – secondary style */
.rescan-btn [data-testid="stButton"] > button {
    background: #F1F5F9 !important;
    color: #334155 !important;
    font-size: 13px !important;
    padding: 10px 20px !important;
    width: auto !important;
}
.rescan-btn [data-testid="stButton"] > button:hover {
    background: #E2E8F0 !important;
    transform: none !important;
}

/* ── Success / info banners ── */
[data-testid="stAlert"] {
    border-radius: 10px !important;
    font-size: 14px !important;
}

/* ── Preview images ── */
[data-testid="stImage"] img {
    border-radius: 10px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.10);
}

/* ── Divider ── */
hr { border-color: #E2E8F0; margin: 28px 0; }

/* ── Stat badge ── */
.stat-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: #EFF6FF;
    color: #1D4ED8;
    font-size: 12px;
    font-weight: 600;
    padding: 5px 12px;
    border-radius: 999px;
    letter-spacing: 0.02em;
}

/* ── Section label ── */
.section-label {
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.12em;
    color: #94A3B8;
    text-transform: uppercase;
    margin-bottom: 12px;
}

/* ── Caption under preview images ── */
[data-testid="stImage"] > div > div {
    font-size: 12px !important;
    color: #64748B !important;
    font-weight: 500 !important;
    text-align: center !important;
}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# UNCHANGED CORE LOGIC
# ══════════════════════════════════════════════════════════════════════════════

GRID_X      = 360
GRID_Y      = 277
RENDER_ZOOM = 2.5

if "gem_registry" not in st.session_state:
    st.session_state.gem_registry = {}

def _crop_and_render(page: fitz.Page, rect: fitz.Rect) -> bytes:
    mat = fitz.Matrix(RENDER_ZOOM, RENDER_ZOOM)
    pix = page.get_pixmap(matrix=mat, clip=rect)
    return pix.tobytes("jpg")

def _quadrant_rect(page: fitz.Page, text_bbox) -> fitz.Rect:
    pw, ph    = page.rect.width, page.rect.height
    x0_label  = text_bbox[0]
    y0_label  = text_bbox[1]
    left      = x0_label < GRID_X
    top       = y0_label < GRID_Y
    if left and top:
        return fitz.Rect(0,      0,      GRID_X, GRID_Y)
    elif not left and top:
        return fitz.Rect(GRID_X, 0,      pw,     GRID_Y)
    elif left and not top:
        return fitz.Rect(0,      GRID_Y, GRID_X, ph)
    else:
        return fitz.Rect(GRID_X, GRID_Y, pw,     ph)

def _single_page_rect(page: fitz.Page, text_bbox) -> fitz.Rect:
    return page.rect

def scan_pdf(file_bytes: bytes) -> dict:
    registry = {}
    doc      = fitz.open(stream=file_bytes, filetype="pdf")
    for page_num in range(len(doc)):
        page      = doc[page_num]
        text_dict = page.get_text("dict")
        sno_lines = []
        for block in text_dict["blocks"]:
            if block["type"] != 0:
                continue
            for line in block["lines"]:
                line_text = "".join(s["text"] for s in line["spans"])
                m = re.search(r'S\.No[-\s]*(\d+)', line_text, re.IGNORECASE)
                if m:
                    sno_lines.append((m.group(1), line["bbox"]))
        if not sno_lines:
            continue
        is_multi = len(sno_lines) > 1
        for s_no, bbox in sno_lines:
            crop_rect        = _quadrant_rect(page, bbox) if is_multi else _single_page_rect(page, bbox)
            registry[s_no]  = _crop_and_render(page, crop_rect)
    doc.close()
    return registry


# ══════════════════════════════════════════════════════════════════════════════
# DETERMINE STEP STATE
# ══════════════════════════════════════════════════════════════════════════════

registry  = st.session_state.gem_registry
has_scan  = bool(registry)
# We'll track selected in session state too so it persists between reruns
if "selected_snos" not in st.session_state:
    st.session_state.selected_snos = []

has_sel   = bool(st.session_state.selected_snos) and has_scan

# Step states: "active" | "done" | "pending"
def step_state(index):
    # 0 = Upload, 1 = Select, 2 = Preview, 3 = Export
    if index == 0:
        return "done"   if has_scan else "active"
    if index == 1:
        if has_sel:   return "done"
        if has_scan:  return "active"
        return "pending"
    if index == 2:
        if has_sel:   return "active"
        return "pending"
    if index == 3:
        return "active" if has_sel else "pending"

steps = ["Upload", "Select S.No", "Preview", "Export PDF"]


# ══════════════════════════════════════════════════════════════════════════════
# RENDER LAYOUT
# ══════════════════════════════════════════════════════════════════════════════

# Build sidebar HTML
step_html = ""
for i, label in enumerate(steps):
    s = step_state(i)
    step_html += f"""
    <div class="step-item">
        <div class="step-dot {s}"></div>
        <span class="step-label {s}">{label}</span>
    </div>"""

sidebar_html = f"""
<div class="sidebar-panel">
    <div class="sidebar-logo">Lunawat Gems</div>
    <div class="sidebar-title">Gem Catalog<br>Builder</div>
    <div class="step-list">{step_html}</div>
</div>"""

# Two-column layout: sidebar | content
left_col, right_col = st.columns([1, 3], gap="small")

with left_col:
    st.markdown(sidebar_html, unsafe_allow_html=True)

with right_col:
    # ── STEP 1: Upload ────────────────────────────────────────────────────────
    st.markdown("""
    <div class="content-header">
        <div class="content-eyebrow">Catalog Builder</div>
        <div class="content-title">Upload your PDF catalog</div>
        <div class="content-sub">Supports single-item and multi-item (4-up) layouts automatically.</div>
    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-label">Catalog File</div>', unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Drop your master catalog PDF here",
        type=["pdf"],
        label_visibility="collapsed",
    )

    col_scan, col_rescan = st.columns([3, 1])
    with col_scan:
        scan_btn = st.button("Scan Catalog", use_container_width=True)
    with col_rescan:
        st.markdown('<div class="rescan-btn">', unsafe_allow_html=True)
        rescan_btn = st.button("🔄 Re-scan")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)  # close card

    if uploaded_file:
        file_bytes = uploaded_file.read()

        if rescan_btn:
            st.session_state.gem_registry   = {}
            st.session_state.selected_snos  = []

        if (scan_btn or not st.session_state.gem_registry) and file_bytes:
            with st.spinner("Scanning pages and mapping gem entries…"):
                st.session_state.gem_registry = scan_pdf(file_bytes)
            registry = st.session_state.gem_registry

        registry = st.session_state.gem_registry

        if not registry:
            st.warning("No S.No entries detected in this PDF.")
            st.stop()

        # ── STEP 2: Select ────────────────────────────────────────────────────
        st.markdown('<div class="card">', unsafe_allow_html=True)

        count = len(registry)
        st.markdown(f"""
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;">
            <div class="section-label" style="margin-bottom:0">Select Serial Numbers</div>
            <div class="stat-badge">💎 {count} entries found</div>
        </div>""", unsafe_allow_html=True)

        sorted_snos = sorted(registry.keys())
        selected = st.multiselect(
            "Choose S.No(s)",
            options=sorted_snos,
            default=st.session_state.selected_snos,
            format_func=lambda x: f"S.No {x}",
            placeholder="Type to search or click to select…",
            label_visibility="collapsed",
        )
        st.session_state.selected_snos = selected

        st.markdown('</div>', unsafe_allow_html=True)  # close card

        # ── STEP 3 & 4: Preview + Export ──────────────────────────────────────
        if selected:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown(f"""
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;">
                <div class="section-label" style="margin-bottom:0">Preview</div>
                <div class="stat-badge">{len(selected)} selected</div>
            </div>""", unsafe_allow_html=True)

            pairs = [selected[i:i+2] for i in range(0, len(selected), 2)]
            for pair in pairs:
                cols = st.columns(len(pair))
                for col, sno in zip(cols, pair):
                    with col:
                        st.image(
                            registry[sno],
                            caption=f"S.No {sno}",
                            use_container_width=True,
                        )

            st.markdown('</div>', unsafe_allow_html=True)  # close card

            # Export card
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="section-label">Export</div>', unsafe_allow_html=True)
            st.markdown(
                f'<p style="font-size:14px;color:#64748B;margin-bottom:20px;">'
                f'Generate a single PDF containing all <strong>{len(selected)}</strong> '
                f'selected gem entries, one per page.</p>',
                unsafe_allow_html=True,
            )

            if st.button("📄 Generate Selection PDF", use_container_width=True):
                with st.spinner("Assembling your catalog PDF…"):
                    out_pdf = fitz.open()
                    for sno in selected:
                        new_page = out_pdf.new_page(width=595, height=842)
                        new_page.insert_text(
                            fitz.Point(40, 45),
                            f"Lunawat Gems — S.No {sno}",
                            fontsize=14,
                            color=(0, 0, 0),
                        )
                        new_page.insert_image(
                            fitz.Rect(40, 65, 555, 780),
                            stream=registry[sno],
                        )
                    buf = io.BytesIO()
                    out_pdf.save(buf)
                    buf.seek(0)

                st.download_button(
                    label="⬇️ Download Selection Catalog PDF",
                    data=buf,
                    file_name="LGC_Selection_Catalog.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )

            st.markdown('</div>', unsafe_allow_html=True)  # close card

    elif not uploaded_file:
        st.markdown("""
        <div style="padding:48px 0;text-align:center;color:#94A3B8;">
            <div style="font-size:40px;margin-bottom:12px;">📂</div>
            <div style="font-size:14px;font-weight:500;">Upload a PDF to get started</div>
            <div style="font-size:13px;margin-top:6px;">Supports any Lunawat Gems catalog layout</div>
        </div>""", unsafe_allow_html=True)
