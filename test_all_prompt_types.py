#!/usr/bin/env python3
"""
Test All Prompt Types

Tests all 6 prompt types to ensure they all work correctly.
"""

import requests
import json

API_BASE = "http://localhost:8000"


def test_prompt_type(prompt_type, title, description):
    """Test generating a prompt for a specific type."""
    print(f"\n{'='*70}")
    print(f"Testing: {prompt_type.upper()}")
    print(f"{'='*70}")

    request_data = {
        "type": prompt_type,
        "title": title,
        "description": description,
        "components": ["SurgeonsService"]
    }

    response = requests.post(
        f"{API_BASE}/api/prompt/generate",
        json=request_data
    )

    if response.status_code == 200:
        data = response.json()
        prompt = data.get('prompt', '')
        metadata = data.get('metadata', {})

        print(f"✅ {prompt_type.upper()} prompt generated successfully!")
        print(f"   Length: {len(prompt)} characters")
        print(f"   Component Count: {metadata.get('component_count')}")

        # Save to file
        output_file = f"/tmp/prompt_{prompt_type}.txt"
        with open(output_file, 'w') as f:
            f.write(prompt)
        print(f"   Saved to: {output_file}")

        # Show header
        header_lines = prompt.split('\n')[:10]
        print(f"\n   Header Preview:")
        for line in header_lines[:5]:
            if line.strip():
                print(f"      {line}")

        return True
    else:
        print(f"❌ Failed: {response.status_code}")
        print(f"   Error: {response.text}")
        return False


def main():
    """Test all prompt types."""
    print("\n🧪 Testing All Prompt Types")
    print("="*70)

    # Test getting available types first
    print("\n1. Getting Available Types...")
    response = requests.get(f"{API_BASE}/api/prompt/types")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Available types: {data.get('available_types')}")
    else:
        print(f"❌ Failed to get types")
        return 1

    # Test each prompt type
    tests = [
        ("enhancement", "Enhance SurgeonsService", "Improve performance, structure, and error handling"),
        ("bug_fix", "Fix pagination bug in SurgeonsService", "Users report that pagination returns wrong page numbers when page > 10"),
        ("new_feature", "Add bulk upload feature", "Add ability to upload multiple surgeons via CSV file"),
        ("refactoring", "Refactor SurgeonsService", "Extract validation logic into separate validator class, reduce method complexity"),
        ("analysis", "Analyze SurgeonsService code quality", "Perform comprehensive code analysis covering security, performance, and maintainability"),
        ("feature_extension", "Extend search with fuzzy matching", "Add optional fuzzy matching capability to existing surgeon search"),
    ]

    results = []
    for prompt_type, title, description in tests:
        try:
            success = test_prompt_type(prompt_type, title, description)
            results.append((prompt_type, success))
        except Exception as e:
            print(f"\n❌ Test '{prompt_type}' raised exception: {e}")
            import traceback
            traceback.print_exc()
            results.append((prompt_type, False))

    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)

    passed = sum(1 for _, success in results if success)
    total = len(results)

    for prompt_type, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}  {prompt_type}")

    print(f"\nTotal: {passed}/{total} prompt types passed")

    # Show file locations
    if passed > 0:
        print("\n📁 Generated Prompts:")
        for prompt_type, success in results:
            if success:
                print(f"   - /tmp/prompt_{prompt_type}.txt")

    if passed == total:
        print("\n🎉 ALL PROMPT TYPES WORKING!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} prompt type(s) failed")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
