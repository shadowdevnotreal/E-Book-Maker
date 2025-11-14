#!/usr/bin/env python3
"""Test PDF cover generation to diagnose issues"""

from pathlib import Path
import sys

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent / 'modules'))

from covers.cover_generator import CoverGenerator

def test_paperback_cover():
    """Test creating a paperback cover (PDF output)"""
    print("=" * 60)
    print("Testing Paperback Cover Generation (PDF)")
    print("=" * 60)

    generator = CoverGenerator()
    output_dir = Path('output/test_covers')
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        cover_path = generator.create_cover(
            cover_type='paperback',
            title='Test Book',
            subtitle='A Test Subtitle',
            author='Test Author',
            style='gradient',
            colors={'primary': '#667eea', 'secondary': '#764ba2'},
            output_dir=output_dir
        )

        print(f"\n✅ SUCCESS! Cover created at: {cover_path}")
        print(f"File exists: {cover_path.exists()}")
        if cover_path.exists():
            print(f"File size: {cover_path.stat().st_size} bytes")
            print(f"File extension: {cover_path.suffix}")

        return True

    except Exception as e:
        print(f"\n❌ FAILED! Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_hardback_cover():
    """Test creating a hardback cover (PDF output)"""
    print("\n" + "=" * 60)
    print("Testing Hardback Cover Generation (PDF)")
    print("=" * 60)

    generator = CoverGenerator()
    output_dir = Path('output/test_covers')
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        cover_path = generator.create_cover(
            cover_type='hardback',
            title='Test Book',
            subtitle='A Test Subtitle',
            author='Test Author',
            style='solid',
            colors={'primary': '#ff6b6b', 'secondary': '#4ecdc4'},
            output_dir=output_dir
        )

        print(f"\n✅ SUCCESS! Cover created at: {cover_path}")
        print(f"File exists: {cover_path.exists()}")
        if cover_path.exists():
            print(f"File size: {cover_path.stat().st_size} bytes")
            print(f"File extension: {cover_path.suffix}")

        return True

    except Exception as e:
        print(f"\n❌ FAILED! Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ebook_cover():
    """Test creating an ebook cover (JPEG output) for comparison"""
    print("\n" + "=" * 60)
    print("Testing E-book Cover Generation (JPEG)")
    print("=" * 60)

    generator = CoverGenerator()
    output_dir = Path('output/test_covers')
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        cover_path = generator.create_cover(
            cover_type='ebook',
            title='Test Book',
            subtitle='A Test Subtitle',
            author='Test Author',
            style='gradient',
            colors={'primary': '#667eea', 'secondary': '#764ba2'},
            output_dir=output_dir
        )

        print(f"\n✅ SUCCESS! Cover created at: {cover_path}")
        print(f"File exists: {cover_path.exists()}")
        if cover_path.exists():
            print(f"File size: {cover_path.stat().st_size} bytes")
            print(f"File extension: {cover_path.suffix}")

        return True

    except Exception as e:
        print(f"\n❌ FAILED! Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    results = {
        'ebook': test_ebook_cover(),
        'paperback': test_paperback_cover(),
        'hardback': test_hardback_cover()
    }

    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    for cover_type, success in results.items():
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{cover_type.upper()}: {status}")

    if all(results.values()):
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print("\n⚠️  Some tests failed. See errors above.")
        sys.exit(1)
