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
except ImportError as e:
    print(f"Warning: Module import failed: {e}")
    print("Some features may not be available until all modules are created.")

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
    'image': {'png', 'jpg', 'jpeg', 'gif', 'bmp'}
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

        if not files or files[0].filename == '':
            return jsonify({'error': 'No files selected'}), 400

        # Save uploaded files
        input_files = []
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
            converter = EBookConverter()
            results = converter.convert(
                input_files=input_files,
                output_formats=output_formats,
                title=title,
                author=author,
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
        data = request.get_json()

        cover_type = data.get('type', 'ebook')  # ebook or paperback
        title = data.get('title', 'Book Title')
        subtitle = data.get('subtitle', '')
        author = data.get('author', 'Author Name')
        style = data.get('style', 'gradient')
        colors = data.get('colors', {'primary': '#667eea', 'secondary': '#764ba2'})

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
                output_dir=app.config['OUTPUT_FOLDER'] / 'covers'
            )

            # Convert to relative path for download
            try:
                relative_path = Path(cover_path).relative_to(app.config['OUTPUT_FOLDER'])
            except ValueError:
                relative_path = Path(cover_path).name

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
    """Convert cover image format"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']
        target_type = request.form.get('type', 'ebook')  # ebook or paperback

        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        if file and allowed_file(file.filename, 'image'):
            filename = secure_filename(file.filename)
            filepath = app.config['UPLOAD_FOLDER'] / filename
            file.save(str(filepath))

            # Convert cover
            try:
                generator = CoverGenerator()
                output_path = generator.convert_cover(
                    input_file=filepath,
                    target_type=target_type,
                    output_dir=app.config['OUTPUT_FOLDER'] / 'covers'
                )

                # Convert to relative path for download
                try:
                    relative_path = Path(output_path).relative_to(app.config['OUTPUT_FOLDER'])
                except ValueError:
                    relative_path = Path(output_path).name

                return jsonify({
                    'success': True,
                    'message': 'Cover converted successfully',
                    'file': str(relative_path)
                })
            except Exception as e:
                return jsonify({'error': f'Cover conversion failed: {str(e)}'}), 500

        return jsonify({'error': 'Invalid file type'}), 400

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
                if file_path.is_file():
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


def main():
    """Start the Flask server"""
    print("=" * 60)
    print("E-Book Maker - Web Interface")
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
