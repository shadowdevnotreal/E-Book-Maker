"""
File handling utilities for E-Book Maker
"""

import os
import shutil
from pathlib import Path
from typing import List, Optional


class FileHandler:
    """Utility class for file operations"""

    @staticmethod
    def ensure_directory(path: Path) -> Path:
        """Ensure directory exists, create if not"""
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        return path

    @staticmethod
    def get_file_size(path: Path) -> int:
        """Get file size in bytes"""
        return Path(path).stat().st_size

    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """Format file size in human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"

    @staticmethod
    def list_files(directory: Path, extensions: Optional[List[str]] = None) -> List[Path]:
        """
        List files in directory with optional extension filtering

        Args:
            directory: Directory to search
            extensions: List of file extensions to filter (e.g., ['.md', '.txt'])

        Returns:
            List of file paths
        """
        directory = Path(directory)
        if not directory.exists():
            return []

        files = []
        for file_path in directory.iterdir():
            if file_path.is_file():
                if extensions is None or file_path.suffix.lower() in extensions:
                    files.append(file_path)

        return sorted(files)

    @staticmethod
    def copy_file(source: Path, destination: Path) -> Path:
        """Copy file from source to destination"""
        source = Path(source)
        destination = Path(destination)

        # Ensure destination directory exists
        destination.parent.mkdir(parents=True, exist_ok=True)

        shutil.copy2(source, destination)
        return destination

    @staticmethod
    def move_file(source: Path, destination: Path) -> Path:
        """Move file from source to destination"""
        source = Path(source)
        destination = Path(destination)

        # Ensure destination directory exists
        destination.parent.mkdir(parents=True, exist_ok=True)

        shutil.move(str(source), str(destination))
        return destination

    @staticmethod
    def delete_file(path: Path) -> bool:
        """Delete file if it exists"""
        path = Path(path)
        if path.exists() and path.is_file():
            path.unlink()
            return True
        return False

    @staticmethod
    def safe_filename(filename: str) -> str:
        """
        Convert filename to safe version (remove special characters)

        Args:
            filename: Original filename

        Returns:
            Safe filename
        """
        import re

        # Remove or replace unsafe characters
        safe_name = re.sub(r'[<>:"/\\|?*]', '', filename)

        # Replace spaces with underscores
        safe_name = safe_name.replace(' ', '_')

        # Remove multiple underscores
        safe_name = re.sub(r'_+', '_', safe_name)

        # Ensure not empty
        if not safe_name:
            safe_name = 'unnamed'

        return safe_name

    @staticmethod
    def get_unique_filename(directory: Path, filename: str) -> Path:
        """
        Get unique filename in directory by appending number if file exists

        Args:
            directory: Directory path
            filename: Desired filename

        Returns:
            Unique file path
        """
        directory = Path(directory)
        base_path = directory / filename

        if not base_path.exists():
            return base_path

        # Split filename and extension
        stem = Path(filename).stem
        suffix = Path(filename).suffix

        counter = 1
        while True:
            new_filename = f"{stem}_{counter}{suffix}"
            new_path = directory / new_filename
            if not new_path.exists():
                return new_path
            counter += 1


if __name__ == '__main__':
    # Test file handler
    handler = FileHandler()
    print(f"1 KB = {handler.format_file_size(1024)}")
    print(f"1 MB = {handler.format_file_size(1024 * 1024)}")
    print(f"Safe filename: {handler.safe_filename('My Book: A Great Story!')}")
