import streamlit as st
import fitz  # PyMuPDF
import re, io
import numpy as np

st.set_page_config(page_title="Lunawat Gem Catalog Builder", layout="centered")
st.title("💎 Gem Catalog Builder")
st.write("Upload a catalog PDF → select S.No(s) → preview and export.")

# ── constants ─────────────────────────────────────────────────────────────────
RENDER_ZOOM  = 2.5   # render resolution multiplier
VORONOI_STEP = 4     # grid sample pitch in points

# ── session state ─────────────────────────────────────────────────────────────
if "gem_registry" not in st.session_state:
    st.session_state.gem_registry = {}

# ── helpers ───────────────────────────────────────────────────────────────────

def _nearest_label(pts: np.ndarray, centers: np.ndarray) -> np.ndarray:
    """
    Pure-numpy vectorised nearest-neighbour (no scipy).
    pts     : (N, 2)
    centers : (M, 2)
    returns : (N,) index array
    """
    diff  = pts[:, None, :] - centers[None, :, :]  # (N, M, 2)
    dist2 = (diff ** 2).sum(axis=2)                 # (N, M)
    return dist2.argmin(axis=1)                      # (N,)


def _extract_sno_labels(page: fitz.Page):
    """Return [(s_no, cx, cy), …] for every S.No label found on the page."""
    labels = []
    for block in page.get_text("dict")["blocks"]:
        if block["type"] != 0:
            continue
        for line in block["lines"]:
            text = "".join(s["text"] for s in line["spans"])
            m = re.search(r'S\.No[-\s]*(\d+)', text, re.IGNORECASE)
            if m:
                x0, y0, x1, y1 = line["bbox"]
                labels.append((m.group(1), (x0 + x1) / 2, (y0 + y1) / 2))
    return labels


def _voronoi_rects(page: fitz.Page, labels: list) -> dict:
    """
    Partition page area among N S.No labels using nearest-neighbour Voronoi.
    Works for any number of items per page (1, 2, 3, 4, 6, …).
    Returns {s_no: fitz.Rect}
    """
    pw, ph = page.rect.width, page.rect.height

    if len(labels) == 1:
        return {labels[0][0]: page.rect}

    # Sample grid
    xs = np.arange(0, pw, VORONOI_STEP, dtype=np.float32)
    ys = np.arange(0, ph, VORONOI_STEP, dtype=np.float32)
    xx, yy = np.meshgrid(xs, ys)
    pts = np.column_stack([xx.ravel(), yy.ravel()])           # (N, 2)
    centers = np.array([(cx, cy) for _, cx, cy in labels],
                       dtype=np.float32)                       # (M, 2)

    indices = _nearest_label(pts, centers)

    result = {}
    for i, (sno, _, _) in enumerate(labels):
        cell = pts[indices == i]
        x0 = max(0.0, float(cell[:, 0].min()))
        y0 = max(0.0, float(cell[:, 1].min()))
        x1 = min(pw,  float(cell[:, 0].max()) + VORONOI_STEP)
        y1 = min(ph,  float(cell[:, 1].max()) + VORONOI_STEP)
        result[sno] = fitz.Rect(x0, y0, x1, y1)

    return result


def _render_region(page: fitz.Page, rect: fitz.Rect) -> bytes:
    mat = fitz.Matrix(RENDER_ZOOM, RENDER_ZOOM)
    pix = page.get_pixmap(matrix=mat, clip=rect)
    return pix.tobytes("jpg")


def scan_pdf(file_bytes: bytes) -> dict:
    registry = {}
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    for page_num in range(len(doc)):
        page   = doc[page_num]
        labels = _extract_sno_labels(page)
        if not labels:
            continue
        rects = _voronoi_rects(page, labels)
        for sno, rect in rects.items():
            registry[sno] = _render_region(page, rect)
    doc.close()
    return registry

# ── UI ────────────────────────────────────────────────────────────────────────
uploaded_file = st.file_uploader("Upload Master Catalog PDF", type=["pdf"])

if uploaded_file:
    file_bytes = uploaded_file.read()

    if st.sidebar.button("🔄 Re-scan PDF"):
        st.session_state.gem_registry = {}

    if not st.session_state.gem_registry:
        with st.spinner("Scanning PDF…"):
            st.session_state.gem_registry = scan_pdf(file_bytes)
        st.success(f"Found **{len(st.session_state.gem_registry)}** gem entries.")

    registry = st.session_state.gem_registry
    if not registry:
        st.warning("No S.No entries found in this PDF.")
        st.stop()

    sorted_snos = sorted(registry.keys())
    selected = st.multiselect(
        "Select S.No(s) to preview / export:",
        options=sorted_snos,
        format_func=lambda x: f"S.No {x}",
    )

    if selected:
        st.markdown("---")
        st.subheader("Preview")
        pairs = [selected[i:i+2] for i in range(0, len(selected), 2)]
        for pair in pairs:
            cols = st.columns(len(pair))
            for col, sno in zip(cols, pair):
                with col:
                    st.image(registry[sno], caption=f"S.No {sno}",
                             use_container_width=True)

        st.markdown("---")
        if st.button("📄 Generate & Download Selection PDF"):
            with st.spinner("Building PDF…"):
                out = fitz.open()
                for sno in selected:
                    pg = out.new_page(width=595, height=842)
                    pg.insert_text(fitz.Point(40, 45),
                                   f"Lunawat Gems — S.No {sno}",
                                   fontsize=14, color=(0, 0, 0))
                    pg.insert_image(fitz.Rect(40, 65, 555, 780),
                                    stream=registry[sno])
                buf = io.BytesIO()
                out.save(buf)
                buf.seek(0)
            st.download_button(
                "⬇️ Download Selection PDF",
                data=buf,
                file_name="LGC_Selection_Catalog.pdf",
                mime="application/pdf",
            )
