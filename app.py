import streamlit as st
import fitz  # PyMuPDF
import re
import io

st.set_page_config(page_title="Lunawat Gem Catalog Builder", layout="centered")
st.title("💎 Gem Catalog Builder")
st.write("Upload a catalog PDF, then select S.No(s) to preview and download a custom PDF.")

# ─── Constants ────────────────────────────────────────────────────────────────
# All pages are 720 × 554.4 pt (landscape).
# Multi-item (4-up) pages have a grid divider at these coordinates:
GRID_X = 360   # left/right column boundary
GRID_Y = 277   # top/bottom row boundary
RENDER_ZOOM = 2.5  # render resolution multiplier

# ─── Session state ─────────────────────────────────────────────────────────────
if "gem_registry" not in st.session_state:
    st.session_state.gem_registry = {}   # {s_no: bytes(jpg)}

# ─── Helpers ───────────────────────────────────────────────────────────────────

def _crop_and_render(page: fitz.Page, rect: fitz.Rect) -> bytes:
    """Render a clipped region of a page to JPEG bytes."""
    mat = fitz.Matrix(RENDER_ZOOM, RENDER_ZOOM)
    pix = page.get_pixmap(matrix=mat, clip=rect)
    return pix.tobytes("jpg")


def _quadrant_rect(page: fitz.Page, text_bbox) -> fitz.Rect:
    """
    Return the full-quadrant fitz.Rect for a 4-up page based on where the
    S.No text label sits (determined by GRID_X / GRID_Y thresholds).
    """
    pw, ph = page.rect.width, page.rect.height
    x0_label = text_bbox[0]
    y0_label = text_bbox[1]

    left  = x0_label < GRID_X
    top   = y0_label < GRID_Y

    if left and top:
        return fitz.Rect(0,      0,      GRID_X, GRID_Y)
    elif not left and top:
        return fitz.Rect(GRID_X, 0,      pw,     GRID_Y)
    elif left and not top:
        return fitz.Rect(0,      GRID_Y, GRID_X, ph)
    else:
        return fitz.Rect(GRID_X, GRID_Y, pw,     ph)


def _single_page_rect(page: fitz.Page, text_bbox) -> fitz.Rect:
    """
    For single-item pages the entire page is the card.
    We just return the full page rect (PyMuPDF clips cleanly at page boundary).
    """
    return page.rect


def scan_pdf(file_bytes: bytes) -> dict:
    """
    Parse every page of the PDF and return a mapping of
    {s_no_string: jpg_bytes} for every gem entry found.
    """
    registry = {}
    doc = fitz.open(stream=file_bytes, filetype="pdf")

    for page_num in range(len(doc)):
        page = doc[page_num]
        text_dict = page.get_text("dict")

        # Collect lines that contain an S.No label
        sno_lines = []
        for block in text_dict["blocks"]:
            if block["type"] != 0:
                continue
            for line in block["lines"]:
                line_text = "".join(s["text"] for s in line["spans"])
                # Match both "S.NO-" and "S.No-" formats followed by digits
                m = re.search(r'S\.No[-\s]*(\d+)', line_text, re.IGNORECASE)
                if m:
                    sno_lines.append((m.group(1), line["bbox"]))

        if not sno_lines:
            continue  # cover page or blank

        is_multi = len(sno_lines) > 1  # 4-up layout if more than one entry

        for s_no, bbox in sno_lines:
            if is_multi:
                crop_rect = _quadrant_rect(page, bbox)
            else:
                crop_rect = _single_page_rect(page, bbox)

            registry[s_no] = _crop_and_render(page, crop_rect)

    doc.close()
    return registry

# ─── File upload ───────────────────────────────────────────────────────────────
uploaded_file = st.file_uploader("Upload Master Catalog PDF", type=["pdf"])

if uploaded_file is not None:
    file_bytes = uploaded_file.read()

    rescan = st.sidebar.button("🔄 Re-scan PDF")
    if not st.session_state.gem_registry or rescan:
        with st.spinner("Scanning PDF and mapping gem entries…"):
            st.session_state.gem_registry = scan_pdf(file_bytes)
        st.success(f"Found **{len(st.session_state.gem_registry)}** gem entries.")

    registry = st.session_state.gem_registry

    if not registry:
        st.warning("No S.No entries detected in this PDF.")
        st.stop()

    # ─── Selection UI ─────────────────────────────────────────────────────────
    sorted_snos = sorted(registry.keys())

    selected = st.multiselect(
        "Select S.No(s) to preview / include in export:",
        options=sorted_snos,
        format_func=lambda x: f"S.No {x}",
    )

    # ─── Preview selected items ───────────────────────────────────────────────
    if selected:
        st.markdown("---")
        st.subheader("Preview")

        # Two-column preview grid
        col_pairs = [selected[i:i+2] for i in range(0, len(selected), 2)]
        for pair in col_pairs:
            cols = st.columns(len(pair))
            for col, sno in zip(cols, pair):
                with col:
                    st.image(registry[sno], caption=f"S.No {sno}", use_container_width=True)

        # ─── Export PDF ───────────────────────────────────────────────────────
        st.markdown("---")
        if st.button("📄 Generate & Download Selection PDF"):
            with st.spinner("Building PDF…"):
                out_pdf = fitz.open()
                for sno in selected:
                    # Portrait A4: 595 × 842 pt
                    new_page = out_pdf.new_page(width=595, height=842)
                    new_page.insert_text(
                        fitz.Point(40, 45),
                        f"Lunawat Gems — S.No {sno}",
                        fontsize=14,
                        color=(0, 0, 0),
                    )
                    display_rect = fitz.Rect(40, 65, 555, 780)
                    new_page.insert_image(display_rect, stream=registry[sno])

                buf = io.BytesIO()
                out_pdf.save(buf)
                buf.seek(0)

            st.download_button(
                label="⬇️ Download Selection Catalog PDF",
                data=buf,
                file_name="LGC_Selection_Catalog.pdf",
                mime="application/pdf",
            )
