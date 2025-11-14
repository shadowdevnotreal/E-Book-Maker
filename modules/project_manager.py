"""
Project Manager - Track and manage e-book projects
Stores project history, metadata, and file references
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import uuid


class ProjectManager:
    def __init__(self, storage_path: str = None):
        """Initialize project manager with storage location"""
        if storage_path is None:
            base_dir = Path(__file__).parent.parent
            storage_path = base_dir / 'output' / 'projects'

        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self.projects_file = self.storage_path / 'projects.json'
        self.projects = self._load_projects()

    def _load_projects(self) -> Dict:
        """Load projects from JSON file"""
        if self.projects_file.exists():
            try:
                with open(self.projects_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading projects: {e}")
                return {'projects': [], 'stats': self._init_stats()}
        return {'projects': [], 'stats': self._init_stats()}

    def _save_projects(self):
        """Save projects to JSON file"""
        try:
            with open(self.projects_file, 'w', encoding='utf-8') as f:
                json.dump(self.projects, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving projects: {e}")

    def _init_stats(self) -> Dict:
        """Initialize stats structure"""
        return {
            'total_books': 0,
            'total_covers': 0,
            'total_conversions': 0,
            'total_watermarks': 0,
            'last_activity': None
        }

    def create_project(self, title: str, project_type: str, **kwargs) -> str:
        """
        Create a new project

        Args:
            title: Project title
            project_type: 'ebook', 'cover', 'watermark', 'conversion'
            **kwargs: Additional project metadata

        Returns:
            project_id: Unique project ID
        """
        project_id = str(uuid.uuid4())

        project = {
            'id': project_id,
            'title': title,
            'type': project_type,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'status': 'draft',
            'files': [],
            'metadata': kwargs.get('metadata', {}),
            'thumbnail': kwargs.get('thumbnail'),
            'tags': kwargs.get('tags', [])
        }

        self.projects['projects'].insert(0, project)  # Add to beginning

        # Update stats
        self._update_stats(project_type)

        self._save_projects()
        return project_id

    def update_project(self, project_id: str, **updates):
        """Update project with new information"""
        for project in self.projects['projects']:
            if project['id'] == project_id:
                project.update(updates)
                project['updated_at'] = datetime.now().isoformat()
                self._save_projects()
                return True
        return False

    def add_file_to_project(self, project_id: str, file_path: str, file_type: str):
        """Add a file reference to a project"""
        for project in self.projects['projects']:
            if project['id'] == project_id:
                project['files'].append({
                    'path': file_path,
                    'type': file_type,
                    'added_at': datetime.now().isoformat()
                })
                project['updated_at'] = datetime.now().isoformat()
                self._save_projects()
                return True
        return False

    def get_project(self, project_id: str) -> Optional[Dict]:
        """Get a specific project by ID"""
        for project in self.projects['projects']:
            if project['id'] == project_id:
                return project
        return None

    def get_recent_projects(self, limit: int = 10, project_type: str = None) -> List[Dict]:
        """
        Get recent projects

        Args:
            limit: Maximum number of projects to return
            project_type: Filter by type ('ebook', 'cover', etc.)
        """
        projects = self.projects['projects']

        if project_type:
            projects = [p for p in projects if p['type'] == project_type]

        return projects[:limit]

    def search_projects(self, query: str) -> List[Dict]:
        """Search projects by title or tags"""
        query = query.lower()
        results = []

        for project in self.projects['projects']:
            if (query in project['title'].lower() or
                any(query in tag.lower() for tag in project.get('tags', []))):
                results.append(project)

        return results

    def delete_project(self, project_id: str) -> bool:
        """Delete a project"""
        initial_len = len(self.projects['projects'])
        self.projects['projects'] = [
            p for p in self.projects['projects']
            if p['id'] != project_id
        ]

        if len(self.projects['projects']) < initial_len:
            self._save_projects()
            return True
        return False

    def _should_ignore_file(self, filename: str) -> bool:
        """Check if file should be ignored in stats/operations"""
        # Ignore special files
        if filename in ['.gitkeep', 'README.md']:
            return True
        # Ignore files starting with underscore or test-
        if filename.startswith('_') or filename.startswith('test-'):
            return True
        return False

    def get_stats(self) -> Dict:
        """Get project statistics - calculated from ACTUAL files in output directories

        Location determines category, not file extension:
        - /output/ebooks/ = Books
        - /output/covers/ = Covers
        - /output/watermarked/ = Watermarks
        """
        base_dir = Path(__file__).parent.parent / 'output'

        stats = {
            'total_books': 0,
            'total_covers': 0,
            'total_conversions': 0,
            'total_watermarks': 0,
            'last_activity': None
        }

        # Count books - ANY file in ebooks/ folder (except ignored files)
        ebooks_dir = base_dir / 'ebooks'
        if ebooks_dir.exists():
            for file in ebooks_dir.iterdir():
                if file.is_file() and not self._should_ignore_file(file.name):
                    stats['total_books'] += 1

        # Count covers - ANY file in covers/ folder (except ignored files)
        covers_dir = base_dir / 'covers'
        if covers_dir.exists():
            for file in covers_dir.iterdir():
                if file.is_file() and not self._should_ignore_file(file.name):
                    stats['total_covers'] += 1

        # Count conversions (same as ebooks for now)
        stats['total_conversions'] = stats['total_books']

        # Count watermarks - ANY file in watermarked/ folder (except ignored files)
        watermarks_dir = base_dir / 'watermarked'
        if watermarks_dir.exists():
            for file in watermarks_dir.iterdir():
                if file.is_file() and not self._should_ignore_file(file.name):
                    stats['total_watermarks'] += 1

        # Get last activity from most recent project
        projects_list = self.projects.get('projects', [])
        if projects_list:
            stats['last_activity'] = projects_list[0].get('created_at')

        # Update stored stats for consistency
        self.projects['stats'] = stats

        return stats

    def _update_stats(self, project_type: str):
        """Update statistics when new project is created"""
        stats = self.projects['stats']
        stats['last_activity'] = datetime.now().isoformat()

        if project_type == 'ebook':
            stats['total_books'] = stats.get('total_books', 0) + 1
        elif project_type == 'cover':
            stats['total_covers'] = stats.get('total_covers', 0) + 1
        elif project_type == 'conversion':
            stats['total_conversions'] = stats.get('total_conversions', 0) + 1
        elif project_type == 'watermark':
            stats['total_watermarks'] = stats.get('total_watermarks', 0) + 1

    def export_project(self, project_id: str, export_path: str) -> bool:
        """Export a project to a specific location"""
        project = self.get_project(project_id)
        if not project:
            return False

        try:
            export_file = Path(export_path) / f"{project['title']}_project.json"
            with open(export_file, 'w', encoding='utf-8') as f:
                json.dump(project, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error exporting project: {e}")
            return False

    def clear_project_history(self) -> bool:
        """Clear all project history but keep output files"""
        try:
            self.projects = {'projects': [], 'stats': self._init_stats()}
            self._save_projects()
            return True
        except Exception as e:
            print(f"Error clearing project history: {e}")
            return False

    def clear_output_files(self, file_type: str = None) -> Dict:
        """
        Clear output files from directories

        Args:
            file_type: 'ebooks', 'covers', 'watermarked', or None for all

        Returns:
            Dict with counts of deleted files
        """
        import shutil

        base_dir = Path(__file__).parent.parent / 'output'
        results = {'deleted': 0, 'errors': 0}

        directories = {
            'ebooks': base_dir / 'ebooks',
            'covers': base_dir / 'covers',
            'watermarked': base_dir / 'watermarked'
        }

        # Determine which directories to clear
        if file_type and file_type in directories:
            dirs_to_clear = {file_type: directories[file_type]}
        else:
            dirs_to_clear = directories

        for dir_name, dir_path in dirs_to_clear.items():
            if dir_path.exists():
                for file in dir_path.iterdir():
                    if file.is_file() and not self._should_ignore_file(file.name):
                        try:
                            file.unlink()
                            results['deleted'] += 1
                        except Exception as e:
                            print(f"Error deleting {file}: {e}")
                            results['errors'] += 1

        return results

    def reset_all(self) -> Dict:
        """
        Reset everything - clear project history AND delete all output files

        Returns:
            Dict with results of both operations
        """
        results = {
            'projects_cleared': False,
            'files_deleted': 0,
            'errors': 0
        }

        # Clear project history
        results['projects_cleared'] = self.clear_project_history()

        # Clear all output files
        file_results = self.clear_output_files()
        results['files_deleted'] = file_results['deleted']
        results['errors'] = file_results['errors']

        return results
