import streamlit as st
import fitz  # PyMuPDF
import re
import io

st.set_page_config(page_title="Universal Gem Catalog Builder", layout="centered")

st.title("💎 Universal Gem Catalog Builder")
st.write("Layout-Agnostic Extraction Engine. Perfectly extracts your custom selections from mixed multi-image catalogs.")

uploaded_file = st.file_uploader("Upload your Master Catalog PDF", type=["pdf"])

if 'gem_registry' not in st.session_state:
    st.session_state.gem_registry = {}

if uploaded_file is not None:
    if not st.session_state.gem_registry or st.sidebar.button("🔄 Clear & Re-Scan Document"):
        st.session_state.gem_registry = {}
        
        with st.spinner("Executing precise grid coordinates mapping... Please wait."):
            doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                page_width = page.rect.width
                page_height = page.rect.height
                
                # Check for all text formatting rules matching your catalog files
                text_instances = page.search_for("S.No")
                if not text_instances:
                    text_instances = page.search_for("S.NO")
                
                if not text_instances:
                    continue
                
                # Filter out duplicate overlapping matches in the same vicinity
                unique_instances = []
                for inst in text_instances:
                    if not any(abs(inst.y0 - u.y0) < 10 and abs(inst.x0 - u.x0) < 10 for u in unique_instances):
                        unique_instances.append(inst)
                
                for inst in unique_instances:
                    # Capture wide reading window to grab the true digits reliably
                    text_window = page.get_text("text", clip=fitz.Rect(max(0, inst.x0 - 10), max(0, inst.y0 - 5), min(page_width, inst.x1 + 250), min(page_height, inst.y1 + 35)))
                    s_no_match = re.search(r'\d{4}', text_window)
                    
                    if not s_no_match:
                        continue
                    s_no = s_no_match.group(0)
                    
                    # --- FIXED GRID MATH BASED ON YOUR UPLOADED FILE ---
                    # Detect layout type (left side item, right side item, or full width single item)
                    is_left_side = inst.x0 < (page_width * 0.45)
                    is_right_side = inst.x0 > (page_width * 0.55)
                    
                    if is_left_side and not is_right_side:
                        # Left block grid boundaries 
                        x_min = 15
                        x_max = (page_width / 2) + 10
                        y_min = max(0, inst.y0 - 330)
                        y_max = min(page_height, inst.y1 + 140)
                    elif is_right_side:
                        # Right block grid boundaries
                        x_min = (page_width / 2) - 10
                        x_max = page_width - 15
                        y_min = max(0, inst.y0 - 330)
                        y_max = min(page_height, inst.y1 + 140)
                    else:
                        # Full-page single item grid boundaries
                        x_min = 15
                        x_max = page_width - 15
                        y_min = max(0, inst.y0 - 360)
                        y_max = min(page_height, inst.y1 + 160)
                    
                    crop_rect = fitz.Rect(x_min, y_min, x_max, y_max)
                    
                    # High quality extraction mapping zoom factor
                    zoom = 2.5  
                    mat = fitz.Matrix(zoom, zoom)
                    pix = page.get_pixmap(matrix=mat, clip=crop_rect)
                    
                    st.session_state.gem_registry[s_no] = pix.tobytes("jpg")
                    
        st.success(f"Successfully configured and mapped {len(st.session_state.gem_registry)} items cleanly!")

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
                with st.spinner("Compiling structural profile output page blocks..."):
                    output_pdf = fitz.open()
                    
                    for s_no in selected_gems:
                        new_page = output_pdf.new_page(width=595, height=842)
                        new_page.insert_text(fitz.Point(40, 50), f"Gemstone Selection Profile — S.No {s_no}", fontsize=16, color=(0,0,0))
                        
                        img_bytes = st.session_state.gem_registry[s_no]
                        
                        # Set layout frame sizes elegantly preserving clarity
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
