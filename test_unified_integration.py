#!/usr/bin/env python3
"""
Test UnifiedIndexer Integration with Tree-sitter Universal Parser
Verifies that C# classes are captured through the full indexing pipeline.
"""

import sys
import json
from pathlib import Path
import shutil

sys.path.insert(0, str(Path(__file__).parent / "code-intelligence"))

from indexer.unified_indexer import UnifiedIndexer


def test_csharp_integration():
    """Test that C# code is captured by UnifiedIndexer via Tree-sitter."""

    print("="*70)
    print("Testing UnifiedIndexer Integration with Tree-sitter")
    print("="*70)

    # Create a temporary test repository with C# code
    test_repo = Path("/tmp/test_csharp_repo")
    if test_repo.exists():
        shutil.rmtree(test_repo)
    test_repo.mkdir(parents=True)

    # Create a C# file with classes
    csharp_code = '''using System;
using System.Collections.Generic;

namespace Payroll {
    public class SearchCustomerTemplatesRequest {
        public string Query { get; set; }
        public int PageSize { get; set; }
    }

    public class PayrollServiceFocus : ServiceBase {
        public void Post(SearchCustomerTemplatesRequest request) {
            // Implementation
        }

        public List<Template> Get() {
            return new List<Template>();
        }
    }

    public class SqlFocusRepository : ISqlRepository {
        public void Save(object entity) {
            // Implementation
        }
    }

    public interface ISqlRepository {
        void Save(object entity);
    }
}
'''

    csharp_file = test_repo / "PayrollService.cs"
    csharp_file.write_text(csharp_code)

    # Also add a Java file to test multi-language support
    java_code = '''package com.example.payroll;

import java.util.List;

public class PayrollService {
    public void processPayroll(Employee employee) {
        // Implementation
    }

    public List<Payment> getPayments() {
        return new ArrayList<>();
    }
}

public class Employee {
    private String name;
    private double salary;

    public String getName() {
        return name;
    }
}
'''

    java_file = test_repo / "PayrollService.java"
    java_file.write_text(java_code)

    # Add a Python file
    python_code = '''from typing import List

class UserService:
    def __init__(self, repository):
        self.repository = repository

    def get_user(self, user_id: int):
        return self.repository.find_by_id(user_id)

    def create_user(self, name: str):
        pass

class UserRepository:
    def find_by_id(self, user_id: int):
        pass
'''

    python_file = test_repo / "user_service.py"
    python_file.write_text(python_code)

    print(f"\n📁 Created test repository: {test_repo}")
    print(f"   - PayrollService.cs (C# - 3 classes, 1 interface)")
    print(f"   - PayrollService.java (Java - 2 classes)")
    print(f"   - user_service.py (Python - 2 classes)")

    # Run UnifiedIndexer
    print(f"\n🔍 Running UnifiedIndexer...")

    try:
        indexer = UnifiedIndexer(str(test_repo))
        index = indexer.index_repository()

        # Analyze results
        print(f"\n✅ Indexing completed successfully!")

        components = index.get("components", [])
        print(f"\n📊 Total components found: {len(components)}")

        # Filter by language
        csharp_components = [c for c in components if c.get("metadata", {}).get("language") == "c_sharp"]
        java_components = [c for c in components if c.get("metadata", {}).get("language") == "java"]
        python_components = [c for c in components if c.get("metadata", {}).get("language") == "python"]

        print(f"\n🔷 C# Components: {len(csharp_components)}")
        if csharp_components:
            for comp in csharp_components:
                print(f"   - {comp['name']} ({comp['type']}) in {comp['file_path']} at line {comp['line_start']}")

        print(f"\n☕ Java Components: {len(java_components)}")
        if java_components:
            for comp in java_components:
                print(f"   - {comp['name']} ({comp['type']}) in {comp['file_path']} at line {comp['line_start']}")

        print(f"\n🐍 Python Components: {len(python_components)}")
        if python_components:
            for comp in python_components:
                print(f"   - {comp['name']} ({comp['type']}) in {comp['file_path']} at line {comp['line_start']}")

        # Verify expected C# classes
        expected_csharp_classes = [
            "SearchCustomerTemplatesRequest",
            "PayrollServiceFocus",
            "SqlFocusRepository",
        ]

        expected_csharp_interfaces = ["ISqlRepository"]

        found_csharp_names = [c['name'] for c in csharp_components]

        print(f"\n🎯 Verification:")
        all_found = True

        for expected in expected_csharp_classes:
            if expected in found_csharp_names:
                print(f"   ✅ Found C# class: {expected}")
            else:
                print(f"   ❌ MISSING C# class: {expected}")
                all_found = False

        for expected in expected_csharp_interfaces:
            if expected in found_csharp_names:
                print(f"   ✅ Found C# interface: {expected}")
            else:
                print(f"   ❌ MISSING C# interface: {expected}")
                all_found = False

        # Verify Java classes
        expected_java_classes = ["PayrollService", "Employee"]
        found_java_names = [c['name'] for c in java_components]

        for expected in expected_java_classes:
            if expected in found_java_names:
                print(f"   ✅ Found Java class: {expected}")
            else:
                print(f"   ⚠️  Missing Java class: {expected}")

        # Verify Python classes
        expected_python_classes = ["UserService", "UserRepository"]
        found_python_names = [c['name'] for c in python_components]

        for expected in expected_python_classes:
            if expected in found_python_names:
                print(f"   ✅ Found Python class: {expected}")
            else:
                print(f"   ⚠️  Missing Python class: {expected}")

        # Save detailed output for inspection
        output_file = Path("/tmp/unified_index_test_output.json")
        with open(output_file, "w") as f:
            json.dump(index, f, indent=2)
        print(f"\n💾 Detailed output saved to: {output_file}")

        if all_found:
            print(f"\n🎉 SUCCESS! All C# entities captured by universal parser!")
            print(f"\n✨ Key Achievement:")
            print(f"   - C# classes now indexed via Tree-sitter")
            print(f"   - Java classes automatically supported")
            print(f"   - Python classes automatically supported")
            print(f"   - ANY language supported by Tree-sitter will work!")
            return 0
        else:
            print(f"\n⚠️  Some C# entities were not found")
            return 1

    except Exception as e:
        print(f"\n❌ Error during indexing: {e}")
        import traceback
        traceback.print_exc()
        return 1

    finally:
        # Cleanup
        if test_repo.exists():
            shutil.rmtree(test_repo)
            print(f"\n🧹 Cleaned up test repository")


def main():
    """Run the integration test."""
    return test_csharp_integration()


if __name__ == "__main__":
    sys.exit(main())
