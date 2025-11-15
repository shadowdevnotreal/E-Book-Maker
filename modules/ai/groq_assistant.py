"""
Groq AI Assistant for E-Book Maker
Provides comprehensive AI-powered features for all aspects of e-book creation
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from groq import Groq


class GroqAssistant:
    """
    Comprehensive AI assistant powered by Groq API
    Handles cover generation, content creation, text enhancement, and metadata
    """

    # Available Groq models (as of 2025)
    # NOTE: llama-3.2-90b-vision-preview has been decommissioned as of early 2025
    AVAILABLE_MODELS = {
        'llama-3.3-70b-versatile': {
            'name': 'Llama 3.3 70B Versatile',
            'description': 'Most capable model - best for complex tasks',
            'category': 'general',
            'speed': 'medium',
            'quality': 'highest'
        },
        'llama-3.1-8b-instant': {
            'name': 'Llama 3.1 8B Instant',
            'description': 'Lightning fast - best for quick responses',
            'category': 'general',
            'speed': 'fastest',
            'quality': 'high'
        },
        'qwen-2.5-coder-32b': {
            'name': 'Qwen 2.5 Coder 32B',
            'description': 'Optimized for code and technical content',
            'category': 'coding',
            'speed': 'fast',
            'quality': 'high'
        },
        'deepseek-r1-distill-llama-70b-specdec': {
            'name': 'DeepSeek R1 Llama 70B',
            'description': 'Alternative powerful model',
            'category': 'general',
            'speed': 'medium',
            'quality': 'highest'
        },
        'mistral-saba-24b': {
            'name': 'Mistral Saba 24B',
            'description': 'Good balance of speed and quality',
            'category': 'general',
            'speed': 'fast',
            'quality': 'high'
        },
        'llama-3.2-3b-preview': {
            'name': 'Llama 3.2 3B Preview',
            'description': 'Ultra-fast, lightweight model',
            'category': 'general',
            'speed': 'ultra-fast',
            'quality': 'good'
        }
    }

    def __init__(self, config_path: str = "config/ai_config.json", streamlit_secrets=None, allow_secrets: bool = False):
        """
        Initialize Groq assistant

        Args:
            config_path: Path to AI configuration file
            streamlit_secrets: Streamlit secrets object (optional)
            allow_secrets: If True, allow loading from secrets.toml (LOCAL ONLY - disabled for cloud)
        """
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.client = None
        self.enabled = False
        self.api_key_source = None  # Track where the API key came from

        # Priority 1: Check Streamlit secrets ONLY if explicitly allowed (local development only)
        api_key = None
        if allow_secrets and streamlit_secrets is not None:
            try:
                api_key = streamlit_secrets.get("GROQ_API_KEY") or streamlit_secrets.get("groq_api_key")
                if api_key:
                    self.api_key_source = "secrets.toml (local)"
            except:
                pass

        # Priority 2: Fall back to config file
        if not api_key and self.config.get('groq_api_key'):
            api_key = self.config['groq_api_key']
            self.api_key_source = "config file"

        # Initialize if API key exists
        if api_key:
            self.set_api_key(api_key)

    def _load_config(self) -> Dict:
        """Load AI configuration from file"""
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                return json.load(f)
        return {
            'groq_api_key': '',
            'ai_enabled': False,
            'default_model': 'llama-3.3-70b-versatile',
            'temperature': 0.7,
            'max_tokens': 2048
        }

    def _save_config(self):
        """Save AI configuration to file"""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)

    def set_api_key(self, api_key: str) -> Tuple[bool, str]:
        """
        Set and validate Groq API key

        Args:
            api_key: Groq API key

        Returns:
            Tuple of (success, message)
        """
        try:
            # Test the API key
            test_client = Groq(api_key=api_key)

            # Make a simple test request
            response = test_client.chat.completions.create(
                model=self.config['default_model'],
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10
            )

            # If we got here, the key works
            self.client = test_client
            self.config['groq_api_key'] = api_key
            self.config['ai_enabled'] = True
            self.enabled = True
            self._save_config()

            return (True, "✓ API key validated successfully! AI features enabled.")

        except Exception as e:
            self.enabled = False
            self.config['ai_enabled'] = False
            return (False, f"✗ API key validation failed: {str(e)}")

    def is_enabled(self) -> bool:
        """Check if AI assistant is enabled"""
        return self.enabled and self.client is not None

    def get_api_key_source(self) -> Optional[str]:
        """
        Get the source of the API key

        Returns:
            Source string ("secrets.toml", "config file", or None)
        """
        return self.api_key_source

    def get_available_models(self) -> Dict:
        """
        Get all available Groq models with their details

        Returns:
            Dictionary of model IDs and their information
        """
        return self.AVAILABLE_MODELS

    def get_current_model(self) -> str:
        """
        Get currently selected model ID

        Returns:
            Model ID string
        """
        return self.config.get('default_model', 'llama-3.3-70b-versatile')

    def get_current_model_info(self) -> Dict:
        """
        Get detailed info about currently selected model

        Returns:
            Dictionary with model information
        """
        model_id = self.get_current_model()
        return self.AVAILABLE_MODELS.get(model_id, {
            'name': model_id,
            'description': 'Unknown model',
            'category': 'general',
            'speed': 'medium',
            'quality': 'high'
        })

    def set_model(self, model_id: str) -> Tuple[bool, str]:
        """
        Change the active model

        Args:
            model_id: Model ID to switch to

        Returns:
            Tuple of (success, message)
        """
        if model_id not in self.AVAILABLE_MODELS:
            return (False, f"✗ Unknown model: {model_id}")

        try:
            # Test the model if client is initialized
            if self.client:
                response = self.client.chat.completions.create(
                    model=model_id,
                    messages=[{"role": "user", "content": "Hello"}],
                    max_tokens=10
                )

            # If we got here, the model works
            self.config['default_model'] = model_id
            self._save_config()

            model_info = self.AVAILABLE_MODELS[model_id]
            return (True, f"✓ Switched to {model_info['name']}")

        except Exception as e:
            return (False, f"✗ Failed to switch model: {str(e)}")

    def _make_request(self, prompt: str, system_prompt: str = None, max_tokens: int = None, model_override: str = None) -> Optional[str]:
        """
        Make a request to Groq API

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt for context
            max_tokens: Maximum tokens for response
            model_override: Optional model ID to use instead of default

        Returns:
            AI response or None if error
        """
        if not self.is_enabled():
            return None

        try:
            messages = []

            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})

            messages.append({"role": "user", "content": prompt})

            # Use override model or default
            model_to_use = model_override if model_override else self.config['default_model']

            response = self.client.chat.completions.create(
                model=model_to_use,
                messages=messages,
                temperature=self.config['temperature'],
                max_tokens=max_tokens or self.config['max_tokens']
            )

            return response.choices[0].message.content

        except Exception as e:
            print(f"AI request error: {e}")
            return None

    # ==========================================
    # COVER GENERATION AI FEATURES
    # ==========================================

    def suggest_cover_title(self, book_topic: str, genre: str = "") -> Optional[str]:
        """
        Generate catchy book title suggestions

        Args:
            book_topic: Main topic or theme of the book
            genre: Book genre (optional)

        Returns:
            Suggested title
        """
        system_prompt = """You are an expert book title creator specializing in Amazon KDP bestsellers.
Create compelling, marketable titles that grab attention and clearly communicate the book's value."""

        genre_text = f" in the {genre} genre" if genre else ""
        prompt = f"""Generate a compelling book title for a book about: {book_topic}{genre_text}

Requirements:
- Catchy and memorable
- Clear value proposition
- SEO-friendly for Amazon KDP
- Between 3-8 words
- Professional and marketable

Return ONLY the title, nothing else."""

        return self._make_request(prompt, system_prompt, max_tokens=100)

    def suggest_cover_subtitle(self, title: str, book_topic: str) -> Optional[str]:
        """
        Generate compelling subtitle

        Args:
            title: Book title
            book_topic: Main topic

        Returns:
            Suggested subtitle
        """
        system_prompt = """You are an expert at creating book subtitles that clarify value and improve discoverability."""

        prompt = f"""Create a compelling subtitle for this book:

Title: {title}
Topic: {book_topic}

Requirements:
- Clarifies what the reader will learn/gain
- Complements the title
- SEO-friendly keywords
- Between 5-12 words
- Professional tone

Return ONLY the subtitle, nothing else."""

        return self._make_request(prompt, system_prompt, max_tokens=100)

    def suggest_color_scheme(self, genre: str, mood: str = "") -> Optional[Dict[str, str]]:
        """
        Suggest color scheme for book cover

        Args:
            genre: Book genre
            mood: Desired mood (optional)

        Returns:
            Dictionary with primary and secondary color hex codes
        """
        system_prompt = """You are an expert graphic designer specializing in book cover design.
Suggest colors that are proven to work well for book covers in specific genres."""

        mood_text = f" with a {mood} mood" if mood else ""
        prompt = f"""Suggest a professional color scheme for a {genre} book cover{mood_text}.

Requirements:
- Two colors (primary and secondary)
- Good contrast and readability
- Psychologically appropriate for genre
- Proven to work on Amazon KDP

Return your response in this EXACT format:
PRIMARY: #HEXCODE
SECONDARY: #HEXCODE

Example:
PRIMARY: #667eea
SECONDARY: #764ba2"""

        response = self._make_request(prompt, system_prompt, max_tokens=150)

        if response:
            # Parse the response
            try:
                lines = response.strip().split('\n')
                colors = {}
                for line in lines:
                    if 'PRIMARY:' in line.upper():
                        colors['primary'] = line.split('#')[1].strip()[:6]
                    elif 'SECONDARY:' in line.upper():
                        colors['secondary'] = line.split('#')[1].strip()[:6]

                if 'primary' in colors and 'secondary' in colors:
                    return {
                        'primary': f"#{colors['primary']}",
                        'secondary': f"#{colors['secondary']}"
                    }
            except:
                pass

        return None

    def suggest_cover_style(self, genre: str, target_audience: str = "") -> Optional[str]:
        """
        Suggest cover design style

        Args:
            genre: Book genre
            target_audience: Target reader demographic

        Returns:
            Style suggestion (gradient, solid, minimalist)
        """
        system_prompt = """You are a book cover design expert who knows what styles work best for different genres and audiences."""

        audience_text = f" targeting {target_audience}" if target_audience else ""
        prompt = f"""Suggest the best cover style for a {genre} book{audience_text}.

Choose from these options:
- gradient: Modern gradient backgrounds (good for tech, business, self-help)
- solid: Single solid color (good for minimalist, literary fiction)
- minimalist: Clean white background (good for professional, academic)

Return ONLY one word: gradient, solid, or minimalist"""

        response = self._make_request(prompt, system_prompt, max_tokens=50)

        if response:
            style = response.strip().lower()
            if style in ['gradient', 'solid', 'minimalist']:
                return style

        return None

    # ==========================================
    # CONTENT GENERATION AI FEATURES
    # ==========================================

    def generate_book_description(self, title: str, subtitle: str, topic: str,
                                  target_audience: str = "", key_points: List[str] = None) -> Optional[str]:
        """
        Generate Amazon KDP book description

        Args:
            title: Book title
            subtitle: Book subtitle
            topic: Main topic
            target_audience: Target readers
            key_points: Key takeaways (optional)

        Returns:
            Formatted book description ready for KDP
        """
        system_prompt = """You are an expert copywriter specializing in Amazon KDP book descriptions that convert browsers into buyers.
Use proven persuasion techniques and formatting that works on Amazon."""

        audience_text = f" for {target_audience}" if target_audience else ""
        points_text = ""
        if key_points:
            points_text = f"\n\nKey Points:\n" + "\n".join([f"- {point}" for point in key_points])

        prompt = f"""Create a compelling Amazon KDP book description for:

Title: {title}
Subtitle: {subtitle}
Topic: {topic}{audience_text}{points_text}

Requirements:
- Hook in first 2 sentences
- Clear benefits and transformations
- Bullet points for key features
- Call to action
- SEO-friendly keywords
- 150-250 words
- Use HTML formatting (<b>, <i>, <br>) for Amazon

Return the complete description ready to paste into KDP."""

        return self._make_request(prompt, system_prompt, max_tokens=1000)

    def generate_author_bio(self, name: str, expertise: str, achievements: str = "") -> Optional[str]:
        """
        Generate professional author biography

        Args:
            name: Author name
            expertise: Area of expertise
            achievements: Notable achievements (optional)

        Returns:
            Professional author bio
        """
        system_prompt = """You are an expert at writing compelling author biographies that build credibility and trust."""

        achievements_text = f"\n\nAchievements: {achievements}" if achievements else ""

        prompt = f"""Write a professional author biography for:

Name: {name}
Expertise: {expertise}{achievements_text}

Requirements:
- Professional tone
- Third person
- Establishes credibility
- 50-100 words
- Suitable for Amazon KDP

Return ONLY the bio, nothing else."""

        return self._make_request(prompt, system_prompt, max_tokens=300)

    def generate_chapter_outline(self, book_topic: str, target_length: int = 10) -> Optional[List[str]]:
        """
        Generate chapter outline for a book

        Args:
            book_topic: Main topic of the book
            target_length: Number of chapters (default 10)

        Returns:
            List of chapter titles
        """
        system_prompt = """You are an expert book structure consultant who creates logical, comprehensive chapter outlines."""

        prompt = f"""Create a {target_length}-chapter outline for a book about: {book_topic}

Requirements:
- Logical progression
- Comprehensive coverage
- Clear chapter titles
- Suitable for self-help/non-fiction
- Each chapter builds on the previous

Return one chapter title per line, numbered 1-{target_length}."""

        response = self._make_request(prompt, system_prompt, max_tokens=500)

        if response:
            # Parse chapter titles
            chapters = []
            for line in response.strip().split('\n'):
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith('Chapter')):
                    # Remove numbering
                    title = line.split('.', 1)[-1].strip() if '.' in line else line
                    title = title.replace('Chapter ', '').strip()
                    if title:
                        chapters.append(title)
            return chapters if chapters else None

        return None

    def generate_chapter_content(self, chapter_title: str, book_topic: str,
                                word_count: int = 1500) -> Optional[str]:
        """
        Generate content for a specific chapter

        Args:
            chapter_title: Title of the chapter
            book_topic: Overall book topic
            word_count: Target word count

        Returns:
            Generated chapter content in markdown format
        """
        system_prompt = """You are an expert non-fiction author who writes clear, engaging, and valuable content."""

        prompt = f"""Write the content for this chapter:

Chapter: {chapter_title}
Book Topic: {book_topic}
Target Length: {word_count} words

Requirements:
- Clear and engaging writing
- Practical examples
- Actionable advice
- Proper structure (intro, body, conclusion)
- Markdown formatting
- Professional tone

Write the complete chapter content in markdown format."""

        return self._make_request(prompt, system_prompt, max_tokens=int(word_count * 2))

    # ==========================================
    # TEXT ENHANCEMENT AI FEATURES
    # ==========================================

    def proofread_text(self, text: str) -> Optional[str]:
        """
        Proofread and correct grammar/spelling

        Args:
            text: Text to proofread

        Returns:
            Corrected text
        """
        system_prompt = """You are an expert editor and proofreader. Fix grammar, spelling, and punctuation errors while preserving the author's voice and style."""

        prompt = f"""Proofread and correct this text:

{text}

Requirements:
- Fix grammar and spelling errors
- Improve clarity and readability
- Preserve author's voice
- Keep the same general length

Return ONLY the corrected text, nothing else."""

        return self._make_request(prompt, system_prompt, max_tokens=len(text) * 2)

    def improve_readability(self, text: str, target_grade_level: int = 8) -> Optional[str]:
        """
        Improve text readability

        Args:
            text: Text to improve
            target_grade_level: Target reading grade level (default 8)

        Returns:
            Improved text
        """
        system_prompt = """You are an expert in making complex text more readable and accessible."""

        prompt = f"""Rewrite this text to improve readability for a grade {target_grade_level} reading level:

{text}

Requirements:
- Simpler vocabulary
- Shorter sentences
- Clearer structure
- Preserve key information
- Maintain professional tone

Return ONLY the rewritten text, nothing else."""

        return self._make_request(prompt, system_prompt, max_tokens=len(text) * 2)

    def expand_text(self, text: str, target_length: int = None) -> Optional[str]:
        """
        Expand text with more detail and examples

        Args:
            text: Text to expand
            target_length: Target word count (optional)

        Returns:
            Expanded text
        """
        system_prompt = """You are an expert writer who can expand content with relevant details, examples, and explanations."""

        length_text = f" to approximately {target_length} words" if target_length else ""

        prompt = f"""Expand this text{length_text} by adding:
- More detailed explanations
- Relevant examples
- Additional context
- Supporting evidence

Original text:
{text}

Return ONLY the expanded text, nothing else."""

        max_tok = target_length * 2 if target_length else len(text) * 4
        return self._make_request(prompt, system_prompt, max_tokens=max_tok)

    def summarize_text(self, text: str, target_length: int = 100) -> Optional[str]:
        """
        Summarize text

        Args:
            text: Text to summarize
            target_length: Target word count for summary

        Returns:
            Summarized text
        """
        system_prompt = """You are an expert at creating clear, concise summaries that capture key points."""

        prompt = f"""Summarize this text in approximately {target_length} words:

{text}

Focus on the most important points and key takeaways.

Return ONLY the summary, nothing else."""

        return self._make_request(prompt, system_prompt, max_tokens=target_length * 2)

    # ==========================================
    # METADATA & MARKETING AI FEATURES
    # ==========================================

    def generate_kdp_keywords(self, title: str, topic: str, genre: str = "") -> Optional[List[str]]:
        """
        Generate Amazon KDP keywords

        Args:
            title: Book title
            topic: Book topic
            genre: Book genre (optional)

        Returns:
            List of 7 keyword phrases for KDP
        """
        system_prompt = """You are an Amazon KDP expert who knows how to create high-traffic, low-competition keywords that help books rank."""

        genre_text = f" in the {genre} genre" if genre else ""

        prompt = f"""Generate 7 keyword phrases for Amazon KDP for this book:

Title: {title}
Topic: {topic}{genre_text}

Requirements:
- High search volume on Amazon
- Relevant to the book
- Mix of short and long-tail keywords
- Avoid branded terms
- Follow KDP guidelines
- Each keyword phrase 2-5 words

Return EXACTLY 7 keyword phrases, one per line, no numbering."""

        response = self._make_request(prompt, system_prompt, max_tokens=300)

        if response:
            keywords = [line.strip() for line in response.strip().split('\n') if line.strip()]
            return keywords[:7]  # Ensure exactly 7

        return None

    def suggest_kdp_categories(self, title: str, topic: str, genre: str = "") -> Optional[List[str]]:
        """
        Suggest Amazon KDP categories

        Args:
            title: Book title
            topic: Book topic
            genre: Book genre (optional)

        Returns:
            List of suggested KDP categories
        """
        system_prompt = """You are an Amazon KDP category expert who knows the best categories for maximum visibility."""

        genre_text = f" ({genre})" if genre else ""

        prompt = f"""Suggest the best 3 Amazon KDP categories for this book:

Title: {title}
Topic: {topic}{genre_text}

Requirements:
- Categories that exist on Amazon KDP
- Good for discoverability
- Not overly competitive
- Relevant to the content

Return 3 category paths, one per line, using > for hierarchy:
Example: Books > Self-Help > Personal Transformation"""

        response = self._make_request(prompt, system_prompt, max_tokens=300)

        if response:
            categories = [line.strip() for line in response.strip().split('\n') if line.strip() and '>' in line]
            return categories[:3]

        return None

    def generate_marketing_copy(self, title: str, description: str, call_to_action: str = "Get your copy today!") -> Optional[str]:
        """
        Generate marketing copy for social media/ads

        Args:
            title: Book title
            description: Short book description
            call_to_action: CTA text

        Returns:
            Marketing copy
        """
        system_prompt = """You are a marketing copywriter expert at creating compelling promotional content for books."""

        prompt = f"""Create engaging marketing copy for this book:

Title: {title}
Description: {description}
CTA: {call_to_action}

Requirements:
- Attention-grabbing hook
- Emotional appeal
- Clear benefits
- Urgency
- 50-100 words
- Include CTA
- Suitable for social media/ads

Return ONLY the marketing copy, nothing else."""

        return self._make_request(prompt, system_prompt, max_tokens=300)

    def generate_back_cover_copy(self, title: str, subtitle: str, description: str) -> Optional[str]:
        """
        Generate back cover copy for print books

        Args:
            title: Book title
            subtitle: Book subtitle
            description: Book description

        Returns:
            Back cover copy
        """
        system_prompt = """You are an expert at writing compelling back cover copy that sells books in physical bookstores."""

        prompt = f"""Write back cover copy for this print book:

Title: {title}
Subtitle: {subtitle}
Description: {description}

Requirements:
- Hook to grab attention
- Key benefits and outcomes
- Social proof elements (if applicable)
- 100-150 words
- Persuasive but professional
- Suitable for paperback/hardback

Return ONLY the back cover text, nothing else."""

        return self._make_request(prompt, system_prompt, max_tokens=400)
