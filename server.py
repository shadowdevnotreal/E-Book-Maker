#!/usr/bin/env python3
"""
E-Book Maker - Web Server
Flask-based web interface for e-book creation, cover generation, and watermarking
"""

import os
import sys
import json
import webbrowser
from pathlib import Path
from threading import Timer
from flask import Flask, render_template, request, jsonify, send_file, send_from_directory
from werkzeug.utils import secure_filename

# Add modules to path
BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR / 'modules'))

# Import modules (will create these next)
try:
    from conversion.converter import EBookConverter
    from covers.cover_generator import CoverGenerator
    from watermarking.watermarker import Watermarker
    from utils.file_handler import FileHandler
    from ai.groq_assistant import GroqAssistant
    from project_manager import ProjectManager
except ImportError as e:
    print(f"Warning: Module import failed: {e}")
    print("Some features may not be available until all modules are created.")

# Initialize AI Assistant and Project Manager
ai_assistant = GroqAssistant()
project_manager = ProjectManager()

# Flask app initialization
app = Flask(__name__,
            template_folder='web/templates',
            static_folder='web/static')

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size
app.config['UPLOAD_FOLDER'] = BASE_DIR / 'output' / 'uploads'
app.config['OUTPUT_FOLDER'] = BASE_DIR / 'output'
app.config['ALLOWED_EXTENSIONS'] = {
    'document': {'md', 'markdown', 'txt', 'html', 'htm', 'pdf', 'docx', 'epub',
                 'odt', 'rtf', 'tex', 'latex', 'rst', 'org'},
    'image': {'png', 'jpg', 'jpeg', 'gif', 'bmp'},
    'cover': {'pdf', 'png', 'jpg', 'jpeg', 'bmp', 'gif'}  # Covers can be PDF or images
}

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'] / 'ebooks', exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'] / 'covers', exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'] / 'watermarked', exist_ok=True)


def allowed_file(filename, file_type='document'):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS'].get(file_type, set())


@app.route('/')
def index():
    """Main dashboard"""
    return render_template('index.html')


@app.route('/convert')
def convert_page():
    """Document conversion interface"""
    return render_template('convert.html')


@app.route('/covers')
def covers_page():
    """Cover creation interface"""
    return render_template('covers.html')


@app.route('/watermark')
def watermark_page():
    """Watermarking interface"""
    return render_template('watermark.html')


@app.route('/marketing')
def marketing_page():
    """AI Marketing & Author Tools interface"""
    return render_template('marketing.html')


@app.route('/settings')
def settings_page():
    """Settings interface"""
    return render_template('settings.html')


# API Endpoints
@app.route('/api/convert', methods=['POST'])
def api_convert():
    """Convert document to e-book formats"""
    try:
        # Check if files were uploaded
        if 'files' not in request.files:
            return jsonify({'error': 'No files provided'}), 400

        files = request.files.getlist('files')
        output_formats = request.form.getlist('formats')
        title = request.form.get('title', 'Untitled E-Book')
        author = request.form.get('author', 'Unknown Author')
        is_folder = request.form.get('is_folder') == 'true'

        if not files or files[0].filename == '':
            return jsonify({'error': 'No files selected'}), 400

        # Save uploaded files
        input_files = []

        if is_folder:
            # Handle folder upload - organize by chapters/appendixes
            chapters = []
            appendixes = []
            other_files = []

            for file in files:
                if file and allowed_file(file.filename, 'document'):
                    # Get the relative path to determine folder structure
                    relative_path = file.filename  # This contains webkitRelativePath
                    path_parts = relative_path.split('/')

                    # Determine which folder this file belongs to
                    folder_name = path_parts[-2] if len(path_parts) > 1 else ''
                    base_filename = path_parts[-1]

                    # Create unique filename to avoid conflicts
                    unique_filename = secure_filename(f"{folder_name}_{base_filename}")
                    filepath = app.config['UPLOAD_FOLDER'] / unique_filename
                    file.save(str(filepath))

                    # Categorize by folder
                    if 'chapter' in folder_name.lower():
                        chapters.append((base_filename, filepath))
                    elif 'appendix' in folder_name.lower() or 'appendices' in folder_name.lower():
                        appendixes.append((base_filename, filepath))
                    else:
                        other_files.append((base_filename, filepath))

            # Sort alphabetically within each category
            chapters.sort(key=lambda x: x[0])
            appendixes.sort(key=lambda x: x[0])
            other_files.sort(key=lambda x: x[0])

            # Combine in order: chapters, appendixes, other files
            input_files = [f[1] for f in chapters] + [f[1] for f in appendixes] + [f[1] for f in other_files]

        else:
            # Handle individual file uploads
            for file in files:
                if file and allowed_file(file.filename, 'document'):
                    filename = secure_filename(file.filename)
                    filepath = app.config['UPLOAD_FOLDER'] / filename
                    file.save(str(filepath))
                    input_files.append(filepath)

        if not input_files:
            return jsonify({'error': 'No valid document files'}), 400

        # Convert using EBookConverter
        try:
            # Build page numbering configuration - ALWAYS enabled by default
            page_numbering_config = {
                'enabled': True,
                'pdf': {
                    'enabled': True,
                    'position': request.form.get('page_number_position', 'footer-center'),
                    'style': request.form.get('page_number_style', 'arabic'),
                    'front_matter': {
                        'enabled': request.form.get('front_matter_enabled') == 'true',
                        'style': request.form.get('front_matter_style', 'roman')
                    }
                },
                'docx': {
                    'enabled': True,
                    'position': request.form.get('page_number_position', 'footer-center'),
                    'style': request.form.get('page_number_style', 'arabic'),
                    'reference_doc': str(Path(__file__).parent / 'config' / 'templates' / 'reference-with-pagenumbers.docx')
                }
            }

            converter = EBookConverter(page_numbering_config=page_numbering_config)
            subtitle = request.form.get('subtitle', '')
            results = converter.convert(
                input_files=input_files,
                output_formats=output_formats,
                title=title,
                author=author,
                subtitle=subtitle,
                output_dir=app.config['OUTPUT_FOLDER'] / 'ebooks'
            )

            # Convert absolute paths to relative paths for download
            for result in results:
                result_path = Path(result['path'])
                if result_path.is_absolute():
                    try:
                        result['path'] = str(result_path.relative_to(app.config['OUTPUT_FOLDER']))
                    except ValueError:
                        # If path is not relative to OUTPUT_FOLDER, keep as is
                        pass

            # Create project entry for tracking
            try:
                project_metadata = {
                    'title': title,
                    'author': author,
                    'subtitle': subtitle,
                    'output_formats': output_formats
                }

                project_id = project_manager.create_project(
                    title=title,
                    project_type='conversion',
                    metadata=project_metadata
                )

                # Add generated files to project
                for result in results:
                    project_manager.add_file_to_project(
                        project_id=project_id,
                        file_path=result['path'],
                        file_type=result['format']
                    )
            except Exception as e:
                print(f"Warning: Could not create project entry: {e}")

            return jsonify({
                'success': True,
                'message': 'Conversion completed',
                'files': results
            })
        except Exception as e:
            return jsonify({'error': f'Conversion failed: {str(e)}'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/create-cover', methods=['POST'])
def api_create_cover():
    """Generate book cover"""
    try:
        # Handle FormData instead of JSON
        cover_type = request.form.get('type', 'ebook')  # ebook or paperback
        title = request.form.get('title', 'Book Title')
        subtitle = request.form.get('subtitle', '')
        author = request.form.get('author', 'Author Name')
        style = request.form.get('style', 'gradient')

        # Build colors dict from separate color fields
        colors = {
            'primary': request.form.get('primary_color', '#667eea'),
            'secondary': request.form.get('secondary_color', '#764ba2')
        }

        # Handle optional background image upload
        background_path = None
        if 'background' in request.files:
            bg_file = request.files['background']
            if bg_file and bg_file.filename != '':
                from werkzeug.utils import secure_filename
                filename = secure_filename(bg_file.filename)
                background_path = app.config['UPLOAD_FOLDER'] / filename
                bg_file.save(str(background_path))

        # Generate cover
        try:
            generator = CoverGenerator()
            cover_path = generator.create_cover(
                cover_type=cover_type,
                title=title,
                subtitle=subtitle,
                author=author,
                style=style,
                colors=colors,
                output_dir=app.config['OUTPUT_FOLDER'] / 'covers',
                background_image=background_path
            )

            # Convert to relative path for download
            try:
                relative_path = Path(cover_path).relative_to(app.config['OUTPUT_FOLDER'])
            except ValueError:
                relative_path = Path(cover_path).name

            # Create project entry for tracking
            try:
                metadata = {
                    'title': title,
                    'subtitle': subtitle,
                    'author': author,
                    'cover_type': cover_type,
                    'style': style,
                    'colors': colors
                }

                project_id = project_manager.create_project(
                    title=f"{title} - Cover",
                    project_type='cover',
                    metadata=metadata
                )

                # Add generated cover to project
                project_manager.add_file_to_project(
                    project_id=project_id,
                    file_path=str(relative_path),
                    file_type='cover_image'
                )
            except Exception as e:
                print(f"Warning: Could not create project entry: {e}")

            return jsonify({
                'success': True,
                'message': 'Cover created successfully',
                'file': str(relative_path)
            })
        except Exception as e:
            return jsonify({'error': f'Cover generation failed: {str(e)}'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/convert-cover', methods=['POST'])
def api_convert_cover():
    """Convert cover from PDF or image format"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']
        target_type = request.form.get('type', 'ebook')  # ebook, paperback, or hardback
        title = request.form.get('title', '')
        author = request.form.get('author', '')
        subtitle = request.form.get('subtitle', '')
        add_text = request.form.get('add_text', 'true') == 'true'
        add_barcode = request.form.get('add_barcode', 'true') == 'true'

        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        # Accept both PDF and image files for covers
        if file and allowed_file(file.filename, 'cover'):
            filename = secure_filename(file.filename)
            filepath = app.config['UPLOAD_FOLDER'] / filename
            file.save(str(filepath))

            # Convert cover
            try:
                generator = CoverGenerator()
                output_path = generator.convert_cover(
                    input_file=filepath,
                    target_type=target_type,
                    output_dir=app.config['OUTPUT_FOLDER'] / 'covers',
                    title=title,
                    subtitle=subtitle,
                    author=author,
                    add_text=add_text,
                    add_barcode_area=add_barcode
                )

                # Convert to relative path for download
                try:
                    relative_path = Path(output_path).relative_to(app.config['OUTPUT_FOLDER'])
                except ValueError:
                    relative_path = Path(output_path).name

                return jsonify({
                    'success': True,
                    'message': f'Cover converted successfully from {Path(filename).suffix.upper()}',
                    'file': str(relative_path)
                })
            except Exception as e:
                return jsonify({'error': f'Cover conversion failed: {str(e)}'}), 500

        return jsonify({'error': 'Invalid file type. Supported: PDF, PNG, JPG, JPEG, BMP, GIF'}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/watermark', methods=['POST'])
def api_watermark():
    """Apply watermark to document"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']
        watermark_text = request.form.get('text', '')
        # Opacity comes as 1-50 from slider, convert to 0.01-0.50
        opacity = float(request.form.get('opacity', 10)) / 100.0
        position = request.form.get('position', 'center')

        # Optional logo file
        logo_file = None
        if 'logo' in request.files and request.files['logo'].filename != '':
            logo_file = request.files['logo']

        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        if file and allowed_file(file.filename, 'document'):
            filename = secure_filename(file.filename)
            filepath = app.config['UPLOAD_FOLDER'] / filename
            file.save(str(filepath))

            # Save logo if provided
            logo_path = None
            if logo_file and allowed_file(logo_file.filename, 'image'):
                logo_filename = secure_filename(logo_file.filename)
                logo_path = app.config['UPLOAD_FOLDER'] / logo_filename
                logo_file.save(str(logo_path))

            # Apply watermark
            try:
                print(f"[WATERMARK] Starting watermark process:")
                print(f"  Input file: {filepath}")
                print(f"  Text: {watermark_text}")
                print(f"  Opacity: {opacity}")
                print(f"  Position: {position}")
                print(f"  Logo: {logo_path}")

                watermarker = Watermarker()
                output_path = watermarker.apply_watermark(
                    input_file=filepath,
                    watermark_text=watermark_text,
                    logo_path=logo_path,
                    opacity=opacity,
                    position=position,
                    output_dir=app.config['OUTPUT_FOLDER'] / 'watermarked'
                )

                print(f"[WATERMARK] Output path: {output_path}")
                print(f"[WATERMARK] File exists: {Path(output_path).exists()}")

                # Convert to relative path for download
                try:
                    relative_path = Path(output_path).relative_to(app.config['OUTPUT_FOLDER'])
                    print(f"[WATERMARK] Relative path: {relative_path}")
                except ValueError as e:
                    relative_path = Path(output_path).name
                    print(f"[WATERMARK] Using filename only: {relative_path}")

                # Create project entry for tracking
                try:
                    metadata = {
                        'original_file': filename,
                        'watermark_text': watermark_text,
                        'opacity': opacity,
                        'position': position,
                        'has_logo': logo_path is not None
                    }

                    project_id = project_manager.create_project(
                        title=f"Watermarked - {filename}",
                        project_type='watermark',
                        metadata=metadata
                    )

                    # Add watermarked file to project
                    project_manager.add_file_to_project(
                        project_id=project_id,
                        file_path=str(relative_path),
                        file_type='watermarked_document'
                    )
                except Exception as e:
                    print(f"Warning: Could not create project entry: {e}")

                return jsonify({
                    'success': True,
                    'message': 'Watermark applied successfully',
                    'file': str(relative_path)
                })
            except Exception as e:
                print(f"[WATERMARK ERROR] {str(e)}")
                import traceback
                traceback.print_exc()
                return jsonify({'error': f'Watermarking failed: {str(e)}'}), 500

        return jsonify({'error': 'Invalid file type'}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/download/<path:filename>')
def api_download(filename):
    """Download generated file"""
    try:
        print(f"[DOWNLOAD] Request for: {filename}")

        # Always treat as relative to OUTPUT_FOLDER
        filepath = app.config['OUTPUT_FOLDER'] / filename

        print(f"[DOWNLOAD] Full path: {filepath}")
        print(f"[DOWNLOAD] File exists: {filepath.exists()}")

        if filepath.exists() and filepath.is_file():
            print(f"[DOWNLOAD] Sending file: {filepath.name}")
            return send_file(str(filepath), as_attachment=True, download_name=filepath.name)
        else:
            print(f"[DOWNLOAD] File not found: {filepath}")
            return jsonify({'error': f'File not found: {filename}'}), 404
    except Exception as e:
        print(f"[DOWNLOAD ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/list-files/<file_type>')
def api_list_files(file_type):
    """List generated files"""
    try:
        if file_type not in ['ebooks', 'covers', 'watermarked']:
            return jsonify({'error': 'Invalid file type'}), 400

        directory = app.config['OUTPUT_FOLDER'] / file_type
        files = []

        if directory.exists():
            for file_path in directory.iterdir():
                # Skip system files (README, .gitkeep, hidden files)
                if file_path.is_file() and not file_path.name.startswith('.') and file_path.name.lower() not in ['readme.md', 'readme', '.gitkeep']:
                    files.append({
                        'name': file_path.name,
                        'size': file_path.stat().st_size,
                        'modified': file_path.stat().st_mtime,
                        'path': str(file_path.relative_to(app.config['OUTPUT_FOLDER']))
                    })

        return jsonify({'files': files})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/check-dependencies')
def api_check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import shutil
        import subprocess
        import platform

        # On Windows, get the full system PATH from the registry
        # because venv may have a truncated PATH
        full_path = os.environ.get('PATH', '')
        if platform.system() == 'Windows':
            try:
                import winreg
                # Get system PATH
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'SYSTEM\CurrentControlSet\Control\Session Manager\Environment') as key:
                    system_path = winreg.QueryValueEx(key, 'Path')[0]

                # Get user PATH
                try:
                    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Environment') as key:
                        user_path = winreg.QueryValueEx(key, 'Path')[0]
                except:
                    user_path = ''

                # Combine: venv\Scripts + system + user
                venv_scripts = os.path.join(sys.prefix, 'Scripts')
                full_path = f"{venv_scripts};{system_path};{user_path}"
            except Exception as e:
                pass  # Fall back to environment PATH

        def check_command(cmd):
            """Check if a command exists and is executable - more robust on Windows"""
            # First try shutil.which with full PATH
            which_result = shutil.which(cmd, path=full_path)
            if which_result:
                return True

            # Fallback: try to actually run the command with --version
            try:
                # Build subprocess arguments
                kwargs = {
                    'stdout': subprocess.PIPE,
                    'stderr': subprocess.PIPE,
                    'timeout': 5,
                    'env': {**os.environ, 'PATH': full_path}  # Use full PATH
                }

                # Add Windows-specific flags to hide console window
                if platform.system() == 'Windows':
                    kwargs['creationflags'] = 0x08000000  # CREATE_NO_WINDOW

                result = subprocess.run([cmd, '--version'], **kwargs)
                return result.returncode == 0
            except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
                return False

        dependencies = {
            'pandoc': check_command('pandoc'),
            'wkhtmltopdf': check_command('wkhtmltopdf'),
            'pdflatex': check_command('pdflatex')
        }

        return jsonify({
            'dependencies': dependencies,
            'all_met': dependencies['pandoc']  # Only pandoc is required
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def open_browser():
    """Open web browser after server starts"""
    webbrowser.open('http://127.0.0.1:5000')


# ==========================================
# AI ASSISTANT ROUTES
# ==========================================

@app.route('/settings')
def settings():
    """Settings page for AI configuration"""
    return render_template('settings.html')


@app.route('/api/ai/status', methods=['GET'])
def ai_status():
    """Check AI assistant status"""
    api_key = ai_assistant.config.get('groq_api_key', '')
    # Show last 4 digits of API key if exists
    masked_key = ''
    if api_key:
        masked_key = f"...{api_key[-4:]}" if len(api_key) > 4 else "****"

    # Get current model info
    model_id = ai_assistant.get_current_model()
    model_info = ai_assistant.get_current_model_info()

    return jsonify({
        'enabled': ai_assistant.is_enabled(),
        'model': model_id,
        'model_info': model_info,
        'has_key': bool(api_key),
        'masked_key': masked_key
    })


@app.route('/api/ai/set-key', methods=['POST'])
def ai_set_key():
    """Set and validate Groq API key"""
    try:
        data = request.get_json()
        api_key = data.get('api_key', '').strip()

        if not api_key:
            return jsonify({'error': 'API key is required'}), 400

        success, message = ai_assistant.set_api_key(api_key)

        if success:
            return jsonify({
                'success': True,
                'message': message,
                'enabled': True
            })
        else:
            return jsonify({'error': message}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/ai/clear-key', methods=['POST'])
def ai_clear_key():
    """Clear/remove Groq API key"""
    try:
        # Clear the API key
        ai_assistant.client = None
        ai_assistant.enabled = False
        ai_assistant.config['groq_api_key'] = ''
        ai_assistant.config['ai_enabled'] = False
        ai_assistant._save_config()

        return jsonify({
            'success': True,
            'message': '✓ API key cleared successfully. AI features disabled.'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/ai/models', methods=['GET'])
def ai_get_models():
    """Get available Groq models"""
    try:
        models = ai_assistant.get_available_models()
        return jsonify({
            'success': True,
            'models': models
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/ai/current-model', methods=['GET'])
def ai_get_current_model():
    """Get currently selected model"""
    try:
        current_model = ai_assistant.get_current_model()
        model_info = ai_assistant.get_current_model_info()
        return jsonify({
            'success': True,
            'model_id': current_model,
            'model_info': model_info
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/ai/set-model', methods=['POST'])
def ai_set_model():
    """Set/change the active model"""
    try:
        data = request.get_json()
        model_id = data.get('model_id', '')

        if not model_id:
            return jsonify({'error': 'Model ID is required'}), 400

        success, message = ai_assistant.set_model(model_id)

        if success:
            return jsonify({
                'success': True,
                'message': message,
                'model_id': model_id,
                'model_info': ai_assistant.get_current_model_info()
            })
        else:
            return jsonify({'error': message}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/ai/suggest-title', methods=['POST'])
def ai_suggest_title():
    """AI-powered book title suggestion"""
    try:
        data = request.get_json()
        topic = data.get('topic', '')
        genre = data.get('genre', '')

        if not ai_assistant.is_enabled():
            return jsonify({'error': 'AI assistant not enabled. Please configure API key in Settings.'}), 400

        title = ai_assistant.suggest_cover_title(topic, genre)

        if title:
            return jsonify({'success': True, 'title': title})
        else:
            return jsonify({'error': 'Failed to generate title'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/ai/suggest-subtitle', methods=['POST'])
def ai_suggest_subtitle():
    """AI-powered subtitle suggestion"""
    try:
        data = request.get_json()
        title = data.get('title', '')
        topic = data.get('topic', '')

        if not ai_assistant.is_enabled():
            return jsonify({'error': 'AI assistant not enabled'}), 400

        subtitle = ai_assistant.suggest_cover_subtitle(title, topic)

        if subtitle:
            return jsonify({'success': True, 'subtitle': subtitle})
        else:
            return jsonify({'error': 'Failed to generate subtitle'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/ai/suggest-colors', methods=['POST'])
def ai_suggest_colors():
    """AI-powered color scheme suggestion"""
    try:
        data = request.get_json()
        genre = data.get('genre', '')
        mood = data.get('mood', '')

        if not ai_assistant.is_enabled():
            return jsonify({'error': 'AI assistant not enabled'}), 400

        colors = ai_assistant.suggest_color_scheme(genre, mood)

        if colors:
            return jsonify({'success': True, 'colors': colors})
        else:
            return jsonify({'error': 'Failed to generate colors'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/ai/suggest-style', methods=['POST'])
def ai_suggest_style():
    """AI-powered cover style suggestion"""
    try:
        data = request.get_json()
        genre = data.get('genre', '')
        audience = data.get('audience', '')

        if not ai_assistant.is_enabled():
            return jsonify({'error': 'AI assistant not enabled'}), 400

        style = ai_assistant.suggest_cover_style(genre, audience)

        if style:
            return jsonify({'success': True, 'style': style})
        else:
            return jsonify({'error': 'Failed to suggest style'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/ai/suggest-spine-color', methods=['POST'])
def ai_suggest_spine_color():
    """AI-powered spine color suggestion based on uploaded cover"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400

        file = request.files['file']
        title = request.form.get('title', 'Untitled Book')

        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        if not ai_assistant.is_enabled():
            return jsonify({'error': 'AI assistant not enabled'}), 400

        # Save uploaded file temporarily
        temp_path = app.config['UPLOAD_FOLDER'] / f"temp_spine_{file.filename}"
        file.save(str(temp_path))

        try:
            # Load image and extract dominant colors
            from PIL import Image
            import fitz  # PyMuPDF

            # Check if file is PDF - convert to image first
            if file.filename.lower().endswith('.pdf'):
                # Open PDF and convert first page to image
                pdf_doc = fitz.open(str(temp_path))
                page = pdf_doc[0]  # First page
                pix = page.get_pixmap(dpi=150)  # 150 DPI for color extraction

                # Convert pixmap to PIL Image
                img_data = pix.tobytes("png")
                import io
                img = Image.open(io.BytesIO(img_data))
                pdf_doc.close()
            else:
                # Regular image file
                img = Image.open(temp_path)

            if img.mode != 'RGB':
                img = img.convert('RGB')

            # Use cover generator to extract dominant colors
            from modules.covers.cover_generator import CoverGenerator
            generator = CoverGenerator()
            dominant_colors = generator.extract_dominant_colors(img, num_colors=5)

            # Use AI to suggest best spine color
            spine_color_rgb = generator.get_ai_spine_color(dominant_colors, title=title)

            # Convert RGB to hex
            spine_color_hex = '#{:02x}{:02x}{:02x}'.format(*spine_color_rgb)

            return jsonify({'success': True, 'color': spine_color_hex})

        finally:
            # Clean up temp file
            if temp_path.exists():
                temp_path.unlink()

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/ai/generate-description', methods=['POST'])
def ai_generate_description():
    """AI-powered book description generation"""
    try:
        data = request.get_json()
        title = data.get('title', '')
        subtitle = data.get('subtitle', '')
        topic = data.get('topic', '')
        audience = data.get('audience', '')
        key_points = data.get('key_points', [])

        if not ai_assistant.is_enabled():
            return jsonify({'error': 'AI assistant not enabled'}), 400

        description = ai_assistant.generate_book_description(
            title, subtitle, topic, audience, key_points
        )

        if description:
            return jsonify({'success': True, 'description': description})
        else:
            return jsonify({'error': 'Failed to generate description'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/ai/generate-bio', methods=['POST'])
def ai_generate_bio():
    """AI-powered author bio generation"""
    try:
        data = request.get_json()
        name = data.get('name', '')
        expertise = data.get('expertise', '')
        achievements = data.get('achievements', '')

        if not ai_assistant.is_enabled():
            return jsonify({'error': 'AI assistant not enabled'}), 400

        bio = ai_assistant.generate_author_bio(name, expertise, achievements)

        if bio:
            return jsonify({'success': True, 'bio': bio})
        else:
            return jsonify({'error': 'Failed to generate bio'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/ai/generate-outline', methods=['POST'])
def ai_generate_outline():
    """AI-powered chapter outline generation"""
    try:
        data = request.get_json()
        topic = data.get('topic', '')
        chapters = data.get('chapters', 10)

        if not ai_assistant.is_enabled():
            return jsonify({'error': 'AI assistant not enabled'}), 400

        outline = ai_assistant.generate_chapter_outline(topic, chapters)

        if outline:
            return jsonify({'success': True, 'outline': outline})
        else:
            return jsonify({'error': 'Failed to generate outline'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/ai/generate-chapter', methods=['POST'])
def ai_generate_chapter():
    """AI-powered chapter content generation"""
    try:
        data = request.get_json()
        chapter_title = data.get('chapter_title', '')
        book_topic = data.get('book_topic', '')
        word_count = data.get('word_count', 1500)

        if not ai_assistant.is_enabled():
            return jsonify({'error': 'AI assistant not enabled'}), 400

        content = ai_assistant.generate_chapter_content(chapter_title, book_topic, word_count)

        if content:
            return jsonify({'success': True, 'content': content})
        else:
            return jsonify({'error': 'Failed to generate content'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/ai/proofread', methods=['POST'])
def ai_proofread():
    """AI-powered proofreading"""
    try:
        data = request.get_json()
        text = data.get('text', '')

        if not ai_assistant.is_enabled():
            return jsonify({'error': 'AI assistant not enabled'}), 400

        corrected = ai_assistant.proofread_text(text)

        if corrected:
            return jsonify({'success': True, 'text': corrected})
        else:
            return jsonify({'error': 'Failed to proofread'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/ai/improve-readability', methods=['POST'])
def ai_improve_readability():
    """AI-powered readability improvement"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        grade_level = data.get('grade_level', 8)

        if not ai_assistant.is_enabled():
            return jsonify({'error': 'AI assistant not enabled'}), 400

        improved = ai_assistant.improve_readability(text, grade_level)

        if improved:
            return jsonify({'success': True, 'text': improved})
        else:
            return jsonify({'error': 'Failed to improve readability'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/ai/expand', methods=['POST'])
def ai_expand():
    """AI-powered text expansion"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        target_length = data.get('target_length')

        if not ai_assistant.is_enabled():
            return jsonify({'error': 'AI assistant not enabled'}), 400

        expanded = ai_assistant.expand_text(text, target_length)

        if expanded:
            return jsonify({'success': True, 'text': expanded})
        else:
            return jsonify({'error': 'Failed to expand text'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/ai/summarize', methods=['POST'])
def ai_summarize():
    """AI-powered text summarization"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        target_length = data.get('target_length', 100)

        if not ai_assistant.is_enabled():
            return jsonify({'error': 'AI assistant not enabled'}), 400

        summary = ai_assistant.summarize_text(text, target_length)

        if summary:
            return jsonify({'success': True, 'text': summary})
        else:
            return jsonify({'error': 'Failed to summarize'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/ai/transform-text', methods=['POST'])
def ai_transform_text():
    """Unified endpoint for text transformation (expand or summarize)"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        action = data.get('action', 'expand')  # 'expand' or 'summarize'
        target_length = data.get('target_length')

        if not ai_assistant.is_enabled():
            return jsonify({'error': 'AI assistant not enabled'}), 400

        if action == 'expand':
            result = ai_assistant.expand_text(text, target_length)
        elif action == 'summarize':
            result = ai_assistant.summarize_text(text, target_length or 100)
        else:
            return jsonify({'error': 'Invalid action. Must be "expand" or "summarize"'}), 400

        if result:
            return jsonify({'success': True, 'transformed_text': result})
        else:
            return jsonify({'error': f'Failed to {action} text'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/ai/generate-keywords', methods=['POST'])
def ai_generate_keywords():
    """AI-powered KDP keywords generation"""
    try:
        data = request.get_json()
        title = data.get('title', '')
        topic = data.get('topic', '')
        genre = data.get('genre', '')

        if not ai_assistant.is_enabled():
            return jsonify({'error': 'AI assistant not enabled'}), 400

        keywords = ai_assistant.generate_kdp_keywords(title, topic, genre)

        if keywords:
            return jsonify({'success': True, 'keywords': keywords})
        else:
            return jsonify({'error': 'Failed to generate keywords'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/ai/suggest-categories', methods=['POST'])
def ai_suggest_categories():
    """AI-powered KDP categories suggestion"""
    try:
        data = request.get_json()
        title = data.get('title', '')
        topic = data.get('topic', '')
        genre = data.get('genre', '')

        if not ai_assistant.is_enabled():
            return jsonify({'error': 'AI assistant not enabled'}), 400

        categories = ai_assistant.suggest_kdp_categories(title, topic, genre)

        if categories:
            return jsonify({'success': True, 'categories': categories})
        else:
            return jsonify({'error': 'Failed to suggest categories'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/ai/generate-marketing', methods=['POST'])
def ai_generate_marketing():
    """AI-powered marketing copy generation"""
    try:
        data = request.get_json()
        title = data.get('title', '')
        description = data.get('description', '')
        cta = data.get('cta', 'Get your copy today!')

        if not ai_assistant.is_enabled():
            return jsonify({'error': 'AI assistant not enabled'}), 400

        marketing = ai_assistant.generate_marketing_copy(title, description, cta)

        if marketing:
            return jsonify({'success': True, 'marketing': marketing})
        else:
            return jsonify({'error': 'Failed to generate marketing copy'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/ai/generate-back-cover', methods=['POST'])
def ai_generate_back_cover():
    """AI-powered back cover copy generation"""
    try:
        data = request.get_json()
        title = data.get('title', '')
        subtitle = data.get('subtitle', '')
        description = data.get('description', '')

        if not ai_assistant.is_enabled():
            return jsonify({'error': 'AI assistant not enabled'}), 400

        back_cover = ai_assistant.generate_back_cover_copy(title, subtitle, description)

        if back_cover:
            return jsonify({'success': True, 'back_cover': back_cover})
        else:
            return jsonify({'error': 'Failed to generate back cover copy'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/ai/chat', methods=['POST'])
def ai_chat():
    """General AI chat endpoint for conversational questions"""
    try:
        data = request.get_json()
        message = data.get('message', '').strip()

        if not message:
            return jsonify({'error': 'No message provided'}), 400

        if not ai_assistant.is_enabled():
            return jsonify({'error': 'AI assistant not enabled. Please configure API key in Settings.'}), 400

        # Use the AI assistant's client to generate a response
        try:
            response = ai_assistant.client.chat.completions.create(
                model=ai_assistant.config.get('default_model', 'llama-3.3-70b-versatile'),
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful AI assistant for an e-book creation tool. "
                                   "You help users with book writing, cover design, document conversion, "
                                   "and publishing. Be concise, friendly, and practical. "
                                   "Use emojis occasionally to make responses engaging."
                    },
                    {
                        "role": "user",
                        "content": message
                    }
                ],
                temperature=0.7,
                max_tokens=500
            )

            ai_response = response.choices[0].message.content

            return jsonify({
                'success': True,
                'response': ai_response
            })

        except Exception as e:
            print(f"AI chat error: {e}")
            return jsonify({'error': 'Failed to generate response'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/ai/generate', methods=['POST'])
def ai_generate():
    """Generic AI generation endpoint for custom prompts"""
    try:
        data = request.get_json()
        prompt = data.get('prompt', '').strip()
        max_tokens = data.get('max_tokens', 1000)

        if not prompt:
            return jsonify({'error': 'No prompt provided'}), 400

        if not ai_assistant.is_enabled():
            return jsonify({'error': 'AI assistant not enabled. Please configure API key in Settings.'}), 400

        # Use the AI assistant's client to generate content
        try:
            response = ai_assistant.client.chat.completions.create(
                model=ai_assistant.config.get('default_model', 'llama-3.3-70b-versatile'),
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional book writing assistant. Generate high-quality content "
                                   "based on the user's prompt. Be creative, detailed, and engaging."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=max_tokens
            )

            generated_text = response.choices[0].message.content

            return jsonify({
                'success': True,
                'text': generated_text
            })

        except Exception as e:
            print(f"AI generate error: {e}")
            return jsonify({'error': 'Failed to generate content'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Settings API Endpoints
OUTPUT_DIR = app.config['OUTPUT_FOLDER']
SETTINGS_FILE = os.path.join(OUTPUT_DIR, '.settings.json')

def load_user_settings():
    """Load user settings from file"""
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {'storage': 'local', 'autosave_interval': 3}

def save_user_settings(settings):
    """Save user settings to file"""
    try:
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f, indent=2)
        return True
    except:
        return False

@app.route('/api/settings/get-preferences', methods=['GET'])
def get_preferences():
    """Get user preferences"""
    try:
        settings = load_user_settings()
        return jsonify({'success': True, **settings})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/settings/storage-preference', methods=['POST'])
def update_storage_preference():
    """Update storage preference"""
    try:
        data = request.get_json()
        storage = data.get('storage', 'local')

        settings = load_user_settings()
        settings['storage'] = storage

        if save_user_settings(settings):
            return jsonify({'success': True, 'storage': storage})
        else:
            return jsonify({'error': 'Failed to save settings'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/settings/autosave-interval', methods=['POST'])
def update_autosave_interval():
    """Update auto-save interval"""
    try:
        data = request.get_json()
        interval = data.get('interval', 3)

        settings = load_user_settings()
        settings['autosave_interval'] = interval

        if save_user_settings(settings):
            return jsonify({'success': True, 'interval': interval})
        else:
            return jsonify({'error': 'Failed to save settings'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Marketing Project API Endpoints
MARKETING_DIR = os.path.join(OUTPUT_DIR, 'marketing')

@app.route('/api/marketing/save-project', methods=['POST'])
def save_marketing_project():
    """Save marketing project to file"""
    try:
        data = request.get_json()
        project_data = data.get('data', {})
        project_name = data.get('name', project_data.get('title', 'Untitled Project'))

        # Sanitize filename
        safe_name = "".join([c if c.isalnum() or c in (' ', '-', '_') else '_' for c in project_name])
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{safe_name}_{timestamp}.json"
        filepath = os.path.join(MARKETING_DIR, filename)

        # Create full project object
        project = {
            'version': '1.0',
            'project_name': project_name,
            'created': datetime.now().isoformat(),
            'modified': datetime.now().isoformat(),
            'data': project_data
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(project, f, indent=2, ensure_ascii=False)

        return jsonify({
            'success': True,
            'filename': filename,
            'filepath': filepath,
            'message': f'Project "{project_name}" saved successfully'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/marketing/list-projects', methods=['GET'])
def list_marketing_projects():
    """List all saved marketing projects"""
    try:
        projects = []

        if os.path.exists(MARKETING_DIR):
            for filename in os.listdir(MARKETING_DIR):
                if filename.endswith('.json'):
                    filepath = os.path.join(MARKETING_DIR, filename)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            project = json.load(f)
                            projects.append({
                                'filename': filename,
                                'name': project.get('project_name', 'Untitled'),
                                'created': project.get('created', ''),
                                'modified': project.get('modified', ''),
                                'title': project.get('data', {}).get('title', ''),
                                'genre': project.get('data', {}).get('genre', '')
                            })
                    except:
                        continue

        # Sort by modified date (newest first)
        projects.sort(key=lambda x: x['modified'], reverse=True)

        return jsonify({'success': True, 'projects': projects})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/marketing/load-project/<filename>', methods=['GET'])
def load_marketing_project(filename):
    """Load a specific marketing project"""
    try:
        filepath = os.path.join(MARKETING_DIR, filename)

        if not os.path.exists(filepath):
            return jsonify({'error': 'Project not found'}), 404

        with open(filepath, 'r', encoding='utf-8') as f:
            project = json.load(f)

        return jsonify({'success': True, 'project': project})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/marketing/delete-project/<filename>', methods=['DELETE'])
def delete_marketing_project(filename):
    """Delete a marketing project"""
    try:
        filepath = os.path.join(MARKETING_DIR, filename)

        if not os.path.exists(filepath):
            return jsonify({'error': 'Project not found'}), 404

        os.remove(filepath)

        return jsonify({'success': True, 'message': 'Project deleted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Project Management API Endpoints
@app.route('/api/projects/stats', methods=['GET'])
def get_project_stats():
    """Get project statistics"""
    try:
        stats = project_manager.get_stats()
        return jsonify({'success': True, 'stats': stats})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/projects/recent', methods=['GET'])
def get_recent_projects():
    """Get recent projects"""
    try:
        limit = request.args.get('limit', 10, type=int)
        project_type = request.args.get('type')
        projects = project_manager.get_recent_projects(limit=limit, project_type=project_type)
        return jsonify({'success': True, 'projects': projects})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/projects/create', methods=['POST'])
def create_project():
    """Create a new project"""
    try:
        data = request.get_json()
        title = data.get('title', 'Untitled Project')
        project_type = data.get('type', 'ebook')
        metadata = data.get('metadata', {})
        tags = data.get('tags', [])

        project_id = project_manager.create_project(
            title=title,
            project_type=project_type,
            metadata=metadata,
            tags=tags
        )

        return jsonify({'success': True, 'project_id': project_id})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/projects/<project_id>', methods=['GET'])
def get_project(project_id):
    """Get a specific project"""
    try:
        project = project_manager.get_project(project_id)
        if project:
            return jsonify({'success': True, 'project': project})
        else:
            return jsonify({'error': 'Project not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/projects/<project_id>', methods=['PUT'])
def update_project(project_id):
    """Update a project"""
    try:
        data = request.get_json()
        success = project_manager.update_project(project_id, **data)
        if success:
            return jsonify({'success': True})
        else:
            return jsonify({'error': 'Project not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/projects/<project_id>', methods=['DELETE'])
def delete_project(project_id):
    """Delete a project"""
    try:
        success = project_manager.delete_project(project_id)
        if success:
            return jsonify({'success': True})
        else:
            return jsonify({'error': 'Project not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/projects/clear', methods=['POST'])
def clear_project_history():
    """Clear all project history"""
    try:
        success = project_manager.clear_project_history()
        if success:
            return jsonify({'success': True, 'message': 'Project history cleared'})
        else:
            return jsonify({'error': 'Failed to clear project history'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/projects/clear-files', methods=['POST'])
def clear_output_files():
    """Clear output files"""
    try:
        data = request.get_json() or {}
        file_type = data.get('type')  # 'ebooks', 'covers', 'watermarked', or None for all
        results = project_manager.clear_output_files(file_type=file_type)
        return jsonify({
            'success': True,
            'message': f"Deleted {results['deleted']} file(s)",
            'results': results
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/projects/reset-all', methods=['POST'])
def reset_all_data():
    """Reset everything - clear projects and files"""
    try:
        results = project_manager.reset_all()
        return jsonify({
            'success': True,
            'message': 'All data has been reset',
            'results': results
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Cover Templates API
@app.route('/api/cover-templates', methods=['GET'])
def get_cover_templates():
    """Get available cover templates"""
    try:
        templates_file = os.path.join(os.path.dirname(__file__), 'config', 'cover_templates.json')
        with open(templates_file, 'r', encoding='utf-8') as f:
            templates_data = json.load(f)
        return jsonify({'success': True, 'templates': templates_data['templates']})
    except Exception as e:
        print(f"Error loading templates: {e}")
        return jsonify({'error': str(e)}), 500


def main():
    """Start the Flask server"""
    import platform

    print("=" * 60)
    print("E-Book Maker - Web Interface")
    print(f"Platform: {platform.system()} {platform.release()}")
    print("=" * 60)

    # Check dependencies
    print("\nChecking dependencies...")
    converter = EBookConverter()
    deps = converter.check_dependencies()

    print(f"  Pandoc:       {'✓ Found' if deps['pandoc'] else '✗ NOT FOUND - REQUIRED!'}")
    print(f"  wkhtmltopdf:  {'✓ Found' if deps['wkhtmltopdf'] else '○ Not found (optional)'}")
    print(f"  pdflatex:     {'✓ Found' if deps['pdflatex'] else '○ Not found (optional)'}")
    print(f"  weasyprint:   {'✓ Found' if deps['weasyprint'] else '○ Not found (optional)'}")

    # Check if at least one PDF engine is available
    pdf_engines_found = deps['wkhtmltopdf'] or deps['pdflatex'] or deps['weasyprint']
    if not pdf_engines_found:
        print("\n⚠ WARNING: No PDF engines found!")
        print("  PDF conversion will NOT work.")
        print("  Install at least one: wkhtmltopdf, pdflatex, or weasyprint")
        print(f"  Run verification script: scripts/verify-setup-{'windows.ps1' if platform.system() == 'Windows' else 'linux.sh'}")
    else:
        available_engine = converter.get_available_pdf_engine()
        print(f"\n✓ PDF engine available: {available_engine}")

    if not deps['pandoc']:
        print("\n✗ CRITICAL: Pandoc not found!")
        print("  Most conversion features will NOT work.")
        print("  Download from: https://pandoc.org/installing.html")
        print()
        input("Press Enter to continue anyway (NOT recommended)...")

    # Check AI status
    if ai_assistant.is_enabled():
        print("✓ AI Assistant: ENABLED")
        print(f"  Model: {ai_assistant.config.get('default_model')}")
    else:
        print("○ AI Assistant: Not configured")
        print("  Configure in Settings to enable AI features")

    print("=" * 60)
    print(f"Starting server on http://127.0.0.1:5000")
    print("Press Ctrl+C to stop the server")
    print("=" * 60)

    # Open browser after 1.5 seconds
    Timer(1.5, open_browser).start()

    # Start Flask server
    app.run(host='127.0.0.1', port=5000, debug=False)


if __name__ == '__main__':
    main()
