#!/usr/bin/env python3
"""
Test Strict Validation Mode

Demonstrates the improvements from strict mode:
- Constructor dependency extraction
- Stack detection
- Dependency categorization
- Deduplication
- Validation checks
"""

import requests
import json

API_BASE = "http://localhost:8000"


def test_strict_validation():
    """Test prompt generation with strict validation."""
    print("\n" + "="*70)
    print("🔒 STRICT MODE VALIDATION TEST")
    print("="*70)

    request_data = {
        "type": "enhancement",
        "title": "Enhance SurgeonsService",
        "description": "Improve performance, structure, and error handling",
        "components": ["SurgeonsService"]
    }

    response = requests.post(
        f"{API_BASE}/api/prompt/generate",
        json=request_data
    )

    if response.status_code == 200:
        data = response.json()
        metadata = data.get('metadata', {})
        context = data.get('context', {})

        print("\n✅ Prompt Generated Successfully\n")

        # Display validation results
        validation = metadata.get('validation', {})
        print("="*70)
        print("📊 VALIDATION RESULTS")
        print("="*70)
        print(f"Valid: {validation.get('valid', 'N/A')}")

        errors = validation.get('errors', [])
        warnings = validation.get('warnings', [])

        if errors:
            print(f"\n❌ Errors ({len(errors)}):")
            for error in errors:
                print(f"   - {error}")
        else:
            print("\n✅ No Errors")

        if warnings:
            print(f"\n⚠️  Warnings ({len(warnings)}):")
            for warning in warnings:
                print(f"   - {warning}")
        else:
            print("\n✅ No Warnings")

        # Display stack detection
        print("\n" + "="*70)
        print("🔍 STACK DETECTION")
        print("="*70)
        print(f"Detected Stack: {context.get('tech_stack', 'N/A')}")

        # Display constructor dependencies
        constructor_deps = metadata.get('constructor_dependencies', [])
        print("\n" + "="*70)
        print("🔧 CONSTRUCTOR DEPENDENCIES")
        print("="*70)
        if constructor_deps:
            print(f"Found {len(constructor_deps)} dependencies:")
            for dep in constructor_deps:
                print(f"   - {dep}")
        else:
            print("No constructor dependencies found")

        # Display categorized dependencies
        categorized = metadata.get('categorized_dependencies', {})
        print("\n" + "="*70)
        print("📂 CATEGORIZED DEPENDENCIES")
        print("="*70)

        for category, deps in categorized.items():
            if deps:
                print(f"\n{category.upper()} ({len(deps)}):")
                for dep in deps:
                    print(f"   - {dep.get('name', 'Unknown')}")

        # Display dependency count
        print("\n" + "="*70)
        print("📊 STATISTICS")
        print("="*70)
        print(f"Total Dependencies: {metadata.get('dependencies_count', 0)}")
        print(f"Component Count: {metadata.get('component_count', 0)}")
        print(f"Has Source Code: {metadata.get('has_source_code', False)}")

        # Display components found
        components = context.get('components_found', [])
        print("\n" + "="*70)
        print("🎯 COMPONENTS FOUND")
        print("="*70)
        for comp in components:
            print(f"\nName: {comp.get('name')}")
            print(f"Type: {comp.get('type')}")
            print(f"Layer: {comp.get('layer')}")
            print(f"File: {comp.get('file_path')}")

        print("\n" + "="*70)
        print("✅ STRICT MODE VALIDATION COMPLETE")
        print("="*70)

    else:
        print(f"❌ Failed: {response.status_code}")
        print(f"Error: {response.text}")


def test_validation_failure():
    """Test validation with a non-existent component."""
    print("\n" + "="*70)
    print("🧪 TESTING VALIDATION FAILURE (Non-existent Component)")
    print("="*70)

    request_data = {
        "type": "enhancement",
        "title": "Enhance NonExistentService",
        "description": "This should fail validation",
        "components": ["NonExistentService"]
    }

    response = requests.post(
        f"{API_BASE}/api/prompt/generate",
        json=request_data
    )

    data = response.json()

    if 'error' in data:
        print(f"\n✅ Expected Error: {data['error']}")

        not_found = data.get('components_not_found', [])
        if not_found:
            print(f"\nComponents Not Found ({len(not_found)}):")
            for comp in not_found:
                print(f"   - {comp.get('name')}: {comp.get('error')}")
                suggestions = comp.get('suggestions', [])
                if suggestions:
                    print(f"     Suggestions: {', '.join(suggestions)}")
    else:
        print("❌ Expected validation to fail, but it succeeded")


def main():
    """Run all tests."""
    print("\n🧪 STRICT MODE VALIDATION TESTS")
    print("="*70)
    print("Testing the improvements:")
    print("  ✅ Constructor dependency extraction")
    print("  ✅ Stack detection")
    print("  ✅ Dependency categorization")
    print("  ✅ Deduplication")
    print("  ✅ Validation checks")
    print("="*70)

    # Test successful validation
    test_strict_validation()

    # Test validation failure
    test_validation_failure()

    print("\n🎉 ALL TESTS COMPLETE!\n")


if __name__ == "__main__":
    main()
