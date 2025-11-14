#!/usr/bin/env python3
"""
Comprehensive AI Features Test Script
Tests all AI features and saves outputs to desktop (not repo)
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'modules'))

from ai.groq_assistant import GroqAssistant

# Output to desktop (NOT in repo)
OUTPUT_DIR = Path.home() / "Desktop" / "E-Book-Maker-Tests" / f"ai_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Test results
results = {
    "timestamp": datetime.now().isoformat(),
    "tests": []
}


def log_test(test_name, success, output=None, error=None):
    """Log test result"""
    result = {
        "test": test_name,
        "success": success,
        "output": output,
        "error": error
    }
    results["tests"].append(result)

    status = "✓" if success else "✗"
    print(f"{status} {test_name}")
    if output and success:
        print(f"  → {output[:100]}..." if len(str(output)) > 100 else f"  → {output}")
    if error:
        print(f"  ✗ {error}")


def main():
    """Run all AI feature tests"""
    print("=" * 80)
    print("E-BOOK MAKER - COMPREHENSIVE AI FEATURES TEST")
    print("=" * 80)
    print(f"Output Directory: {OUTPUT_DIR}")
    print("=" * 80)

    # Initialize AI Assistant
    ai = GroqAssistant()

    # Test 1: API Key Configuration
    print("\n📋 TEST CATEGORY: API Key Management")
    print("-" * 80)

    api_key = ""
    success, message = ai.set_api_key(api_key)
    log_test("API Key Validation", success, message, None if success else message)

    if not ai.is_enabled():
        print("\n✗ AI not enabled. Cannot continue tests.")
        return

    # Test 2: Cover Design AI
    print("\n🎨 TEST CATEGORY: Cover Design AI")
    print("-" * 80)

    title = ai.suggest_cover_title("Python programming for beginners", "Education")
    log_test("Title Suggestion", bool(title), title)

    if title:
        subtitle = ai.suggest_cover_subtitle(title, "Python programming")
        log_test("Subtitle Suggestion", bool(subtitle), subtitle)

    colors = ai.suggest_color_scheme("Technology", "modern")
    log_test("Color Scheme Suggestion", bool(colors), colors)

    style = ai.suggest_cover_style("Self-Help", "professionals")
    log_test("Style Suggestion", bool(style), style)

    # Test 3: Content Generation AI
    print("\n📝 TEST CATEGORY: Content Generation AI")
    print("-" * 80)

    description = ai.generate_book_description(
        "Python Mastery",
        "From Beginner to Expert",
        "Python programming",
        "aspiring developers",
        ["Hands-on exercises", "Real-world projects", "Best practices"]
    )
    log_test("Book Description Generation", bool(description), description[:200] if description else None)

    if description:
        # Save description to file
        desc_file = OUTPUT_DIR / "book_description.html"
        desc_file.write_text(description)
        print(f"  💾 Saved to: {desc_file}")

    bio = ai.generate_author_bio(
        "John Smith",
        "Software Engineering and Python Development",
        "10+ years experience, published author"
    )
    log_test("Author Bio Generation", bool(bio), bio)

    if bio:
        bio_file = OUTPUT_DIR / "author_bio.txt"
        bio_file.write_text(bio)
        print(f"  💾 Saved to: {bio_file}")

    outline = ai.generate_chapter_outline("Python Programming Fundamentals", 8)
    log_test("Chapter Outline Generation", bool(outline), f"{len(outline)} chapters" if outline else None)

    if outline:
        outline_file = OUTPUT_DIR / "chapter_outline.txt"
        outline_file.write_text("\n".join([f"{i+1}. {ch}" for i, ch in enumerate(outline)]))
        print(f"  💾 Saved to: {outline_file}")

    # Test chapter content generation (smaller for speed)
    if outline and len(outline) > 0:
        chapter_content = ai.generate_chapter_content(
            outline[0],
            "Python Programming",
            word_count=500
        )
        log_test("Chapter Content Generation", bool(chapter_content), f"{len(chapter_content)} chars" if chapter_content else None)

        if chapter_content:
            chapter_file = OUTPUT_DIR / "sample_chapter.md"
            chapter_file.write_text(chapter_content)
            print(f"  💾 Saved to: {chapter_file}")

    # Test 4: Text Enhancement AI
    print("\n✨ TEST CATEGORY: Text Enhancement AI")
    print("-" * 80)

    sample_text = "This is a sample text with some gramatical errors and can be improve for better readability."

    proofread = ai.proofread_text(sample_text)
    log_test("Proofreading", bool(proofread), proofread)

    improved = ai.improve_readability(sample_text, target_grade_level=6)
    log_test("Readability Improvement", bool(improved), improved)

    expanded = ai.expand_text("Python is a programming language.", target_length=150)
    log_test("Text Expansion", bool(expanded), expanded)

    long_text = "Python is a high-level, interpreted programming language with dynamic semantics. " \
                "It's known for its simplicity and readability, making it an excellent choice for beginners. " \
                "Python supports multiple programming paradigms including procedural, object-oriented, and functional programming."
    summary = ai.summarize_text(long_text, target_length=30)
    log_test("Text Summarization", bool(summary), summary)

    # Test 5: Metadata & Marketing AI
    print("\n📊 TEST CATEGORY: Metadata & Marketing AI")
    print("-" * 80)

    keywords = ai.generate_kdp_keywords("Python Mastery", "Python programming", "Education")
    log_test("KDP Keywords Generation", bool(keywords) and len(keywords) == 7, keywords)

    if keywords:
        keywords_file = OUTPUT_DIR / "kdp_keywords.txt"
        keywords_file.write_text("\n".join(keywords))
        print(f"  💾 Saved to: {keywords_file}")

    categories = ai.suggest_kdp_categories("Python Mastery", "Python programming", "Technology")
    log_test("KDP Categories Suggestion", bool(categories), categories)

    if categories:
        categories_file = OUTPUT_DIR / "kdp_categories.txt"
        categories_file.write_text("\n".join(categories))
        print(f"  💾 Saved to: {categories_file}")

    marketing = ai.generate_marketing_copy(
        "Python Mastery",
        "Learn Python programming from scratch to advanced",
        "Start your Python journey today!"
    )
    log_test("Marketing Copy Generation", bool(marketing), marketing)

    if marketing:
        marketing_file = OUTPUT_DIR / "marketing_copy.txt"
        marketing_file.write_text(marketing)
        print(f"  💾 Saved to: {marketing_file}")

    back_cover = ai.generate_back_cover_copy(
        "Python Mastery",
        "From Beginner to Expert",
        "A comprehensive guide to Python programming"
    )
    log_test("Back Cover Copy Generation", bool(back_cover), back_cover)

    if back_cover:
        back_cover_file = OUTPUT_DIR / "back_cover_copy.txt"
        back_cover_file.write_text(back_cover)
        print(f"  💾 Saved to: {back_cover_file}")

    # Generate test report
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)

    passed = sum(1 for t in results["tests"] if t["success"])
    total = len(results["tests"])
    print(f"✓ Passed: {passed}/{total} ({passed/total*100:.1f}%)")
    print(f"✗ Failed: {total - passed}/{total}")

    # Save results
    results_file = OUTPUT_DIR / "test_results.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n💾 Full results saved to: {results_file}")

    print("\n" + "=" * 80)
    print(f"📁 All test outputs saved to: {OUTPUT_DIR}")
    print("=" * 80)

    if passed == total:
        print("\n🎉 ALL TESTS PASSED! AI features are working perfectly!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Check the output for details.")

    return passed == total


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
