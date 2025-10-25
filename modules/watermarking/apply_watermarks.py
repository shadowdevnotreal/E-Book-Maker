#!/usr/bin/env python3
"""
Batch Watermarking Tool - Diatasso PRCM™
PRIVATE - Apply watermarks to all generated documents
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
import argparse
import shutil

# Import the watermarking system
try:
    from watermark_generator import DiatassoWatermarkSystem
except ImportError:
    print("Error: watermark_generator module not found")
    sys.exit(1)

class BatchWatermarkProcessor:
    """Process multiple documents with Diatasso watermarks"""

    def __init__(self):
        self.watermark_system = DiatassoWatermarkSystem()
        self.processed_files = []
        self.failed_files = []
        self.project_root = Path(__file__).parent.parent

    def find_generated_documents(self):
        """Find all generated documents that need watermarking"""
        document_paths = []

        # Generated folder
        generated_dir = self.project_root / "generated"
        if generated_dir.exists():
            document_paths.extend(list(generated_dir.rglob("*.pdf")))
            document_paths.extend(list(generated_dir.rglob("*.docx")))
            document_paths.extend(list(generated_dir.rglob("*.html")))

        # Web downloads
        web_downloads = self.project_root / "generated" / "web_downloads"
        if web_downloads.exists():
            document_paths.extend(list(web_downloads.rglob("*.pdf")))
            document_paths.extend(list(web_downloads.rglob("*.docx")))
            document_paths.extend(list(web_downloads.rglob("*.html")))

        # Interactive tools (HTML files)
        interactive_dir = self.project_root / "interactive_tools"
        if interactive_dir.exists():
            document_paths.extend(list(interactive_dir.glob("*.html")))

        return document_paths

    def is_already_watermarked(self, file_path):
        """Check if file is already watermarked"""
        metadata_file = Path(str(file_path) + '.watermark.json')
        return metadata_file.exists()

    def watermark_html_file(self, file_path):
        """Add watermark to HTML file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Check if already watermarked
            if 'diatasso-watermark' in content.lower():
                print(f"  ⚠️  Already watermarked: {file_path.name}")
                return True

            # Add watermark CSS and elements
            watermark_css = self.watermark_system.generate_html_watermark_css()
            copyright_text = self.watermark_system.copyright

            # Insert CSS before </head>
            if '</head>' in content:
                content = content.replace('</head>', f'<style>{watermark_css}</style></head>')
            else:
                # Add to beginning if no head tag
                content = f'<style>{watermark_css}</style>\n' + content

            # Insert watermark div after <body>
            if '<body>' in content:
                content = content.replace('<body>',
                    f'<body><div class="diatasso-watermark"></div><div class="diatasso-copyright">{copyright_text}</div>')
            elif '<body' in content:
                # Handle body with attributes
                import re
                content = re.sub(r'(<body[^>]*>)',
                    rf'\1<div class="diatasso-watermark"></div><div class="diatasso-copyright">{copyright_text}</div>', content)
            else:
                # Add at beginning if no body tag
                content = f'<div class="diatasso-watermark"></div><div class="diatasso-copyright">{copyright_text}</div>\n' + content

            # Write watermarked content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            return True

        except Exception as e:
            print(f"  ❌ Error watermarking HTML {file_path.name}: {e}")
            return False

    def watermark_pdf_file(self, file_path):
        """Add watermark to PDF file"""
        try:
            # Create backup
            backup_path = file_path.with_suffix(file_path.suffix + '.backup')
            shutil.copy2(file_path, backup_path)

            # Apply watermark
            if self.watermark_system.apply_watermark_to_pdf(str(file_path), str(file_path)):
                print(f"  ✅ PDF watermarked: {file_path.name}")
                return True
            else:
                # Restore backup if failed
                shutil.move(backup_path, file_path)
                print(f"  ❌ Failed to watermark PDF: {file_path.name}")
                return False

        except Exception as e:
            print(f"  ❌ Error watermarking PDF {file_path.name}: {e}")
            return False

    def watermark_docx_file(self, file_path):
        """Add watermark metadata to DOCX file"""
        try:
            # For DOCX files, we'll add metadata and create a watermarked HTML version
            metadata = self.watermark_system.save_watermark_metadata(str(file_path))
            print(f"  ✅ DOCX metadata added: {file_path.name}")

            # Create HTML version with watermark
            html_path = file_path.with_suffix('.watermarked.html')
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>Watermarked Document - {file_path.stem}</title>
                <style>
                    {self.watermark_system.generate_html_watermark_css()}
                    body {{ font-family: Arial, sans-serif; padding: 2rem; line-height: 1.6; }}
                </style>
            </head>
            <body>
                <div class="diatasso-watermark"></div>
                <div class="diatasso-copyright">{self.watermark_system.copyright}</div>

                <h1>Document: {file_path.name}</h1>
                <p><strong>Note:</strong> This DOCX file has been processed with Diatasso PRCM™ watermarking.</p>
                <p><strong>Original file:</strong> {file_path.name}</p>
                <p><strong>Processed:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>

                <h2>Protection Information</h2>
                <ul>
                    <li>Document is protected with Diatasso PRCM™ watermarking</li>
                    <li>Intellectual property protection applied</li>
                    <li>Unauthorized distribution is prohibited</li>
                </ul>

                <p>To view the original document content, open: <code>{file_path.name}</code></p>
            </body>
            </html>
            """

            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)

            print(f"  ✅ DOCX companion HTML created: {html_path.name}")
            return True

        except Exception as e:
            print(f"  ❌ Error processing DOCX {file_path.name}: {e}")
            return False

    def process_file(self, file_path):
        """Process a single file for watermarking"""
        if self.is_already_watermarked(file_path):
            print(f"  ⚠️  Already processed: {file_path.name}")
            return True

        suffix = file_path.suffix.lower()

        if suffix == '.html':
            success = self.watermark_html_file(file_path)
        elif suffix == '.pdf':
            success = self.watermark_pdf_file(file_path)
        elif suffix == '.docx':
            success = self.watermark_docx_file(file_path)
        else:
            print(f"  ⚠️  Unsupported format: {file_path.name}")
            return False

        if success:
            self.watermark_system.save_watermark_metadata(str(file_path))
            self.processed_files.append(file_path)
        else:
            self.failed_files.append(file_path)

        return success

    def run_batch_processing(self, target_dir=None):
        """Run batch watermarking on all generated documents"""
        print("🎨 Diatasso PRCM™ Batch Watermarking System")
        print("=" * 50)

        if target_dir:
            target_path = Path(target_dir)
            if not target_path.exists():
                print(f"❌ Target directory not found: {target_dir}")
                return False

            documents = list(target_path.rglob("*.pdf"))
            documents.extend(list(target_path.rglob("*.docx")))
            documents.extend(list(target_path.rglob("*.html")))
        else:
            documents = self.find_generated_documents()

        if not documents:
            print("📄 No documents found to watermark")
            return True

        print(f"📋 Found {len(documents)} documents to process")
        print()

        for doc_path in documents:
            print(f"🔄 Processing: {doc_path.relative_to(self.project_root)}")
            self.process_file(doc_path)

        print()
        print("📊 WATERMARKING SUMMARY")
        print("=" * 30)
        print(f"✅ Successfully processed: {len(self.processed_files)}")
        print(f"❌ Failed: {len(self.failed_files)}")
        print(f"📄 Total documents: {len(documents)}")

        if self.processed_files:
            print("\n✅ Successfully watermarked:")
            for file_path in self.processed_files:
                print(f"   • {file_path.name}")

        if self.failed_files:
            print("\n❌ Failed to watermark:")
            for file_path in self.failed_files:
                print(f"   • {file_path.name}")

        # Generate report
        self.generate_watermarking_report()

        return len(self.failed_files) == 0

    def generate_watermarking_report(self):
        """Generate detailed watermarking report"""
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'total_documents': len(self.processed_files) + len(self.failed_files),
            'successfully_processed': len(self.processed_files),
            'failed': len(self.failed_files),
            'processed_files': [str(f) for f in self.processed_files],
            'failed_files': [str(f) for f in self.failed_files],
            'watermark_system': 'Diatasso PRCM™',
            'copyright': self.watermark_system.copyright
        }

        report_file = self.project_root / 'private_watermark_system' / 'watermarking_report.json'
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2)

        print(f"\n📋 Detailed report saved: {report_file}")

def main():
    """CLI interface for batch watermarking"""
    parser = argparse.ArgumentParser(
        description='Diatasso PRCM™ Batch Watermarking System'
    )
    parser.add_argument('--target', help='Target directory to watermark (default: auto-detect)')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be processed without making changes')
    parser.add_argument('--force', action='store_true', help='Re-watermark already processed files')

    args = parser.parse_args()

    processor = BatchWatermarkProcessor()

    if args.dry_run:
        print("🔍 DRY RUN MODE - No files will be modified")
        documents = processor.find_generated_documents() if not args.target else list(Path(args.target).rglob("*"))
        print(f"Would process {len(documents)} documents:")
        for doc in documents:
            print(f"  • {doc}")
        return

    if args.force:
        # Remove existing watermark metadata to force re-processing
        print("🔄 Force mode: Removing existing watermark metadata")
        if args.target:
            target_path = Path(args.target)
            metadata_files = list(target_path.rglob("*.watermark.json"))
        else:
            metadata_files = list(processor.project_root.rglob("*.watermark.json"))

        for metadata_file in metadata_files:
            metadata_file.unlink()
        print(f"Removed {len(metadata_files)} metadata files")

    success = processor.run_batch_processing(args.target)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()