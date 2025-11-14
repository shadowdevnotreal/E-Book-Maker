"""
Page Numbering Configuration Module
Handles page numbering for PDF, DOCX, and EPUB formats
"""

from typing import Dict, List, Optional
from pathlib import Path
import json


class PageNumberingConfig:
    """Configuration for page numbering across different formats"""

    # Position mappings for LaTeX fancyhdr
    LATEX_POSITIONS = {
        'header-left': 'L',
        'header-center': 'C',
        'header-right': 'R',
        'footer-left': 'L',
        'footer-center': 'C',
        'footer-right': 'R'
    }

    # Numbering style mappings
    NUMBERING_STYLES = {
        'arabic': 'arabic',      # 1, 2, 3, ...
        'roman': 'roman',        # i, ii, iii, ...
        'Roman': 'Roman',        # I, II, III, ...
        'alph': 'alph',          # a, b, c, ...
        'Alph': 'Alph'           # A, B, C, ...
    }

    def __init__(self, config: Optional[Dict] = None):
        """Initialize with default or custom config"""
        self.config = self._load_default_config()
        if config:
            self._merge_config(self.config, config)

    def _load_default_config(self) -> Dict:
        """Load default page numbering configuration"""
        return {
            'enabled': True,
            'pdf': {
                'enabled': True,
                'position': 'footer-center',
                'style': 'arabic',
                'front_matter': {
                    'enabled': False,
                    'style': 'roman'
                },
                'skip_pages': ['title'],
                'custom_headers': {'enabled': False},
                'custom_footers': {'enabled': False}
            },
            'docx': {
                'enabled': True,
                'position': 'footer-center',
                'style': 'arabic',
                'reference_doc': None
            },
            'epub': {
                'enabled': False,
                'page_list': False,
                'source_isbn': ''
            }
        }

    def _merge_config(self, default: Dict, user: Dict):
        """Recursively merge user config into default config"""
        for key, value in user.items():
            if key in default and isinstance(default[key], dict) and isinstance(value, dict):
                self._merge_config(default[key], value)
            else:
                default[key] = value

    def generate_latex_header(self) -> str:
        """Generate LaTeX header-includes for page numbering"""
        if not self.config['enabled'] or not self.config['pdf']['enabled']:
            return ""

        pdf_config = self.config['pdf']
        lines = [
            "\\usepackage{fancyhdr}",
            "\\pagestyle{fancy}"
        ]

        # Clear default headers/footers
        lines.append("\\fancyhf{}")

        # Set custom headers if enabled
        if pdf_config['custom_headers']['enabled']:
            for pos in ['left', 'center', 'right']:
                content = pdf_config['custom_headers'].get(pos, '')
                if content:
                    latex_pos = self.LATEX_POSITIONS[f'header-{pos}']
                    lines.append(f"\\fancyhead[{latex_pos}]{{{content}}}")

        # Set custom footers if enabled
        if pdf_config['custom_footers']['enabled']:
            for pos in ['left', 'center', 'right']:
                content = pdf_config['custom_footers'].get(pos, '')
                if content:
                    latex_pos = self.LATEX_POSITIONS[f'footer-{pos}']
                    lines.append(f"\\fancyfoot[{latex_pos}]{{{content}}}")
        else:
            # Use simple position
            position = pdf_config['position']
            if position in self.LATEX_POSITIONS:
                latex_pos = self.LATEX_POSITIONS[position]
                lines.append(f"\\fancyfoot[{latex_pos}]{{\\thepage}}")

        # Add rule widths
        lines.append("\\renewcommand{\\headrulewidth}{0.4pt}")
        lines.append("\\renewcommand{\\footrulewidth}{0pt}")

        return "\n".join(lines)

    def generate_frontmatter_commands(self) -> str:
        """Generate LaTeX commands for front matter"""
        if not self.config['enabled'] or not self.config['pdf']['enabled']:
            return ""

        if not self.config['pdf']['front_matter']['enabled']:
            return ""

        style = self.config['pdf']['front_matter']['style']
        return f"\\pagenumbering{{{style}}}"

    def generate_mainmatter_commands(self) -> str:
        """Generate LaTeX commands for main matter"""
        if not self.config['enabled'] or not self.config['pdf']['enabled']:
            return ""

        style = self.config['pdf']['style']
        return f"\\pagenumbering{{{style}}}"

    def get_reference_doc_path(self) -> Optional[Path]:
        """Get path to DOCX reference document"""
        if not self.config['enabled'] or not self.config['docx']['enabled']:
            return None

        ref_doc = self.config['docx'].get('reference_doc')
        if ref_doc:
            path = Path(ref_doc)
            if path.exists():
                return path

        return None

    def is_epub_pagination_enabled(self) -> bool:
        """Check if EPUB pagination is enabled"""
        return (self.config['enabled'] and
                self.config['epub']['enabled'] and
                self.config['epub']['page_list'])


if __name__ == '__main__':
    # Test the page numbering configuration
    config = PageNumberingConfig()
    print("Default LaTeX Header:")
    print(config.generate_latex_header())
    print()

    # Test with custom configuration
    custom_config = PageNumberingConfig({
        'pdf': {
            'position': 'footer-right',
            'style': 'roman',
            'front_matter': {
                'enabled': True,
                'style': 'Roman'
            }
        }
    })
    print("Custom LaTeX Header:")
    print(custom_config.generate_latex_header())
