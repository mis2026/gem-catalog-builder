import streamlit as st
import fitz  # PyMuPDF
import re
import io

st.set_page_config(page_title="Universal Gem Catalog Builder", layout="centered")

st.title("💎 Universal Gem Catalog Builder")
st.write("Smart Vector Border Tracking Engine. Automatically detects black frame lines surrounding your item selections.")

uploaded_file = st.file_uploader("Upload your Master Catalog PDF", type=["pdf"])

if 'gem_registry' not in st.session_state:
    st.session_state.gem_registry = {}

if uploaded_file is not None:
    if not st.session_state.gem_registry or st.sidebar.button("🔄 Clear & Re-Scan Document"):
        st.session_state.gem_registry = {}
        
        with st.spinner("Scanning vector frames and mapping black border cards..."):
            doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                page_width = page.rect.width
                page_height = page.rect.height
                
                # 1. Fetch all vector shapes and rectangles drawn on this page
                drawings = page.get_drawings()
                border_rects = []
                
                for draw in drawings:
                    # Look for rectangular paths or closed lines that frame boxes
                    if draw["type"] == "s" or draw["type"] == "f" or draw["type"] == "fs":
                        for path in draw["items"]:
                            if path[0] == "re":  # "re" means it's a structural rectangle line
                                border_rects.append(fitz.Rect(path[1]))
                
                # 2. Search for the S.No flags
                text_instances = page.search_for("S.No-")
                if not text_instances:
                    text_instances = page.search_for("S.NO-")
                if not text_instances:
                    text_instances = page.search_for("S.No")
                if not text_instances:
                    text_instances = page.search_for("S.NO")
                
                if not text_instances:
                    continue
                
                for inst in text_instances:
                    # Read the serial number digits safely
                    text_window = page.get_text("text", clip=fitz.Rect(inst.x0 - 5, inst.y0 - 5, inst.x1 + 220, inst.y1 + 25))
                    s_no_match = re.search(r'\d{4}', text_window)
                    
                    if not s_no_match:
                        continue
                    s_no = s_no_match.group(0)
                    
                    # 3. VECTOR BORDER SNAP LOGIC
                    # Find which drawn rectangle completely encloses or contains this text marker
                    matched_box = None
                    
                    for r in border_rects:
                        # If the S.No text center point sits inside this rectangle path frame
                        center_x = (inst.x0 + inst.x1) / 2
                        center_y = (inst.y0 + inst.y1) / 2
                        
                        # We give a slight leeway for overlapping borders or margins
                        if r.x0 - 15 <= center_x <= r.x1 + 15 and r.y0 - 400 <= center_y <= r.y1 + 50:
                            matched_box = r
                            break
                    
                    # 4. Fallback Grid Layout Anchor (If a page happens to use flat image backgrounds instead of vectors)
                    if not matched_box:
                        is_left_column = inst.x0 < (page_width / 2)
                        if is_left_column:
                            matched_box = fitz.Rect(max(0, inst.x0 - 30), max(0, inst.y0 - 390), min(page_width, inst.x0 + 285), min(page_height, inst.y1 + 50))
                        else:
                            matched_box = fitz.Rect(max(0, inst.x0 - 180), max(0, inst.y0 - 390), min(page_width, inst.x1 + 180), min(page_height, inst.y1 + 50))
                    
                    # Apply minimal padding to clean up the frame lines
                    crop_rect = fitz.Rect(
                        max(0, matched_box.x0 - 5),
                        max(0, matched_box.y0 - 5),
                        min(page_width, matched_box.x1 + 5),
                        min(page_height, matched_box.y1 + 5)
                    )
                    
                    # Render image snapshot 
                    zoom = 2.5  
                    mat = fitz.Matrix(zoom, zoom)
                    pix = page.get_pixmap(matrix=mat, clip=crop_rect)
                    
                    st.session_state.gem_registry[s_no] = pix.tobytes("jpg")
                    
        st.success(f"Successfully located and boxed {len(st.session_state.gem_registry)} item borders!")

    # UI Dropdown Selector
    if st.session_state.gem_registry:
        available_items = sorted(list(st.session_state.gem_registry.keys()))
        
        selected_gems = st.multiselect(
            "Select which Serial Numbers you want in your final download:",
            options=available_items,
            format_func=lambda x: f"Item S.No: {x}"
        )
        
        # Compile Selection PDF Generator
        if selected_gems:
            if st.button("Generate & Download My Custom PDF"):
                with st.spinner("Assembling custom layout catalog..."):
                    output_pdf = fitz.open()
                    
                    for s_no in selected_gems:
                        new_page = output_pdf.new_page(width=595, height=842)
                        new_page.insert_text(fitz.Point(40, 50), f"Gemstone Selection Profile — S.No {s_no}", fontsize=16, color=(0,0,0))
                        
                        img_bytes = st.session_state.gem_registry[s_no]
                        
                        display_window = fitz.Rect(40, 80, 555, 780)
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
