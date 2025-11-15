#!/usr/bin/env python3
"""
E-Book Maker - Streamlit Interface
Alternative to Flask server.py - provides modern, reactive UI
"""

import streamlit as st
import sys
from pathlib import Path
import subprocess
import shutil

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent / 'modules'))

from conversion.converter import EBookConverter
from covers.cover_generator import CoverGenerator
from watermarking.watermarker import Watermarker
from ai.groq_assistant import GroqAssistant

# Utility functions
def check_pandoc_available():
    """Check if Pandoc is installed"""
    return shutil.which('pandoc') is not None

def get_pandoc_version():
    """Get Pandoc version if available"""
    try:
        result = subprocess.run(['pandoc', '--version'], capture_output=True, text=True)
        first_line = result.stdout.split('\n')[0]
        return first_line.replace('pandoc', '').strip()
    except:
        return None

# Page config
st.set_page_config(
    page_title="E-Book Maker",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'ai_assistant' not in st.session_state:
    # SECURITY: Secrets are disabled by default to prevent cloud API key exposure
    # Users must enter their own API keys via the UI
    # For local development only, you can enable secrets by setting allow_secrets=True
    st.session_state.ai_assistant = GroqAssistant()

# Check for system dependencies
if 'pandoc_available' not in st.session_state:
    st.session_state.pandoc_available = check_pandoc_available()
    st.session_state.pandoc_version = get_pandoc_version()

# Sidebar navigation
st.sidebar.title("📚 E-Book Maker")
st.sidebar.markdown("**v2.1.0** - Streamlit Interface")

page = st.sidebar.radio(
    "Navigate:",
    ["🏠 Dashboard", "🔄 Convert Documents", "🎨 Create Covers", "💧 Watermark", "📢 AI Marketing", "🤖 AI Settings"]
)

# System status in sidebar
st.sidebar.markdown("---")
st.sidebar.markdown("### System Status")

# Pandoc status
if st.session_state.pandoc_available:
    st.sidebar.success("✅ Pandoc Available")
else:
    st.sidebar.error("❌ Pandoc Missing")
    st.sidebar.caption("Conversion disabled")

# AI Status
ai_enabled = st.session_state.ai_assistant.is_enabled()
if ai_enabled:
    model_info = st.session_state.ai_assistant.get_current_model_info()
    st.sidebar.success(f"✅ AI: {model_info['name']}")
else:
    st.sidebar.warning("⚠️ AI Not Configured")

# Main content based on page selection
if page == "🏠 Dashboard":
    st.title("📚 E-Book Maker Dashboard")
    st.markdown("### Professional Publishing Toolkit for Amazon KDP")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.info("### 🔄 Document Conversion\n\nConvert 9+ formats to EPUB, PDF, HTML, DOCX, Markdown")

    with col2:
        st.info("### 🎨 Cover Creation\n\nKDP-compliant covers for e-books, paperbacks, and hardbacks")

    with col3:
        st.info("### 💧 Watermarking\n\nProtect your documents with logo and text watermarks")

    st.markdown("---")

    # System Status
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("#### ✨ Features")

        features = [
            "✅ **9+ Input Formats**: DOCX, EPUB, RTF, ODT, LaTeX, RST, Org-mode, Markdown, HTML",
            "✅ **5 Output Formats**: EPUB, PDF, HTML, DOCX, Markdown",
            "✅ **KDP Compliance**: Official Amazon KDP specifications",
            "✅ **300 DPI**: Print-ready quality",
            "✅ **AI Assistant**: Powered by Groq (7 models available)",
            "✅ **Cross-Platform**: Windows, Linux, macOS"
        ]

        for feature in features:
            st.markdown(feature)

    with col2:
        st.markdown("#### 🔧 System Status")

        # Pandoc status
        if st.session_state.pandoc_available:
            st.success(f"✅ Pandoc {st.session_state.pandoc_version}")
            st.caption("Document conversion: **Available**")
        else:
            st.warning("⚠️ Pandoc not found")
            st.caption("Document conversion: **Unavailable**")

        # Other features (always available)
        st.info("✅ Cover Generation")
        st.info("✅ Watermarking")
        st.info("✅ AI Features")

elif page == "🔄 Convert Documents":
    st.title("🔄 Document Conversion")
    st.markdown("Convert documents to KDP-compliant formats")

    # Check Pandoc availability
    if not st.session_state.pandoc_available:
        st.error("⚠️ **Pandoc Not Available**")
        st.markdown("""
        Document conversion requires **Pandoc**, which is not currently installed or accessible.

        **Options:**
        1. **Local Installation**: Download and run E-Book Maker locally where Pandoc is installed
        2. **Install Pandoc**:
           - Windows: Download from [pandoc.org](https://pandoc.org/installing.html)
           - Linux: `sudo apt-get install pandoc`
           - Mac: `brew install pandoc`

        **Features Available Without Pandoc:**
        - ✅ Cover Creation (works perfectly)
        - ✅ Watermarking (works perfectly)
        - ✅ AI Assistant (works perfectly)

        **Note:** If running on Streamlit Cloud, Pandoc installation is handled automatically via `packages.txt`.
        If you still see this message, the installation may have failed. Try restarting the app.
        """)
        st.stop()
    else:
        # Show Pandoc version
        if st.session_state.pandoc_version:
            st.success(f"✅ Pandoc {st.session_state.pandoc_version} detected")

    # File upload
    uploaded_file = st.file_uploader(
        "Upload Document",
        type=['docx', 'epub', 'rtf', 'odt', 'tex', 'rst', 'org', 'md', 'html'],
        help="Supported: DOCX, EPUB, RTF, ODT, LaTeX, RST, Org-mode, Markdown, HTML"
    )

    if uploaded_file:
        st.success(f"📄 Uploaded: {uploaded_file.name}")

        col1, col2 = st.columns(2)

        with col1:
            output_format = st.selectbox(
                "Output Format",
                ["EPUB", "PDF", "HTML", "DOCX", "Markdown"],
                help="Select target format"
            )

        with col2:
            add_toc = st.checkbox("Generate Table of Contents", value=True)

        # Metadata
        st.markdown("#### 📝 Metadata")
        col1, col2 = st.columns(2)

        with col1:
            title = st.text_input("Book Title", placeholder="My Awesome Book")

        with col2:
            author = st.text_input("Author", placeholder="Author Name")

        # Advanced Options
        with st.expander("⚙️ Advanced Options"):
            normalize_text = st.checkbox("Normalize text encoding", value=True, help="Fix encoding issues and convert bullet points")

            # Page numbering (for PDF/DOCX)
            if output_format in ["PDF", "DOCX"]:
                st.markdown("**Page Numbering**")
                enable_page_numbers = st.checkbox("Enable automatic page numbering", value=True)

                if enable_page_numbers:
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        page_number_position = st.selectbox(
                            "Position",
                            ["bottom-center", "bottom-right", "bottom-left", "top-center", "top-right", "top-left"],
                            help="Page number position"
                        )

                    with col2:
                        page_number_style = st.selectbox(
                            "Style",
                            ["arabic", "roman", "alphabetic"],
                            help="Numbering style (1,2,3 or i,ii,iii or a,b,c)"
                        )

                    with col3:
                        front_matter = st.checkbox("Front matter numbering", value=True, help="Different numbering for preface/TOC")

        if st.button("🚀 Convert Document", type="primary"):
            with st.spinner("Converting..."):
                try:
                    # Save uploaded file
                    input_path = Path("output/uploads") / uploaded_file.name
                    input_path.parent.mkdir(parents=True, exist_ok=True)

                    with open(input_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())

                    # Build page numbering configuration
                    page_config = None
                    if output_format in ["PDF", "DOCX"]:
                        try:
                            if enable_page_numbers:
                                page_config = {
                                    'enabled': True,
                                    'pdf': {'enabled': True, 'position': page_number_position, 'style': page_number_style,
                                            'front_matter': {'enabled': front_matter, 'style': 'roman'}},
                                    'docx': {'enabled': True, 'position': page_number_position, 'style': page_number_style}
                                }
                        except:
                            pass  # Variables not defined if options collapsed

                    # Convert
                    converter = EBookConverter(page_numbering_config=page_config)
                    results = converter.convert(
                        input_files=[input_path],
                        output_formats=[output_format.lower()],
                        title=title or "Untitled",
                        author=author or "Unknown",
                        output_dir=Path("output/ebooks"),
                        normalize_text=normalize_text
                    )

                    if results and len(results) > 0:
                        output_file = Path(results[0]['path'])
                        st.success(f"✅ Conversion successful!")

                        # Download button
                        with open(output_file, "rb") as f:
                            st.download_button(
                                label=f"📥 Download {output_format}",
                                data=f,
                                file_name=output_file.name,
                                mime="application/octet-stream"
                            )
                    else:
                        st.error("❌ Conversion failed: No output generated")

                except Exception as e:
                    st.error(f"❌ Conversion failed: {str(e)}")

elif page == "🎨 Create Covers":
    st.title("🎨 Cover Creation & Conversion")
    st.markdown("Create or convert KDP-compliant book covers")

    # Cover mode selection
    cover_mode = st.radio(
        "Mode",
        ["Create New Cover", "Convert Existing Cover"],
        horizontal=True
    )

    if cover_mode == "Create New Cover":
        st.markdown("### Create New Cover")

        # Cover type
        cover_type = st.radio(
            "Cover Type",
            ["E-book (JPEG)", "Paperback (PDF)", "Hardback (PDF)"],
            horizontal=True,
            key="create_cover_type"
        )

        # Map display names to actual types
        type_map = {
            "E-book (JPEG)": "ebook",
            "Paperback (PDF)": "paperback",
            "Hardback (PDF)": "hardback"
        }
        actual_type = type_map[cover_type]

        # Basic info
        col1, col2 = st.columns(2)

        with col1:
            title = st.text_input("Book Title", placeholder="My Book Title")
            author = st.text_input("Author", placeholder="Author Name")

        with col2:
            subtitle = st.text_input("Subtitle (Optional)", placeholder="An Epic Journey")
            style = st.selectbox("Style", ["Gradient", "Solid", "Minimalist"])

        # Colors
        col1, col2 = st.columns(2)

        with col1:
            primary_color = st.color_picker("Primary Color", "#667eea")

        with col2:
            secondary_color = st.color_picker("Secondary Color", "#764ba2")

        # Optional background
        background_file = st.file_uploader(
            "Background Image (Optional)",
            type=['pdf', 'png', 'jpg', 'jpeg'],
            help="Upload custom background image or PDF"
        )

        # Additional options for paperback/hardback
        if actual_type in ['paperback', 'hardback']:
            st.markdown("---")
            st.markdown("### Print Book Options")

            col1, col2 = st.columns(2)
            with col1:
                page_count = st.number_input(
                    "Page Count",
                    min_value=24,
                    max_value=828,
                    value=100,
                    help="Number of pages (determines spine width). KDP min: 24, max: 828. Spine text requires minimum 79 pages."
                )
                paper_type = st.selectbox(
                    "Paper Type",
                    ["white", "cream", "color"],
                    help="Paper type affects spine width calculation"
                )

            with col2:
                add_barcode = st.checkbox(
                    "Add Barcode Safe Area",
                    value=True,
                    help="Add KDP 2.0\" × 1.2\" white box on back cover for barcode"
                )
                # Show spine text info
                if page_count >= 79:
                    st.info(f"✓ Spine text will be added ({page_count} pages)")
                else:
                    st.warning(f"⚠️ Spine text requires minimum 79 pages (current: {page_count})")

            # Trim size selection
            col1, col2 = st.columns(2)
            with col1:
                trim_size = st.selectbox(
                    "Trim Size",
                    ["6×9", "5×8", "5.5×8.5", "8.5×11", "7×10", "8×10"],
                    help="Standard KDP trim size"
                )
            with col2:
                # Parse trim size
                trim_parts = trim_size.replace("×", "x").split("x")
                trim_width = float(trim_parts[0])
                trim_height = float(trim_parts[1])
                st.info(f"Trim: {trim_width}\" × {trim_height}\"")
        else:
            # Default for ebook
            add_barcode = False
            page_count = 100
            paper_type = "white"
            trim_width = 6.0
            trim_height = 9.0

        if st.button("🎨 Generate Cover", type="primary"):
            if not title:
                st.warning("⚠️ Please enter a book title")
            else:
                with st.spinner("Generating cover..."):
                    try:
                        background_path = None

                        if background_file:
                            bg_path = Path("output/uploads") / background_file.name
                            bg_path.parent.mkdir(parents=True, exist_ok=True)
                            with open(bg_path, "wb") as f:
                                f.write(background_file.getbuffer())
                            background_path = bg_path

                        # Generate cover
                        generator = CoverGenerator()
                        cover_path = generator.create_cover(
                            cover_type=actual_type,
                            title=title,
                            subtitle=subtitle,
                            author=author or "Author",
                            style=style.lower(),
                            colors={'primary': primary_color, 'secondary': secondary_color},
                            output_dir=Path("output/covers"),
                            background_image=background_path,
                            add_barcode_area=add_barcode,
                            page_count=page_count,
                            paper_type=paper_type,
                            trim_width=trim_width,
                            trim_height=trim_height
                        )

                        st.success(f"✅ Cover created successfully!")

                        # Display preview for images
                        if actual_type == "ebook":
                            st.image(str(cover_path), caption="Cover Preview", use_column_width=True)
                        else:
                            st.info(f"📄 PDF cover created: {cover_path.name}")

                        # Download button
                        with open(cover_path, "rb") as f:
                            st.download_button(
                                label=f"📥 Download Cover",
                                data=f,
                                file_name=cover_path.name,
                                mime="application/octet-stream"
                            )

                    except Exception as e:
                        st.error(f"❌ Cover generation failed: {str(e)}")

    else:  # Convert Existing Cover
        st.markdown("### Convert Existing Cover")
        st.caption("Convert an existing cover to different KDP formats")

        # Cover upload
        cover_file = st.file_uploader(
            "Upload Cover Image",
            type=['pdf', 'png', 'jpg', 'jpeg'],
            help="Upload cover to convert (PDF, PNG, JPG, JPEG)",
            key="convert_cover_upload"
        )

        if cover_file:
            st.success(f"📄 Uploaded: {cover_file.name}")

            # Target type
            convert_type = st.radio(
                "Convert To",
                ["E-book (JPEG)", "Paperback (PDF)", "Hardback (PDF)"],
                horizontal=True,
                key="convert_cover_type"
            )

            # Map display names to actual types
            type_map = {
                "E-book (JPEG)": "ebook",
                "Paperback (PDF)": "paperback",
                "Hardback (PDF)": "hardback"
            }
            convert_actual_type = type_map[convert_type]

            # Text options
            add_text = st.checkbox(
                "Add Text Overlay",
                value=True,
                help="Add title and author text to cover (useful for spine text on print books)"
            )

            if add_text:
                col1, col2 = st.columns(2)
                with col1:
                    convert_title = st.text_input("Book Title", placeholder="My Book Title", key="convert_title")
                    convert_author = st.text_input("Author", placeholder="Author Name", key="convert_author")
                with col2:
                    convert_subtitle = st.text_input("Subtitle (Optional)", placeholder="Subtitle", key="convert_subtitle")
                    spine_color = st.color_picker("Spine Color", "#FF6B35", key="convert_spine_color")
            else:
                convert_title = ""
                convert_author = ""
                convert_subtitle = ""
                spine_color = "#FF6B35"

            # Barcode option for print books
            if convert_actual_type in ['paperback', 'hardback']:
                st.markdown("---")
                st.markdown("### Print Book Options")
                col1, col2 = st.columns(2)
                with col1:
                    convert_page_count = st.number_input(
                        "Page Count",
                        min_value=24,
                        max_value=828,
                        value=100,
                        help="Number of pages for spine width. Spine text requires minimum 79 pages.",
                        key="convert_page_count"
                    )
                with col2:
                    convert_add_barcode = st.checkbox(
                        "Add Barcode Safe Area",
                        value=True,
                        help="Add KDP 2.0\" × 1.2\" white box on back cover for barcode"
                    )
                    # Show spine text info
                    if convert_page_count >= 79:
                        st.info(f"✓ Spine text will be added ({convert_page_count} pages)")
                    else:
                        st.warning(f"⚠️ Spine text requires minimum 79 pages (current: {convert_page_count})")
            else:
                convert_add_barcode = False
                convert_page_count = 100

            if st.button("🔄 Convert Cover", type="primary"):
                with st.spinner("Converting cover..."):
                    try:
                        # Save uploaded file
                        input_path = Path("output/uploads") / cover_file.name
                        input_path.parent.mkdir(parents=True, exist_ok=True)
                        with open(input_path, "wb") as f:
                            f.write(cover_file.getbuffer())

                        # Convert cover
                        generator = CoverGenerator()
                        converted_path = generator.convert_cover(
                            input_file=input_path,
                            target_type=convert_actual_type,
                            output_dir=Path("output/covers"),
                            title=convert_title,
                            subtitle=convert_subtitle,
                            author=convert_author,
                            add_text=add_text,
                            spine_color=spine_color,
                            add_barcode_area=convert_add_barcode,
                            page_count=convert_page_count
                        )

                        st.success(f"✅ Cover converted successfully!")

                        # Display preview for images
                        if convert_actual_type == "ebook":
                            st.image(str(converted_path), caption="Converted Cover Preview", use_column_width=True)
                        else:
                            st.info(f"📄 PDF cover created: {converted_path.name}")

                        # Download button
                        with open(converted_path, "rb") as f:
                            st.download_button(
                                label=f"📥 Download Converted Cover",
                                data=f,
                                file_name=converted_path.name,
                                mime="application/octet-stream"
                            )

                    except Exception as e:
                        st.error(f"❌ Cover conversion failed: {str(e)}")

elif page == "💧 Watermark":
    st.title("💧 Document Watermarking")
    st.markdown("Add watermarks to protect your documents")

    # File upload
    uploaded_file = st.file_uploader(
        "Upload Document",
        type=['pdf', 'html', 'docx', 'md'],
        help="Supported: PDF, HTML, DOCX, Markdown"
    )

    if uploaded_file:
        st.success(f"📄 Uploaded: {uploaded_file.name}")

        # Watermark options
        col1, col2 = st.columns(2)

        with col1:
            watermark_text = st.text_input("Watermark Text", placeholder="© 2025 - All Rights Reserved")
            opacity = st.slider("Opacity", 0.0, 1.0, 0.3, 0.05)

        with col2:
            position = st.selectbox(
                "Position",
                ["center", "top-right", "bottom-right", "top-left", "bottom-left"]
            )
            logo_file = st.file_uploader("Logo (Optional)", type=['png', 'jpg', 'jpeg'])

        if st.button("💧 Apply Watermark", type="primary"):
            with st.spinner("Applying watermark..."):
                try:
                    # Save uploaded file
                    input_path = Path("output/uploads") / uploaded_file.name
                    input_path.parent.mkdir(parents=True, exist_ok=True)

                    with open(input_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())

                    logo_path = None
                    if logo_file:
                        logo_path = Path("output/uploads") / logo_file.name
                        with open(logo_path, "wb") as f:
                            f.write(logo_file.getbuffer())

                    # Apply watermark
                    watermarker = Watermarker()
                    output_file = watermarker.apply_watermark(
                        input_file=input_path,
                        watermark_text=watermark_text,
                        logo_path=logo_path,
                        opacity=opacity,
                        position=position,
                        output_dir=Path("output/watermarked")
                    )

                    st.success("✅ Watermark applied successfully!")

                    # Download button
                    with open(output_file, "rb") as f:
                        st.download_button(
                            label=f"📥 Download Watermarked File",
                            data=f,
                            file_name=output_file.name,
                            mime="application/octet-stream"
                        )

                except Exception as e:
                    st.error(f"❌ Watermarking failed: {str(e)}")

elif page == "📢 AI Marketing":
    st.title("📢 AI Marketing Wizard")
    st.markdown("Generate professional marketing content for your book using AI")

    # Check if AI is enabled
    if not ai_enabled:
        st.warning("⚠️ AI features are not configured. Please configure your Groq API key in AI Settings.")
        st.info("👉 Go to AI Settings to set up your API key")
        st.stop()

    # Initialize wizard session state
    if 'wizard_step' not in st.session_state:
        st.session_state.wizard_step = 1

    if 'wizard_data' not in st.session_state:
        st.session_state.wizard_data = {
            'title': '',
            'genre': '',
            'audience': '',
            'concept': '',
            'outline': '',
            'description': '',
            'keywords': [],
            'social_posts': [],
            'blurbs': []
        }

    # Progress indicator
    steps = ["📖 Book Details", "✨ Generate Content", "✏️ Polish Content", "🎯 Marketing"]
    cols = st.columns(4)
    for i, (col, step) in enumerate(zip(cols, steps), 1):
        with col:
            if i < st.session_state.wizard_step:
                st.success(f"✅ {step}")
            elif i == st.session_state.wizard_step:
                st.info(f"▶️ {step}")
            else:
                st.text(f"⏸️ {step}")

    st.markdown("---")

    # Step 1: Book Details
    if st.session_state.wizard_step == 1:
        st.subheader("📖 Tell Us About Your Book")
        st.caption("Let's start by gathering some basic information")

        title = st.text_input(
            "Book Title *",
            value=st.session_state.wizard_data['title'],
            placeholder="Enter your book title"
        )

        genre = st.selectbox(
            "Genre *",
            ["", "Fiction", "Non-Fiction", "Mystery/Thriller", "Romance", "Science Fiction",
             "Fantasy", "Biography/Memoir", "Self-Help", "Business", "History", "Other"],
            index=0 if not st.session_state.wizard_data['genre'] else
                  ["", "Fiction", "Non-Fiction", "Mystery/Thriller", "Romance", "Science Fiction",
                   "Fantasy", "Biography/Memoir", "Self-Help", "Business", "History", "Other"].index(st.session_state.wizard_data['genre'])
        )

        audience = st.text_input(
            "Target Audience *",
            value=st.session_state.wizard_data['audience'],
            placeholder="e.g., Young adults, Business professionals, History enthusiasts"
        )

        concept = st.text_area(
            "Brief Concept/Summary *",
            value=st.session_state.wizard_data['concept'],
            placeholder="Describe your book concept in a few sentences. This helps AI understand your project.",
            height=150
        )

        st.caption(f"{len(concept)} characters")

        # Navigation
        col1, col2, col3 = st.columns([1, 2, 1])
        with col3:
            if st.button("Next →", type="primary", use_container_width=True):
                if title and genre and audience and concept:
                    st.session_state.wizard_data.update({
                        'title': title,
                        'genre': genre,
                        'audience': audience,
                        'concept': concept
                    })
                    st.session_state.wizard_step = 2
                    st.rerun()
                else:
                    st.error("⚠️ Please fill in all required fields")

    # Step 2: Generate Content
    elif st.session_state.wizard_step == 2:
        st.subheader("✨ Generate Content")
        st.caption("Let AI help you create chapter outlines and book descriptions")

        # Chapter Outline
        st.markdown("### 📝 Chapter Outline")
        col1, col2 = st.columns([3, 1])

        with col1:
            st.markdown(f"**Book:** {st.session_state.wizard_data['title']}")

        with col2:
            num_chapters = st.selectbox("Chapters:", [5, 10, 15, 20], index=1, key="outline_chapters")

        if 'outline_generated' not in st.session_state:
            st.session_state.outline_generated = False

        if not st.session_state.outline_generated or not st.session_state.wizard_data['outline']:
            if st.button("✨ Generate Chapter Outline", use_container_width=True):
                with st.spinner("Generating chapter outline..."):
                    try:
                        prompt = f"Generate a detailed {num_chapters}-chapter outline for a {st.session_state.wizard_data['genre']} book titled \"{st.session_state.wizard_data['title']}\". Target audience: {st.session_state.wizard_data['audience']}. Concept: {st.session_state.wizard_data['concept']}. Format as: Chapter 1: [Title] - [2-3 sentence summary]"

                        success, result = st.session_state.ai_assistant.generate_text(prompt, max_tokens=1000)

                        if success:
                            st.session_state.wizard_data['outline'] = result
                            st.session_state.outline_generated = True
                            st.rerun()
                        else:
                            st.error(f"❌ Generation failed: {result}")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
        else:
            outline = st.text_area(
                "Chapter Outline",
                value=st.session_state.wizard_data['outline'],
                height=200,
                key="outline_edit"
            )
            st.session_state.wizard_data['outline'] = outline

            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 Regenerate", use_container_width=True):
                    st.session_state.outline_generated = False
                    st.session_state.wizard_data['outline'] = ''
                    st.rerun()
            with col2:
                if st.button("🗑️ Clear", use_container_width=True):
                    st.session_state.outline_generated = False
                    st.session_state.wizard_data['outline'] = ''
                    st.rerun()

        st.markdown("---")

        # Book Description
        st.markdown("### 📄 Book Description")

        length = st.selectbox(
            "Length:",
            ["Short (50-75 words)", "Medium (100-150 words)", "Long (200-300 words)"],
            index=1,
            key="description_length"
        )

        if 'description_generated' not in st.session_state:
            st.session_state.description_generated = False

        if not st.session_state.description_generated or not st.session_state.wizard_data['description']:
            if st.button("✨ Generate Description", use_container_width=True):
                with st.spinner("Generating book description..."):
                    try:
                        word_count = {"Short (50-75 words)": "50-75", "Medium (100-150 words)": "100-150", "Long (200-300 words)": "200-300"}[length]

                        prompt = f"Write a compelling {word_count}-word book description for \"{st.session_state.wizard_data['title']}\", a {st.session_state.wizard_data['genre']} book. Target audience: {st.session_state.wizard_data['audience']}. Concept: {st.session_state.wizard_data['concept']}. Make it engaging and marketable."

                        success, result = st.session_state.ai_assistant.generate_text(prompt, max_tokens=500)

                        if success:
                            st.session_state.wizard_data['description'] = result
                            st.session_state.description_generated = True
                            st.rerun()
                        else:
                            st.error(f"❌ Generation failed: {result}")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
        else:
            description = st.text_area(
                "Book Description",
                value=st.session_state.wizard_data['description'],
                height=150,
                key="description_edit"
            )
            st.session_state.wizard_data['description'] = description

            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 Regenerate", use_container_width=True, key="regen_desc"):
                    st.session_state.description_generated = False
                    st.session_state.wizard_data['description'] = ''
                    st.rerun()
            with col2:
                if st.button("🗑️ Clear", use_container_width=True, key="clear_desc"):
                    st.session_state.description_generated = False
                    st.session_state.wizard_data['description'] = ''
                    st.rerun()

        # Navigation
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            if st.button("← Back", use_container_width=True):
                st.session_state.wizard_step = 1
                st.rerun()
        with col3:
            if st.button("Next →", type="primary", use_container_width=True):
                st.session_state.wizard_step = 3
                st.rerun()

    # Step 3: Polish Content
    elif st.session_state.wizard_step == 3:
        st.subheader("✏️ Polish Your Content")
        st.caption("Review and enhance your generated content")

        # Polish Outline
        st.markdown("### 📝 Chapter Outline")
        polish_outline = st.text_area(
            "Edit your outline",
            value=st.session_state.wizard_data.get('outline', 'No outline generated yet'),
            height=200,
            key="polish_outline"
        )

        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("🔍 Fix Grammar", use_container_width=True, key="grammar_outline"):
                with st.spinner("Improving grammar..."):
                    try:
                        prompt = f"Fix grammar and spelling errors in this text, but keep the style and meaning the same:\n\n{polish_outline}"
                        success, result = st.session_state.ai_assistant.generate_text(prompt, max_tokens=1000)
                        if success:
                            st.session_state.wizard_data['outline'] = result
                            st.rerun()
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

        with col2:
            if st.button("📉 Simplify", use_container_width=True, key="simplify_outline"):
                with st.spinner("Simplifying..."):
                    try:
                        prompt = f"Simplify this text to make it easier to read, while keeping the key points:\n\n{polish_outline}"
                        success, result = st.session_state.ai_assistant.generate_text(prompt, max_tokens=1000)
                        if success:
                            st.session_state.wizard_data['outline'] = result
                            st.rerun()
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

        with col3:
            if st.button("📈 Expand", use_container_width=True, key="expand_outline"):
                with st.spinner("Expanding..."):
                    try:
                        prompt = f"Expand this text with more details and examples, making it more comprehensive:\n\n{polish_outline}"
                        success, result = st.session_state.ai_assistant.generate_text(prompt, max_tokens=1500)
                        if success:
                            st.session_state.wizard_data['outline'] = result
                            st.rerun()
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

        st.session_state.wizard_data['outline'] = polish_outline

        st.markdown("---")

        # Polish Description
        st.markdown("### 📄 Book Description")
        polish_description = st.text_area(
            "Edit your description",
            value=st.session_state.wizard_data.get('description', 'No description generated yet'),
            height=150,
            key="polish_description"
        )

        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("🔍 Fix Grammar", use_container_width=True, key="grammar_desc"):
                with st.spinner("Improving grammar..."):
                    try:
                        prompt = f"Fix grammar and spelling errors in this text, but keep the style and meaning the same:\n\n{polish_description}"
                        success, result = st.session_state.ai_assistant.generate_text(prompt, max_tokens=1000)
                        if success:
                            st.session_state.wizard_data['description'] = result
                            st.rerun()
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

        with col2:
            if st.button("✨ Make Engaging", use_container_width=True, key="engaging_desc"):
                with st.spinner("Enhancing..."):
                    try:
                        prompt = f"Rewrite this text to be more engaging, compelling, and emotionally resonant:\n\n{polish_description}"
                        success, result = st.session_state.ai_assistant.generate_text(prompt, max_tokens=1000)
                        if success:
                            st.session_state.wizard_data['description'] = result
                            st.rerun()
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

        with col3:
            if st.button("🔑 Add Keywords", use_container_width=True, key="keywords_desc"):
                with st.spinner("Adding keywords..."):
                    try:
                        prompt = f"Rewrite this book description to naturally include relevant keywords that would help with Amazon SEO:\n\n{polish_description}"
                        success, result = st.session_state.ai_assistant.generate_text(prompt, max_tokens=1000)
                        if success:
                            st.session_state.wizard_data['description'] = result
                            st.rerun()
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

        st.session_state.wizard_data['description'] = polish_description

        # Navigation
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            if st.button("← Back", use_container_width=True):
                st.session_state.wizard_step = 2
                st.rerun()
        with col3:
            if st.button("Next →", type="primary", use_container_width=True):
                st.session_state.wizard_step = 4
                st.rerun()

    # Step 4: Marketing Materials
    elif st.session_state.wizard_step == 4:
        st.subheader("🎯 Marketing Materials")
        st.caption("Generate professional marketing content for your book")

        # Amazon Keywords
        st.markdown("### 🔑 Amazon Keywords")
        if 'keywords_generated' not in st.session_state:
            st.session_state.keywords_generated = False

        if not st.session_state.keywords_generated or not st.session_state.wizard_data['keywords']:
            if st.button("✨ Generate Keywords", use_container_width=True):
                with st.spinner("Generating Amazon keywords..."):
                    try:
                        prompt = f"Generate 10 highly relevant Amazon KDP keywords for a {st.session_state.wizard_data['genre']} book titled \"{st.session_state.wizard_data['title']}\". Target audience: {st.session_state.wizard_data['audience']}. Format: one keyword per line, no numbers."

                        success, result = st.session_state.ai_assistant.generate_text(prompt, max_tokens=200)

                        if success:
                            keywords = [k.strip() for k in result.split('\n') if k.strip()]
                            st.session_state.wizard_data['keywords'] = keywords
                            st.session_state.keywords_generated = True
                            st.rerun()
                        else:
                            st.error(f"❌ Generation failed: {result}")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
        else:
            for i, keyword in enumerate(st.session_state.wizard_data['keywords'], 1):
                st.write(f"{i}. {keyword}")

            if st.button("📋 Copy All Keywords", use_container_width=True):
                keywords_text = '\n'.join(st.session_state.wizard_data['keywords'])
                st.code(keywords_text, language=None)
                st.success("✅ Keywords ready to copy!")

        st.markdown("---")

        # Social Media Posts
        st.markdown("### 📱 Social Media Posts")
        if 'social_generated' not in st.session_state:
            st.session_state.social_generated = False

        if not st.session_state.social_generated or not st.session_state.wizard_data['social_posts']:
            if st.button("✨ Generate Social Posts", use_container_width=True):
                with st.spinner("Generating social media posts..."):
                    try:
                        prompt = f"Create 3 engaging social media posts (Twitter/Facebook style) to promote the book \"{st.session_state.wizard_data['title']}\". Genre: {st.session_state.wizard_data['genre']}. Include hooks, call-to-actions, and relevant hashtags. Separate each post with '---'."

                        success, result = st.session_state.ai_assistant.generate_text(prompt, max_tokens=500)

                        if success:
                            posts = [p.strip() for p in result.split('---') if p.strip()]
                            st.session_state.wizard_data['social_posts'] = posts
                            st.session_state.social_generated = True
                            st.rerun()
                        else:
                            st.error(f"❌ Generation failed: {result}")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
        else:
            for i, post in enumerate(st.session_state.wizard_data['social_posts'], 1):
                with st.expander(f"Post {i}", expanded=True):
                    st.write(post)
                    if st.button(f"📋 Copy Post {i}", key=f"copy_social_{i}"):
                        st.code(post, language=None)
                        st.success("✅ Ready to copy!")

        st.markdown("---")

        # Book Blurbs
        st.markdown("### 📣 Book Blurbs")
        if 'blurbs_generated' not in st.session_state:
            st.session_state.blurbs_generated = False

        if not st.session_state.blurbs_generated or not st.session_state.wizard_data['blurbs']:
            if st.button("✨ Generate Blurbs", use_container_width=True):
                with st.spinner("Generating book blurbs..."):
                    try:
                        prompt = f"Write 3 different promotional blurbs for \"{st.session_state.wizard_data['title']}\" ({st.session_state.wizard_data['genre']}). Make them compelling and different in tone: 1) Short & punchy (30 words), 2) Medium & descriptive (75 words), 3) Long & detailed (150 words). Separate with '---'."

                        success, result = st.session_state.ai_assistant.generate_text(prompt, max_tokens=800)

                        if success:
                            blurbs = [b.strip() for b in result.split('---') if b.strip()]
                            st.session_state.wizard_data['blurbs'] = blurbs
                            st.session_state.blurbs_generated = True
                            st.rerun()
                        else:
                            st.error(f"❌ Generation failed: {result}")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
        else:
            versions = ["Short Version (30 words)", "Medium Version (75 words)", "Long Version (150 words)"]
            for i, (blurb, version) in enumerate(zip(st.session_state.wizard_data['blurbs'], versions), 1):
                with st.expander(version, expanded=True):
                    st.write(blurb)
                    if st.button(f"📋 Copy {version}", key=f"copy_blurb_{i}"):
                        st.code(blurb, language=None)
                        st.success("✅ Ready to copy!")

        st.markdown("---")

        # Export Section
        st.markdown("### 📥 Export Everything")
        col1, col2 = st.columns(2)

        with col1:
            if st.button("📥 Download All Content", type="primary", use_container_width=True):
                content = f"""BOOK MARKETING MATERIALS
Generated: {Path(__file__).parent}

========================
BOOK DETAILS
========================
Title: {st.session_state.wizard_data['title']}
Genre: {st.session_state.wizard_data['genre']}
Target Audience: {st.session_state.wizard_data['audience']}

Concept:
{st.session_state.wizard_data['concept']}

========================
CHAPTER OUTLINE
========================
{st.session_state.wizard_data.get('outline', 'Not generated')}

========================
BOOK DESCRIPTION
========================
{st.session_state.wizard_data.get('description', 'Not generated')}

========================
AMAZON KEYWORDS
========================
{chr(10).join(st.session_state.wizard_data.get('keywords', ['Not generated']))}

========================
SOCIAL MEDIA POSTS
========================
{chr(10).join([f"Post {i+1}:{chr(10)}{post}{chr(10)}" for i, post in enumerate(st.session_state.wizard_data.get('social_posts', []))])}

========================
BOOK BLURBS
========================
{chr(10).join([f"Version {i+1}:{chr(10)}{blurb}{chr(10)}" for i, blurb in enumerate(st.session_state.wizard_data.get('blurbs', []))])}
"""
                st.download_button(
                    label="💾 Download Marketing Materials",
                    data=content,
                    file_name=f"{st.session_state.wizard_data['title'].replace(' ', '_')}_marketing.txt",
                    mime="text/plain"
                )

        with col2:
            if st.button("🔄 Start Over", use_container_width=True):
                st.session_state.wizard_step = 1
                st.session_state.wizard_data = {
                    'title': '',
                    'genre': '',
                    'audience': '',
                    'concept': '',
                    'outline': '',
                    'description': '',
                    'keywords': [],
                    'social_posts': [],
                    'blurbs': []
                }
                st.session_state.outline_generated = False
                st.session_state.description_generated = False
                st.session_state.keywords_generated = False
                st.session_state.social_generated = False
                st.session_state.blurbs_generated = False
                st.rerun()

        # Navigation
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            if st.button("← Back", use_container_width=True):
                st.session_state.wizard_step = 3
                st.rerun()

elif page == "🤖 AI Settings":
    st.title("🤖 AI Assistant Configuration")
    st.markdown("Configure Groq AI integration for enhanced features")

    # Show API key source if enabled
    if ai_enabled:
        api_key_source = st.session_state.ai_assistant.get_api_key_source()
        if api_key_source:
            st.info(f"ℹ️ API Key loaded from **{api_key_source}**")
        st.markdown("---")

    # API Key Configuration
    st.markdown("### 🔑 API Key Setup")
    st.info("💡 **Get your FREE Groq API key at:** [console.groq.com/keys](https://console.groq.com/keys)")

    api_key_input = st.text_input(
        "Enter Your Groq API Key",
        type="password",
        placeholder="gsk_...",
        help="Your API key is stored locally and never shared"
    )

    if st.button("💾 Save & Test API Key", type="primary"):
        if api_key_input:
            with st.spinner("Validating API key..."):
                success, message = st.session_state.ai_assistant.set_api_key(api_key_input)
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
        else:
            st.warning("⚠️ Please enter an API key")

    # Model selection (only if AI is enabled)
    if ai_enabled:
        st.markdown("---")
        st.markdown("### Model Selection")

        models = st.session_state.ai_assistant.get_available_models()
        current_model = st.session_state.ai_assistant.get_current_model()

        # Create model options
        model_options = {}
        for model_id, info in models.items():
            model_options[f"{info['name']} - {info['description']}"] = model_id

        # Reverse lookup for current selection
        current_display = next(
            (display for display, mid in model_options.items() if mid == current_model),
            list(model_options.keys())[0] if model_options else ""
        )

        selected_display = st.selectbox(
            "AI Model",
            options=list(model_options.keys()),
            index=list(model_options.keys()).index(current_display) if current_display in model_options else 0
        )

        selected_model_id = model_options[selected_display]

        # Show model info
        model_info = models[selected_model_id]

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Quality", model_info['quality'].title())

        with col2:
            st.metric("Speed", model_info['speed'].title())

        with col3:
            st.metric("Category", model_info['category'].title())

        st.info(f"ℹ️ {model_info['description']}")

        # Change model button
        if selected_model_id != current_model:
            if st.button("✅ Switch to This Model", type="primary"):
                success, message = st.session_state.ai_assistant.set_model(selected_model_id)
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)

        # Clear API key
        st.markdown("---")
        if st.button("🗑️ Remove API Key", type="secondary"):
            st.session_state.ai_assistant.client = None
            st.session_state.ai_assistant.enabled = False
            st.session_state.ai_assistant.config['groq_api_key'] = ''
            st.session_state.ai_assistant.config['ai_enabled'] = False
            st.session_state.ai_assistant._save_config()
            st.success("✅ API key removed. AI features disabled.")
            st.rerun()

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("**E-Book Maker v2.1.0**")
st.sidebar.markdown("*Streamlit Interface*")
st.sidebar.markdown("© 2025 Diatasso LLC")
