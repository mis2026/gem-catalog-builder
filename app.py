import streamlit as st
import fitz  # PyMuPDF
import re
import io
import math

st.set_page_config(page_title="Universal Gem Catalog Builder", layout="centered")

st.title("💎 Universal Gem Catalog Builder")
st.write("Automatically extracts exact image units matching your serial numbers across mixed page grid layouts.")

uploaded_file = st.file_uploader("Upload your Master Catalog PDF", type=["pdf"])

if 'gem_registry' not in st.session_state:
    st.session_state.gem_registry = {}

if uploaded_file is not None:
    if not st.session_state.gem_registry or st.sidebar.button("🔄 Clear & Re-Scan Document"):
        st.session_state.gem_registry = {}
        
        with st.spinner("Executing structural multi-layout parsing algorithm..."):
            doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                # 1. Locate all actual embedded image objects and get their positions
                image_info_list = page.get_image_info(rects=True)
                if not image_info_list:
                    continue
                
                # 2. Extract all S.No text instances and their coordinates
                text_instances = page.search_for("S.No")
                if not text_instances:
                    text_instances = page.search_for("S.NO")
                
                for inst in text_instances:
                    # Expand matching frame context horizontally to read full digits safely
                    text_window = page.get_text("text", clip=fitz.Rect(inst.x0 - 5, inst.y0 - 5, inst.x1 + 180, inst.y1 + 15))
                    s_no_match = re.search(r'\d{4}', text_window)
                    
                    if not s_no_match:
                        continue
                    s_no = s_no_match.group(0)
                    
                    # 3. ADVANCED GEOMETRIC DISTANCE MATCHING
                    # Find the physical image on this page closest to our S.No text label
                    best_img_rect = None
                    min_distance = float('inf')
                    
                    for img in image_info_list:
                        img_rect = fitz.Rect(img['bbox'])
                        
                        # Calculate distance between centers
                        center_text_x = (inst.x0 + inst.x1) / 2
                        center_text_y = (inst.y0 + inst.y1) / 2
                        center_img_x = (img_rect.x0 + img_rect.x1) / 2
                        center_img_y = (img_rect.y0 + img_rect.y1) / 2
                        
                        distance = math.sqrt((center_text_x - center_img_x)**2 + (center_text_y - center_img_y)**2)
                        
                        # Tie-breaker: Prioritize images that are directly ABOVE or next to the text
                        if img_rect.y1 <= inst.y0 + 50: 
                            distance -= 150 # Bias boost for expected layout mapping
                            
                        if distance < min_distance:
                            min_distance = distance
                            best_img_rect = img_rect
                    
                    # 4. Extract and Save the Best Matched Box
                    if best_img_rect:
                        # Add minimal safety padding around the embedded picture boundaries
                        crop_rect = fitz.Rect(
                            best_img_rect.x0 - 5,
                            best_img_rect.y0 - 5,
                            max(best_img_rect.x1 + 5, inst.x1 + 10), # Include text label at the bottom safely
                            max(best_img_rect.y1 + 5, inst.y1 + 10)
                        )
                        
                        # Cap bounds to fit physical page limits
                        if crop_rect.y0 < 0: crop_rect.y0 = 0
                        if crop_rect.x0 < 0: crop_rect.x0 = 0
                        if crop_rect.y1 > page.rect.height: crop_rect.y1 = page.rect.height
                        if crop_rect.x1 > page.rect.width: crop_rect.x1 = page.rect.width
                        
                        zoom = 2.5  
                        mat = fitz.Matrix(zoom, zoom)
                        pix = page.get_pixmap(matrix=mat, clip=crop_rect)
                        
                        st.session_state.gem_registry[s_no] = pix.tobytes("jpg")
                        
        st.success(f"Successfully configured and mapped {len(st.session_state.gem_registry)} dynamic items!")

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
                with st.spinner("Compiling structural profile output page blocks..."):
                    output_pdf = fitz.open()
                    
                    for s_no in selected_gems:
                        new_page = output_pdf.new_page(width=595, height=842)
                        new_page.insert_text(fitz.Point(40, 50), f"Gemstone Selection Profile — S.No {s_no}", fontsize=16, color=(0,0,0))
                        
                        img_bytes = st.session_state.gem_registry[s_no]
                        display_window = fitz.Rect(40, 90, 555, 750)
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
