#!/usr/bin/env python3
"""
Test Universal Parser with Multiple Languages
Verifies that the TreeSitterParser with UniversalExtractor works for C#, Java, Python, Go, etc.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "code-intelligence"))

from parsers.treesitter.tree_sitter_parser import TreeSitterParser


def test_language(language: str, extension: str, test_code: str, expected_classes: list):
    """Test parsing for a specific language."""
    print(f"\n{'='*70}")
    print(f"Testing {language.upper()}")
    print(f"{'='*70}")

    # Create temp file
    test_file = Path(f"/tmp/test_parser{extension}")
    test_file.write_text(test_code)

    # Parse with universal parser
    parser = TreeSitterParser("/tmp")
    try:
        result = parser.parse_file(test_file)

        if result and result.get('entities'):
            entities = result['entities']
            classes = entities.get('classes', [])
            functions = entities.get('functions', [])
            methods = entities.get('methods', [])
            interfaces = entities.get('interfaces', [])
            imports = entities.get('imports', [])

            print(f"\n✅ {language} Parsing Results:")
            print(f"   Classes:    {len(classes)}")
            print(f"   Functions:  {len(functions)}")
            print(f"   Methods:    {len(methods)}")
            print(f"   Interfaces: {len(interfaces)}")
            print(f"   Imports:    {len(imports)}")

            if classes:
                print(f"\n   Found Classes:")
                for cls in classes:
                    print(f"      - {cls['name']} (line {cls['line_start']})")
                    if cls.get('methods'):
                        print(f"        Methods: {', '.join(cls['methods'])}")

            if functions:
                print(f"\n   Found Functions:")
                for func in functions:
                    print(f"      - {func['name']} (line {func['line_start']})")

            # Verify expected classes were found
            found_names = [cls['name'] for cls in classes]
            missing = [name for name in expected_classes if name not in found_names]

            if missing:
                print(f"\n⚠️  Missing classes: {missing}")
                return False
            else:
                print(f"\n✅ All expected classes found!")
                return True

        else:
            print(f"\n❌ Parsing failed or returned empty result")
            if result:
                print(f"   Result: {result}")
            return False

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        test_file.unlink(missing_ok=True)


def main():
    """Run tests for multiple languages."""

    results = {}

    # Test C#
    csharp_code = '''
using System;
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
    results['C#'] = test_language(
        "C#",
        ".cs",
        csharp_code,
        ["SearchCustomerTemplatesRequest", "PayrollServiceFocus", "SqlFocusRepository"]
    )

    # Test Java
    java_code = '''
package com.example.payroll;

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
    results['Java'] = test_language(
        "Java",
        ".java",
        java_code,
        ["PayrollService", "Employee"]
    )

    # Test Python
    python_code = '''
from typing import List

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

def standalone_function():
    pass
'''
    results['Python'] = test_language(
        "Python",
        ".py",
        python_code,
        ["UserService", "UserRepository"]
    )

    # Test Go
    go_code = '''
package main

import "fmt"

type PayrollService struct {
    db Database
}

func (p *PayrollService) ProcessPayroll(employee Employee) error {
    return nil
}

type Employee struct {
    Name   string
    Salary float64
}

func NewEmployee(name string) *Employee {
    return &Employee{Name: name}
}
'''
    results['Go'] = test_language(
        "Go",
        ".go",
        go_code,
        ["PayrollService", "Employee"]  # Go uses structs
    )

    # Test TypeScript
    typescript_code = '''
import { Injectable } from '@nestjs/common';

@Injectable()
export class AuthService {
    async login(username: string, password: string) {
        // Implementation
    }

    async validateUser(username: string) {
        return true;
    }
}

export class UserDto {
    username: string;
    email: string;
}

export interface IAuthService {
    login(username: string, password: string): Promise<any>;
}
'''
    results['TypeScript'] = test_language(
        "TypeScript",
        ".ts",
        typescript_code,
        ["AuthService", "UserDto"]
    )

    # Print summary
    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")

    total = len(results)
    passed = sum(1 for success in results.values() if success)

    for lang, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}  {lang}")

    print(f"\nTotal: {passed}/{total} languages passed")

    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Universal parser works for all languages!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} language(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
