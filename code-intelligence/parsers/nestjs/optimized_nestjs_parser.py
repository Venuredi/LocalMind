"""
Optimized NestJS Parser
High-performance parser with parallel processing, caching, and progress tracking.
"""

import re
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

# Import base parser
from .enhanced_nestjs_parser import EnhancedNestJSParser

# Extended exclusion patterns for better performance
_EXCLUDED_DIRS = {
    "node_modules", ".pnpm", ".npm", ".yarn",
    "dist", "build", ".next", "out", "coverage",
    ".git", ".svn", ".hg",
    "vendor", "__pycache__", ".venv", "venv",
    ".nyc_output", ".turbo", ".cache",
    "bower_components", "jspm_packages",
    ".idea", ".vscode", ".vs",
    "tmp", "temp", ".tmp",
}

_EXCLUDED_FILE_PATTERNS = {
    ".spec.ts", ".test.ts",
    ".d.ts",  # TypeScript declaration files
    ".min.ts", ".bundle.ts",
}


class OptimizedNestJSParser:
    """
    Optimized NestJS parser with:
    - Parallel file processing
    - File caching
    - Progress callbacks
    - Better exclusions
    - Incremental parsing support
    """

    def __init__(
        self,
        repo_path: str,
        progress_callback: Optional[Callable] = None,
        max_workers: int = 4,
        use_cache: bool = True,
        cache_dir: Optional[str] = None
    ):
        """
        Initialize optimized parser.

        Args:
            repo_path: Path to repository
            progress_callback: Optional callback for progress updates
            max_workers: Number of parallel workers
            use_cache: Whether to use file caching
            cache_dir: Directory for cache files
        """
        self.repo_path = Path(repo_path)
        self.progress_callback = progress_callback
        self.max_workers = max_workers
        self.use_cache = use_cache

        # Cache directory
        if cache_dir:
            self.cache_dir = Path(cache_dir)
        else:
            self.cache_dir = Path.home() / ".localmind_cache" / "parser"

        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Results storage
        self.controllers: List[Dict[str, Any]] = []
        self.services: List[Dict[str, Any]] = []
        self.dtos: List[Dict[str, Any]] = []
        self.entities: List[Dict[str, Any]] = []
        self.repositories: List[Dict[str, Any]] = []
        self.graphql_resolvers: List[Dict[str, Any]] = []
        self.graphql_mutations: List[Dict[str, Any]] = []
        self.socket_gateways: List[Dict[str, Any]] = []
        self.bull_processors: List[Dict[str, Any]] = []
        self.mongo_schemas: List[Dict[str, Any]] = []
        self.microservices: List[Dict[str, Any]] = []
        self.guards: List[Dict[str, Any]] = []
        self.interceptors: List[Dict[str, Any]] = []
        self.middleware: List[Dict[str, Any]] = []
        self.modules: List[Dict[str, Any]] = []

        # Statistics
        self.stats = {
            "total_files": 0,
            "processed_files": 0,
            "cached_files": 0,
            "skipped_files": 0,
            "start_time": None,
            "end_time": None,
        }

    def _is_excluded(self, file_path: Path) -> bool:
        """
        Check if file should be excluded.

        Args:
            file_path: Path to check

        Returns:
            True if should be excluded
        """
        # Check directories
        for part in file_path.parts:
            if part in _EXCLUDED_DIRS:
                return True

        # Check file patterns
        file_name = file_path.name
        for pattern in _EXCLUDED_FILE_PATTERNS:
            if file_name.endswith(pattern):
                return True

        return False

    def _get_file_hash(self, file_path: Path) -> str:
        """
        Get hash of file content for caching.

        Args:
            file_path: File to hash

        Returns:
            MD5 hash of file content
        """
        try:
            content = file_path.read_bytes()
            return hashlib.md5(content).hexdigest()
        except Exception:
            return ""

    def _get_cache_path(self, file_path: Path) -> Path:
        """
        Get cache file path for a source file.

        Args:
            file_path: Source file path

        Returns:
            Cache file path
        """
        # Create a unique cache filename based on full path
        relative = file_path.relative_to(self.repo_path)
        cache_name = str(relative).replace("/", "_").replace("\\", "_")
        return self.cache_dir / f"{cache_name}.cache.json"

    def _load_from_cache(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """
        Load parsed data from cache if valid.

        Args:
            file_path: Source file path

        Returns:
            Cached data if valid, None otherwise
        """
        if not self.use_cache:
            return None

        cache_path = self._get_cache_path(file_path)

        if not cache_path.exists():
            return None

        try:
            # Load cache
            with open(cache_path, "r", encoding="utf-8") as f:
                cache_data = json.load(f)

            # Validate cache
            current_hash = self._get_file_hash(file_path)
            if cache_data.get("file_hash") == current_hash:
                self.stats["cached_files"] += 1
                return cache_data.get("parsed_data")

        except Exception:
            pass

        return None

    def _save_to_cache(self, file_path: Path, parsed_data: Dict[str, Any]):
        """
        Save parsed data to cache.

        Args:
            file_path: Source file path
            parsed_data: Parsed data to cache
        """
        if not self.use_cache:
            return

        try:
            cache_path = self._get_cache_path(file_path)

            cache_data = {
                "file_hash": self._get_file_hash(file_path),
                "cached_at": datetime.now().isoformat(),
                "parsed_data": parsed_data,
            }

            with open(cache_path, "w", encoding="utf-8") as f:
                json.dump(cache_data, f)

        except Exception as e:
            # Silently fail cache writes
            pass

    def _parse_single_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """
        Parse a single file (used by parallel processing).

        Args:
            file_path: File to parse

        Returns:
            Parsed data or None
        """
        try:
            # Check cache first
            cached = self._load_from_cache(file_path)
            if cached:
                return cached

            # Create a single-file parser
            parser = EnhancedNestJSParser(str(self.repo_path))

            # Parse just this file
            parser._parse_file(file_path)

            # Collect results
            result = {
                "controllers": parser.controllers,
                "services": parser.services,
                "dtos": parser.dtos,
                "entities": parser.entities,
                "repositories": parser.repositories,
                "graphql_resolvers": parser.graphql_resolvers,
                "socket_gateways": parser.socket_gateways,
                "bull_processors": parser.bull_processors,
                "mongo_schemas": parser.mongo_schemas,
                "guards": parser.guards,
                "interceptors": parser.interceptors,
                "middleware": parser.middleware,
                "modules": parser.modules,
            }

            # Save to cache
            self._save_to_cache(file_path, result)

            return result

        except Exception as e:
            if self.progress_callback:
                self.progress_callback(f"⚠️  Error parsing {file_path.name}: {e}")
            return None

    def parse(self) -> Dict[str, Any]:
        """
        Parse the entire repository with parallel processing.

        Returns:
            Combined parsed data from all files
        """
        self.stats["start_time"] = datetime.now()

        # Find all TypeScript files (excluding node_modules, etc.)
        if self.progress_callback:
            self.progress_callback("🔍 Finding TypeScript files...")

        ts_files = [
            f for f in self.repo_path.rglob("*.ts")
            if not self._is_excluded(f)
        ]

        self.stats["total_files"] = len(ts_files)

        if self.progress_callback:
            self.progress_callback(f"   Found {len(ts_files)} files to parse")

        if len(ts_files) == 0:
            if self.progress_callback:
                self.progress_callback("⚠️  No TypeScript files found!")
            return self._compile_results()

        # Process files in parallel
        if self.progress_callback:
            self.progress_callback(f"   Using {self.max_workers} parallel workers")

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all files
            future_to_file = {
                executor.submit(self._parse_single_file, file_path): file_path
                for file_path in ts_files
            }

            # Process as they complete
            for future in as_completed(future_to_file):
                file_path = future_to_file[future]
                self.stats["processed_files"] += 1

                # Update progress
                if self.progress_callback:
                    self.progress_callback(str(file_path))

                try:
                    result = future.result()

                    if result:
                        # Merge results
                        self.controllers.extend(result.get("controllers", []))
                        self.services.extend(result.get("services", []))
                        self.dtos.extend(result.get("dtos", []))
                        self.entities.extend(result.get("entities", []))
                        self.repositories.extend(result.get("repositories", []))
                        self.graphql_resolvers.extend(result.get("graphql_resolvers", []))
                        self.socket_gateways.extend(result.get("socket_gateways", []))
                        self.bull_processors.extend(result.get("bull_processors", []))
                        self.mongo_schemas.extend(result.get("mongo_schemas", []))
                        self.guards.extend(result.get("guards", []))
                        self.interceptors.extend(result.get("interceptors", []))
                        self.middleware.extend(result.get("middleware", []))
                        self.modules.extend(result.get("modules", []))

                except Exception as e:
                    if self.progress_callback:
                        self.progress_callback(f"❌ Error: {e}")

        self.stats["end_time"] = datetime.now()

        return self._compile_results()

    def _compile_results(self) -> Dict[str, Any]:
        """Compile all parsed results."""
        return {
            "controllers": self.controllers,
            "services": self.services,
            "dtos": self.dtos,
            "entities": self.entities,
            "repositories": self.repositories,
            "graphql_resolvers": self.graphql_resolvers,
            "graphql_mutations": self.graphql_mutations,
            "socket_gateways": self.socket_gateways,
            "bull_processors": self.bull_processors,
            "mongo_schemas": self.mongo_schemas,
            "microservices": self.microservices,
            "guards": self.guards,
            "interceptors": self.interceptors,
            "middleware": self.middleware,
            "modules": self.modules,
        }

    def get_stats(self) -> Dict[str, Any]:
        """Get parsing statistics."""
        stats = self.stats.copy()

        if stats["start_time"] and stats["end_time"]:
            elapsed = (stats["end_time"] - stats["start_time"]).total_seconds()
            stats["elapsed_seconds"] = elapsed

            if stats["processed_files"] > 0:
                stats["files_per_second"] = stats["processed_files"] / elapsed

        return stats

    def clear_cache(self):
        """Clear all cached files."""
        import shutil
        if self.cache_dir.exists():
            shutil.rmtree(self.cache_dir)
            self.cache_dir.mkdir(parents=True, exist_ok=True)
