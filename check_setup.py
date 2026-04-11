"""
Setup Checker for Code Intelligence System & Tree Sitter Parser
Verifies all required software and dependencies are installed.
"""

import sys
import subprocess
from pathlib import Path
import importlib.util

# Color codes for output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.END}")

def print_success(text):
    print(f"{Colors.GREEN}✓{Colors.END} {text}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠{Colors.END} {text}")

def print_error(text):
    print(f"{Colors.RED}✗{Colors.END} {text}")

def print_info(text):
    print(f"  {text}")

def check_python_version():
    """Check Python version."""
    print_header("Python Version Check")

    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"

    print_info(f"Python version: {version_str}")

    if version.major == 3 and version.minor >= 8:
        print_success(f"Python {version_str} is installed (>= 3.8 required)")
        return True
    else:
        print_error(f"Python {version_str} is installed but 3.8+ is required")
        return False

def check_package(package_name, import_name=None, min_version=None):
    """Check if a Python package is installed."""
    if import_name is None:
        import_name = package_name.replace("-", "_")

    try:
        module = __import__(import_name)
        version = getattr(module, '__version__', 'unknown')

        # Handle version as tuple (e.g., esprima returns tuple)
        if isinstance(version, tuple):
            version = '.'.join(map(str, version))

        # Convert to string if not already
        version = str(version) if version != 'unknown' else 'unknown'

        if min_version and version != 'unknown':
            try:
                from packaging import version as pkg_version
                if pkg_version.parse(version) >= pkg_version.parse(min_version):
                    print_success(f"{package_name} {version} installed")
                    return True
                else:
                    print_warning(f"{package_name} {version} installed (minimum {min_version} recommended)")
                    return True
            except Exception:
                # If version comparison fails, just mark as installed
                print_success(f"{package_name} {version} installed")
                return True
        else:
            print_success(f"{package_name} {version} installed")
            return True

    except ImportError:
        print_error(f"{package_name} not installed")
        return False

def check_core_dependencies():
    """Check core Python dependencies."""
    print_header("Core Dependencies Check")

    dependencies = {
        # Core parsing and AST
        'tree-sitter': ('tree_sitter', '0.21.0'),
        'tree-sitter-languages': ('tree_sitter_languages', '1.10.0'),
        'libcst': ('libcst', '1.1.0'),
        'esprima': ('esprima', '4.0.0'),
        'pyyaml': ('yaml', '6.0.0'),
        'python-hcl2': ('hcl2', '4.3.0'),

        # Graph and network analysis
        'networkx': ('networkx', '3.2.0'),
        'matplotlib': ('matplotlib', '3.7.0'),

        # Vector search and embeddings
        'chromadb': ('chromadb', '0.4.0'),
        'sentence-transformers': ('sentence_transformers', '2.3.0'),
        'faiss-cpu': ('faiss', '1.8.0'),
        'openai': ('openai', '1.10.0'),

        # Web framework
        'fastapi': ('fastapi', '0.109.0'),
        'uvicorn': ('uvicorn', '0.27.0'),
        'pydantic': ('pydantic', '2.7.0'),

        # Data processing
        'pandas': ('pandas', '2.2.0'),
        'numpy': ('numpy', '1.26.0'),

        # Code analysis
        'radon': ('radon', '6.0.0'),
        'lizard': ('lizard', '1.17.0'),

        # Utilities
        'python-dotenv': ('dotenv', '1.0.0'),
        'rich': ('rich', '13.7.0'),
        'click': ('click', '8.1.0'),
        'loguru': ('loguru', '0.7.0'),
        'aiofiles': ('aiofiles', '23.2.0'),
    }

    results = []
    for package_name, (import_name, min_version) in dependencies.items():
        result = check_package(package_name, import_name, min_version)
        results.append(result)

    installed = sum(results)
    total = len(results)

    print_info(f"\nInstalled: {installed}/{total} packages")

    return all(results)

def check_tree_sitter_languages():
    """Check Tree Sitter language support."""
    print_header("Tree Sitter Language Support Check")

    try:
        import tree_sitter_languages as tsl

        languages = [
            'python', 'javascript', 'typescript', 'tsx',
            'java', 'go', 'rust', 'cpp', 'c',
            'c_sharp', 'ruby', 'php', 'swift', 'kotlin'
        ]

        supported = []
        unsupported = []

        for lang in languages:
            try:
                parser = tsl.get_parser(lang)
                supported.append(lang)
                print_success(f"Language '{lang}' supported")
            except Exception as e:
                unsupported.append(lang)
                print_warning(f"Language '{lang}' not available: {e}")

        print_info(f"\nSupported languages: {len(supported)}/{len(languages)}")

        return len(supported) > 0

    except ImportError:
        print_error("tree-sitter-languages not installed")
        return False

def check_project_structure():
    """Check if project structure is correct."""
    print_header("Project Structure Check")

    required_paths = [
        'code-intelligence',
        'code-intelligence/parsers',
        'code-intelligence/parsers/treesitter',
        'code-intelligence/parsers/treesitter/tree_sitter_parser.py',
        'code-intelligence/parsers/treesitter/ontology_generator.py',
        'code-intelligence/parsers/treesitter/language_extractors.py',
        'code-intelligence/graph',
        'code-intelligence/indexer',
        'requirements.txt',
    ]

    results = []
    for path_str in required_paths:
        path = Path(path_str)
        if path.exists():
            print_success(f"{path_str}")
            results.append(True)
        else:
            print_error(f"{path_str} not found")
            results.append(False)

    print_info(f"\nFound: {sum(results)}/{len(results)} required paths")

    return all(results)

def check_demo_repo():
    """Check if demo repository exists."""
    print_header("Demo Repository Check")

    demo_repo = Path("./demo-repo")

    if demo_repo.exists():
        # Count files
        ts_files = list(demo_repo.rglob("*.ts"))
        js_files = list(demo_repo.rglob("*.js"))
        py_files = list(demo_repo.rglob("*.py"))

        print_success(f"Demo repository found at: {demo_repo}")
        print_info(f"  TypeScript files: {len(ts_files)}")
        print_info(f"  JavaScript files: {len(js_files)}")
        print_info(f"  Python files: {len(py_files)}")

        return True
    else:
        print_warning("Demo repository not found at ./demo-repo")
        print_info("  You can still use the parser with your own repositories")
        return False

def check_data_directory():
    """Check/create data directory for outputs."""
    print_header("Data Directory Check")

    data_dir = Path("./data")

    if not data_dir.exists():
        try:
            data_dir.mkdir(parents=True, exist_ok=True)
            print_success("Created ./data directory")

            # Create subdirectories
            (data_dir / "treesitter").mkdir(exist_ok=True)
            (data_dir / "treesitter" / "visualizations").mkdir(exist_ok=True)
            print_success("Created ./data/treesitter subdirectories")

            return True
        except Exception as e:
            print_error(f"Failed to create data directory: {e}")
            return False
    else:
        print_success("Data directory exists: ./data")

        # Check/create treesitter subdirectory
        ts_dir = data_dir / "treesitter"
        if not ts_dir.exists():
            ts_dir.mkdir(exist_ok=True)
            (ts_dir / "visualizations").mkdir(exist_ok=True)
            print_success("Created ./data/treesitter subdirectories")

        return True

def test_tree_sitter_parser():
    """Test if Tree Sitter parser can be imported and initialized."""
    print_header("Tree Sitter Parser Test")

    try:
        sys.path.insert(0, str(Path.cwd() / "code-intelligence"))
        sys.path.insert(0, str(Path.cwd()))

        from parsers.treesitter.tree_sitter_parser import TreeSitterParser
        from parsers.treesitter.ontology_generator import OntologyGenerator

        print_success("TreeSitterParser imported successfully")
        print_success("OntologyGenerator imported successfully")

        # Try to initialize
        parser = TreeSitterParser(".")
        print_success("Parser initialized successfully")

        # Test language detection
        test_cases = [
            (Path("test.py"), "python"),
            (Path("test.ts"), "typescript"),
            (Path("test.js"), "javascript"),
        ]

        all_ok = True
        for file_path, expected in test_cases:
            detected = parser._get_language_from_extension(file_path)
            if detected == expected:
                print_success(f"Language detection: {file_path.suffix} -> {detected}")
            else:
                print_error(f"Language detection failed: {file_path.suffix} -> {detected} (expected {expected})")
                all_ok = False

        return all_ok

    except Exception as e:
        print_error(f"Failed to test parser: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_git():
    """Check if git is installed."""
    print_header("Git Check")

    try:
        result = subprocess.run(
            ['git', '--version'],
            capture_output=True,
            text=True,
            check=True
        )
        version = result.stdout.strip()
        print_success(f"{version}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print_warning("Git not found (optional, but recommended)")
        return False

def check_optional_tools():
    """Check optional but useful tools."""
    print_header("Optional Tools Check")

    tools = {
        'neo4j': 'Neo4j database (for graph import)',
        'graphviz': 'Graphviz (for advanced visualizations)',
    }

    for tool, description in tools.items():
        try:
            subprocess.run(
                [tool, '--version'],
                capture_output=True,
                check=True
            )
            print_success(f"{tool} - {description}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print_info(f"{tool} not installed - {description}")

def generate_install_commands(missing_packages):
    """Generate commands to install missing packages."""
    print_header("Installation Commands")

    if not missing_packages:
        print_success("All required packages are installed!")
        return

    print_info("To install missing packages, run:\n")
    print(f"{Colors.BOLD}pip install -r requirements.txt{Colors.END}\n")

    print_info("Or install individually:\n")
    for package in missing_packages:
        print(f"pip install {package}")

def print_summary(checks):
    """Print summary of all checks."""
    print_header("Setup Summary")

    total = len(checks)
    passed = sum(1 for _, status in checks.items() if status)
    failed = total - passed

    print_info(f"Total checks: {total}")
    print_success(f"Passed: {passed}")

    if failed > 0:
        print_error(f"Failed: {failed}")
        print_info("\nFailed checks:")
        for check_name, status in checks.items():
            if not status:
                print_error(f"  - {check_name}")
    else:
        print_success(f"All checks passed!")

    print_info("\nSystem Status:")
    if passed == total:
        print_success("✓ System is fully set up and ready to use!")
        print_info("\nNext steps:")
        print_info("  1. Run quick test: python3 test_treesitter_simple.py")
        print_info("  2. Try examples: python3 example_treesitter_usage.py")
        print_info("  3. Parse your repo: See TREESITTER_PARSER_GUIDE.md")
    elif passed >= total * 0.8:
        print_warning("⚠ System is mostly ready, but some components are missing")
        print_info("  Install missing packages with: pip install -r requirements.txt")
    else:
        print_error("✗ System needs setup")
        print_info("  Install required packages with: pip install -r requirements.txt")

def main():
    """Run all checks."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}")
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 10 + "CODE INTELLIGENCE SYSTEM - SETUP CHECKER" + " " * 18 + "║")
    print("║" + " " * 14 + "Tree Sitter Parser & Dependencies" + " " * 21 + "║")
    print("╚" + "═" * 68 + "╝")
    print(f"{Colors.END}\n")

    checks = {}

    # Run all checks
    checks['Python Version'] = check_python_version()
    checks['Core Dependencies'] = check_core_dependencies()
    checks['Tree Sitter Languages'] = check_tree_sitter_languages()
    checks['Project Structure'] = check_project_structure()
    checks['Demo Repository'] = check_demo_repo()
    checks['Data Directory'] = check_data_directory()
    checks['Git'] = check_git()
    checks['Tree Sitter Parser'] = test_tree_sitter_parser()

    # Optional checks (don't affect overall status)
    check_optional_tools()

    # Print summary
    print_summary(checks)

    # Exit code based on critical checks
    critical_checks = [
        'Python Version',
        'Core Dependencies',
        'Tree Sitter Languages',
        'Project Structure',
        'Tree Sitter Parser'
    ]

    critical_passed = all(checks.get(check, False) for check in critical_checks)

    return 0 if critical_passed else 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Setup check interrupted by user{Colors.END}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}Setup check failed with error: {e}{Colors.END}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
