#!/usr/bin/env python3
"""
Test Prompt Generation API Endpoint

Tests the new /api/prompt/generate endpoint to ensure it works correctly.
"""

import requests
import json

API_BASE = "http://localhost:8000"


def test_prompt_types():
    """Test getting available prompt types."""
    print("="*70)
    print("Testing GET /api/prompt/types")
    print("="*70)

    response = requests.get(f"{API_BASE}/api/prompt/types")

    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ Available Types:")
        for ptype in data.get('available_types', []):
            desc = data.get('descriptions', {}).get(ptype, 'No description')
            print(f"   - {ptype}: {desc}")
        return True
    else:
        print(f"❌ Failed: {response.text}")
        return False


def test_prompt_generation():
    """Test generating a prompt for SurgeonsService."""
    print("\n" + "="*70)
    print("Testing POST /api/prompt/generate")
    print("="*70)

    request_data = {
        "type": "enhancement",
        "title": "Enhance SurgeonsService",
        "description": "Improve performance, code structure, and error handling in the SurgeonsService",
        "components": ["SurgeonsService"]
    }

    print(f"\nRequest:")
    print(json.dumps(request_data, indent=2))

    response = requests.post(
        f"{API_BASE}/api/prompt/generate",
        json=request_data
    )

    print(f"\nStatus: {response.status_code}")

    if response.status_code == 200:
        data = response.json()

        print(f"\n✅ Prompt Generated Successfully!")

        # Print metadata
        metadata = data.get('metadata', {})
        print(f"\nMetadata:")
        print(f"   Type: {metadata.get('type')}")
        print(f"   Component Count: {metadata.get('component_count')}")
        print(f"   Has Source Code: {metadata.get('has_source_code')}")

        # Print context
        context = data.get('context', {})
        components_found = context.get('components_found', [])
        print(f"\nComponents Found: {len(components_found)}")
        for comp in components_found:
            print(f"   - {comp.get('name')} ({comp.get('type')}) in {comp.get('layer')}")

        dependencies = context.get('dependencies', [])
        print(f"\nDependencies: {len(dependencies)}")
        for dep in dependencies[:5]:  # Show first 5
            print(f"   - {dep.get('name')} ({dep.get('type')})")

        dtos = context.get('related_dtos', [])
        print(f"\nRelated DTOs: {len(dtos)}")
        for dto in dtos[:5]:  # Show first 5
            print(f"   - {dto.get('name')}")

        # Print prompt preview
        prompt = data.get('prompt', '')
        print(f"\n{'='*70}")
        print("GENERATED PROMPT (First 500 chars):")
        print(f"{'='*70}")
        print(prompt[:500])
        print("...")

        # Save full prompt to file
        output_file = "/tmp/generated_prompt.txt"
        with open(output_file, 'w') as f:
            f.write(prompt)
        print(f"\n💾 Full prompt saved to: {output_file}")

        return True

    else:
        print(f"❌ Failed: {response.text}")
        return False


def main():
    """Run all tests."""
    print("\n🧪 Testing Prompt Generation API")
    print("="*70)

    tests = [
        ("Get Prompt Types", test_prompt_types),
        ("Generate Prompt", test_prompt_generation),
    ]

    results = []

    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"\n❌ Test '{test_name}' raised exception: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))

    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)

    passed = sum(1 for _, success in results if success)
    total = len(results)

    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}  {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
