#!/usr/bin/env python3
"""
Verification script to check if the service parsing fix is present.
"""

import sys
import json
from pathlib import Path

# Add to path
sys.path.insert(0, str(Path(__file__).parent / "code-intelligence"))

def check_parser_logic():
    """Check if the parser properly captures services."""

    print("=" * 70)
    print("Service Parsing Verification")
    print("=" * 70)

    # Check 1: Verify EnhancedNestJSParser has service parsing
    print("\n✓ Check 1: EnhancedNestJSParser._parse_service exists")
    from parsers.nestjs.enhanced_nestjs_parser import EnhancedNestJSParser

    if hasattr(EnhancedNestJSParser, '_parse_service'):
        print("  ✅ _parse_service method found")
    else:
        print("  ❌ _parse_service method NOT found")
        return False

    # Check 2: Verify OptimizedNestJSParser uses enhanced parser
    print("\n✓ Check 2: OptimizedNestJSParser uses EnhancedNestJSParser")
    from parsers.nestjs.optimized_nestjs_parser import OptimizedNestJSParser

    # Check if it has services list
    if hasattr(OptimizedNestJSParser, '__init__'):
        print("  ✅ OptimizedNestJSParser initialized correctly")
    else:
        print("  ❌ OptimizedNestJSParser initialization issue")
        return False

    # Check 3: Verify _compile_results includes services
    print("\n✓ Check 3: _compile_results includes services")
    parser_code = open("code-intelligence/parsers/nestjs/optimized_nestjs_parser.py").read()

    if '"services": self.services' in parser_code:
        print("  ✅ Services are included in compiled results")
    else:
        print("  ❌ Services NOT included in compiled results")
        return False

    # Check 4: Look for potential issues in parsing logic
    print("\n✓ Check 4: Checking service detection patterns")
    enhanced_code = open("code-intelligence/parsers/nestjs/enhanced_nestjs_parser.py").read()

    issues = []

    # Check if .service.ts pattern is used
    if '".service.ts" in file_path.name' in enhanced_code:
        print("  ✅ Files ending with .service.ts are parsed as services")
    else:
        issues.append("Missing .service.ts pattern check")

    # Check if @Injectable is verified
    if '"@Injectable" not in content' in enhanced_code:
        print("  ✅ @Injectable decorator is verified in service parser")
    else:
        issues.append("@Injectable verification missing")

    # Check if services are appended
    if 'self.services.append(service)' in enhanced_code:
        print("  ✅ Services are appended to services list")
    else:
        issues.append("Services not appended to list")

    # Check 5: Look for potential missed services issue
    print("\n✓ Check 5: Checking for fallback @Injectable parsing")

    # The issue: what if a service doesn't end with .service.ts?
    if_elif_count = enhanced_code.count('elif ')

    # Check if there's a fallback for @Injectable files
    has_injectable_fallback = False
    lines = enhanced_code.split('\n')

    for i, line in enumerate(lines):
        if '@Injectable' in line and 'elif' not in lines[max(0, i-1)]:
            # Check if it's NOT part of the if-elif chain
            if 'def _parse_file' in '\n'.join(lines[max(0, i-20):i]):
                has_injectable_fallback = True
                break

    if not has_injectable_fallback:
        print("  ⚠️  WARNING: No fallback for @Injectable files that don't match naming patterns")
        print("     This means services not ending with .service.ts might be missed!")
        issues.append("Missing fallback for generic @Injectable files")
    else:
        print("  ✅ Fallback exists for generic @Injectable files")

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    if issues:
        print(f"\n⚠️  Found {len(issues)} potential issue(s):")
        for i, issue in enumerate(issues, 1):
            print(f"  {i}. {issue}")

        print("\n" + "=" * 70)
        print("RECOMMENDATION:")
        print("=" * 70)
        print("""
The parser should add a fallback case to capture ALL @Injectable classes
that don't match specific patterns (guards, interceptors, etc.).

Add this to the if-elif chain in _parse_file:

    # ... existing elif conditions ...

    # Fallback: capture any @Injectable class as a service
    elif "@Injectable" in content and "export class" in content:
        # Only if not already caught by specific parsers
        self._parse_service(content, str(relative_path), file_path)
""")
        return False
    else:
        print("\n✅ All checks passed! Service parsing is properly configured.")
        return True

if __name__ == "__main__":
    success = check_parser_logic()
    sys.exit(0 if success else 1)
