#!/usr/bin/env python3
"""
Fix curly braces in template files.

In Python f-strings, curly braces need to be doubled to be treated as literals.
This script processes template files and doubles all curly braces except those
that are already doubled or are part of Python variable interpolation.
"""

import re
from pathlib import Path

def fix_fstring_braces(content: str) -> str:
    """
    Fix curly braces in f-strings.

    Strategy:
    1. Find all f-string literals
    2. Within those, double all single curly braces
    3. But preserve already-doubled braces and Python expressions
    """

    # This is complex, so let's use a simpler approach:
    # Just replace all { and } with {{ and }}
    # But skip lines that look like Python code (have colons, equals, etc.)

    lines = content.split('\n')
    fixed_lines = []
    in_fstring = False

    for line in lines:
        # Check if we're in an f-string
        if 'return f"""' in line or '= f"""' in line:
            in_fstring = True
            fixed_lines.append(line)
            continue

        if in_fstring and '"""' in line and not line.strip().startswith('#'):
            in_fstring = False
            fixed_lines.append(line)
            continue

        if in_fstring:
            # This line is inside an f-string
            # Double all curly braces that aren't already doubled or part of {variable}

            # Skip if it's a Python interpolation line (contains ': {')
            if re.match(r'.*\w+.*:\s*\{', line):
                # This looks like it has variable interpolation - be careful
                # Only double braces that are clearly part of code examples
                pass

            # Replace { with {{ and } with }} except in patterns like {variable}
            # First, protect Python variable interpolations
            protected = line

            # Find all {variable} or {expression} patterns
            placeholders = {}
            placeholder_pattern = r'\{[a-zA-Z_][a-zA-Z0-9_\.()\'\"]*\}'

            for i, match in enumerate(re.finditer(placeholder_pattern, line)):
                placeholder = f'__PLACEHOLDER_{i}__'
                placeholders[placeholder] = match.group(0)
                protected = protected.replace(match.group(0), placeholder, 1)

            # Now double all remaining braces
            protected = protected.replace('{', '{{').replace('}', '}}')

            # Restore placeholders
            for placeholder, original in placeholders.items():
                protected = protected.replace(placeholder, original)

            fixed_lines.append(protected)
        else:
            # Not in an f-string, keep as is
            fixed_lines.append(line)

    return '\n'.join(fixed_lines)


def process_file(file_path: Path):
    """Process a single template file."""
    print(f"Processing {file_path.name}...")

    content = file_path.read_text()
    fixed_content = fix_fstring_braces(content)

    if content != fixed_content:
        file_path.write_text(fixed_content)
        print(f"  ✓ Fixed {file_path.name}")
    else:
        print(f"  - No changes needed for {file_path.name}")


def main():
    """Fix all template files."""
    templates_dir = Path("/Users/venureddy/Downloads/LocalMind/code-intelligence/prompt/templates")

    template_files = [
        "refactoring.py",
        "feature_extension.py",
        "new_feature.py",
        "analysis.py",
        "bug_fix.py",
    ]

    for filename in template_files:
        file_path = templates_dir / filename
        if file_path.exists():
            try:
                process_file(file_path)
            except Exception as e:
                print(f"  ✗ Error processing {filename}: {e}")
        else:
            print(f"  ✗ File not found: {filename}")

    print("\n✅ Done!")


if __name__ == "__main__":
    main()
