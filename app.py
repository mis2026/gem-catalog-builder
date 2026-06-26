import streamlit as st
import fitz  # PyMuPDF
import re
import io

st.set_page_config(page_title="Global Gem Catalog Builder", layout="centered")

st.title("💎 Universal Gem Catalog Builder")
st.write("Upload your catalog PDF. The system will extract full item blocks cleanly by tracking structural layout boundaries.")

# 1. File Uploader Component
uploaded_file = st.file_uploader("Upload your Master Catalog PDF", type=["pdf"])

if 'gem_registry' not in st.session_state:
    st.session_state.gem_registry = {}

if uploaded_file is not None:
    if not st.session_state.gem_registry or st.sidebar.button("🔄 Clear & Re-Scan Document"):
        st.session_state.gem_registry = {}
        
        with st.spinner("Smart-scanning page blocks to extract perfect boundaries..."):
            doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                # Get ALL structural layout blocks on the page (text + images grouped naturally)
                # "blocks" returns a list of tuples: (x0, y0, x1, y1, "text content", block_no, block_type)
                text_blocks = page.get_text("blocks")
                
                for block in text_blocks:
                    block_text = block[4] # The text inside this layout boundary
                    
                    # Check if "S.No" or "S.NO" is written inside this block
                    if "S.No" in block_text or "S.NO" in block_text:
                        s_no_match = re.search(r'\d{4}', block_text)
                        if not s_no_match:
                            continue
                        s_no = s_no_match.group(0)
                        
                        # --- BLOCK-BASED BOUNDARY HACK ---
                        # Instead of guessing offsets, we take the exact box of the block!
                        # We expand it outward by a safe, minimal padding (e.g., 15-20 pixels) 
                        # to ensure none of the stone edges are clipped.
                        crop_rect = fitz.Rect(
                            block[0] - 20,  # Left edge of block minus padding
                            block[1] - 150, # Lift higher up to catch the full image height inside this zone
                            block[2] + 20,  # Right edge of block plus padding
                            block[3] + 20   # Bottom edge of block plus padding
                        )
                        
                        # Bound check against physical page limitations
                        if crop_rect.y0 < 0: crop_rect.y0 = 0
                        if crop_rect.x0 < 0: crop_rect.x0 = 0
                        if crop_rect.y1 > page.rect.height: crop_rect.y1 = page.rect.height
                        if crop_rect.x1 > page.rect.width: crop_rect.x1 = page.rect.width
                        
                        # Render high quality crisp snap
                        zoom = 2.5  # Slightly higher zoom for crisper gem details
                        mat = fitz.Matrix(zoom, zoom)
                        pix = page.get_pixmap(matrix=mat, clip=crop_rect)
                        
                        # Save clean image into memory
                        st.session_state.gem_registry[s_no] = pix.tobytes("jpg")
                        
        st.success(f"Perfectly mapped {len(st.session_state.gem_registry)} full gem blocks!")

    # 2. Dropdown UI Selector
    if st.session_state.gem_registry:
        available_items = sorted(list(st.session_state.gem_registry.keys()))
        
        selected_gems = st.multiselect(
            "Select which Serial Numbers you want in your final download:",
            options=available_items,
            format_func=lambda x: f"Item S.No: {x}"
        )
        
        # 3. Compile Selection PDF Generator
        if selected_gems:
            if st.button("Generate & Download My Custom PDF"):
                with st.spinner("Compiling pages..."):
                    output_pdf = fitz.open()
                    
                    for s_no in selected_gems:
                        new_page = output_pdf.new_page(width=595, height=842)
                        
                        new_page.insert_text(fitz.Point(40, 50), f"Gemstone Selection Profile — S.No {s_no}", fontsize=16, color=(0,0,0))
                        
                        img_bytes = st.session_state.gem_registry[s_no]
                        
                        # Centered display window frame preserving clarity
                        display_window = fitz.Rect(40, 90, 555, 600)
                        new_page.insert_image(display_window, stream=img_bytes)
                    
                    pdf_buffer = io.BytesIO()
                    output_pdf.save(pdf_buffer)
                    pdf_buffer.seek(0)
                    
                    st.download_button(
                        label="⬇️ Click here to Download Selection Catalog PDF",
                        data=pdf_buffer,
                        file_name="Selected_Gems_Report.pdf",
                        mime="application/pdf"
                    )
