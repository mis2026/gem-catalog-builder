import streamlit as st
import fitz  # PyMuPDF
import re
import io

st.set_page_config(page_title="Global Gem Catalog Builder", layout="centered")

st.title("💎 Universal Gem Catalog Builder")
st.write("Upload your catalog PDF. The system will automatically crop the gemstone pictures above each serial number block so you can compile a custom PDF.")

# 1. File Uploader Component
uploaded_file = st.file_uploader("Upload your Master Catalog PDF", type=["pdf"])

# Persistent session memory to prevent losing images when changing selections
if 'gem_registry' not in st.session_state:
    st.session_state.gem_registry = {}

if uploaded_file is not None:
    # If a new file is dropped, scan its page coordinates
    if not st.session_state.gem_registry or st.sidebar.button("🔄 Clear & Re-Scan Document"):
        st.session_state.gem_registry = {}
        
        with st.spinner("Analyzing layout grid and cropping gem boxes..."):
            doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                # Lowercase match tracking to catch "S.No-", "S.NO-", or "S.No "
                text_instances = page.search_for("S.No")
                if not text_instances:
                    text_instances = page.search_for("S.NO")

                for inst in text_instances:
                    # Look at a small window around the text to grab the serial number cleanly
                    text_window = page.get_text("text", clip=fitz.Rect(inst.x0, inst.y0, inst.x1 + 120, inst.y1 + 15))
                    s_no_match = re.search(r'\d{4}', text_window)
                    
                    if not s_no_match:
                        continue
                    s_no = s_no_match.group(0)
                    
                    # --- GRID CROPPING MATH FOR YOUR LAYOUT ---
                    # Because the image sits ABOVE the serial text box:
                    crop_rect = fitz.Rect(
                        inst.x0 - 20,    # Left boundary line
                        inst.y0 - 260,   # Reach UP 260 pixels to capture the gem photo
                        inst.x0 + 260,   # Right boundary line
                        inst.y1 + 140    # Capture the text details below it too
                    )
                    
                    # Prevent going past actual page boundaries
                    if crop_rect.y0 < 0: crop_rect.y0 = 0
                    if crop_rect.x0 < 0: crop_rect.x0 = 0
                    
                    # Render high quality crisp snap
                    zoom = 2  
                    mat = fitz.Matrix(zoom, zoom)
                    pix = page.get_pixmap(matrix=mat, clip=crop_rect)
                    
                    # Save image into browser storage memory
                    st.session_state.gem_registry[s_no] = pix.tobytes("jpg")
                    
        st.success(f"Loaded {len(st.session_state.gem_registry)} gem items from your document successfully!")

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
                        # Append blank sheet (A4 Dimension: 595 width x 842 height)
                        new_page = output_pdf.new_page(width=595, height=842)
                        
                        # Add a clean headline text marker
                        new_page.insert_text(fitz.Point(40, 50), f"Gemstone Selection Profile — S.No {s_no}", fontsize=16, color=(0,0,0))
                        
                        # Fetch cropped image segment bytes
                        img_bytes = st.session_state.gem_registry[s_no]
                        
                        # Place image onto the page nicely centered
                        display_window = fitz.Rect(40, 80, 555, 650)
                        new_page.insert_image(display_window, stream=img_bytes)
                    
                    # Output compiling pipeline stream
                    pdf_buffer = io.BytesIO()
                    output_pdf.save(pdf_buffer)
                    pdf_buffer.seek(0)
                    
                    st.download_button(
                        label="⬇️ Click here to Download Selection Catalog PDF",
                        data=pdf_buffer,
                        file_name="Selected_Gems_Report.pdf",
                        mime="application/pdf"
                    )