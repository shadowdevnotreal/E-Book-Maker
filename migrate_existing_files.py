#!/usr/bin/env python3
"""
Migration script to import existing files into the project database
This creates project entries for files that were created before ProjectManager was implemented
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent))

from modules.project_manager import ProjectManager

def migrate_existing_files():
    """Import existing output files into the project database"""

    print("="*60)
    print("E-Book Maker - File Migration Script")
    print("="*60)
    print()

    base_dir = Path(__file__).parent
    project_manager = ProjectManager()

    migrated_count = 0

    # Migrate e-books
    print("📚 Migrating E-books...")
    ebooks_dir = base_dir / 'output' / 'ebooks'
    if ebooks_dir.exists():
        for file in ebooks_dir.iterdir():
            if file.is_file() and file.name != 'README.md':
                title = file.stem.replace('_', ' ').title()

                # Determine format from extension
                ext = file.suffix.lower()
                file_type = ext[1:] if ext else 'unknown'

                project_id = project_manager.create_project(
                    title=title,
                    project_type='conversion',
                    metadata={
                        'title': title,
                        'migrated': True,
                        'original_file': file.name
                    }
                )

                # Add file to project
                relative_path = f"ebooks/{file.name}"
                project_manager.add_file_to_project(
                    project_id=project_id,
                    file_path=relative_path,
                    file_type=file_type
                )

                print(f"  ✓ Migrated: {file.name}")
                migrated_count += 1

    # Migrate covers
    print("\n🎨 Migrating Covers...")
    covers_dir = base_dir / 'output' / 'covers'
    if covers_dir.exists():
        for file in covers_dir.iterdir():
            if file.is_file() and file.name != 'README.md':
                # Extract title from filename
                title = file.stem.replace('_', ' ').title()

                # Determine cover type from filename
                cover_type = 'ebook'
                if 'paperback' in file.name.lower():
                    cover_type = 'paperback'
                elif 'hardback' in file.name.lower():
                    cover_type = 'hardback'

                project_id = project_manager.create_project(
                    title=f"{title} - Cover",
                    project_type='cover',
                    metadata={
                        'title': title,
                        'cover_type': cover_type,
                        'migrated': True,
                        'original_file': file.name
                    }
                )

                # Add file to project
                relative_path = f"covers/{file.name}"
                project_manager.add_file_to_project(
                    project_id=project_id,
                    file_path=relative_path,
                    file_type='cover_image'
                )

                print(f"  ✓ Migrated: {file.name}")
                migrated_count += 1

    # Migrate watermarked files
    print("\n💧 Migrating Watermarked Files...")
    watermarked_dir = base_dir / 'output' / 'watermarked'
    if watermarked_dir.exists():
        for file in watermarked_dir.iterdir():
            if file.is_file() and file.name != 'README.md':
                title = file.stem.replace('_', ' ').replace('watermarked', '').strip().title()

                project_id = project_manager.create_project(
                    title=f"Watermarked - {title}",
                    project_type='watermark',
                    metadata={
                        'original_file': title,
                        'migrated': True
                    }
                )

                # Add file to project
                relative_path = f"watermarked/{file.name}"
                project_manager.add_file_to_project(
                    project_id=project_id,
                    file_path=relative_path,
                    file_type='watermarked_document'
                )

                print(f"  ✓ Migrated: {file.name}")
                migrated_count += 1

    # Get updated stats
    print("\n" + "="*60)
    print("Migration Complete!")
    print("="*60)

    stats = project_manager.get_stats()
    print(f"\n📊 Updated Statistics:")
    print(f"  📚 Books Created: {stats['total_books']}")
    print(f"  🎨 Covers Designed: {stats['total_covers']}")
    print(f"  🔄 Conversions: {stats['total_conversions']}")
    print(f"  💧 Watermarks: {stats['total_watermarks']}")
    print(f"\n✅ Total files migrated: {migrated_count}")
    print(f"✅ Total projects in database: {len(project_manager.projects['projects'])}")
    print("\nRefresh your dashboard to see the updated statistics!")
    print()

if __name__ == '__main__':
    try:
        migrate_existing_files()
    except Exception as e:
        print(f"\n❌ Error during migration: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
