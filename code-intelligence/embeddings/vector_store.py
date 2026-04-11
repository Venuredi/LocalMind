"""
Vector Store using ChromaDB
Provides semantic search capabilities for code components.
"""

import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional
from pathlib import Path
import json
import hashlib


class VectorStore:
    """
    Vector store for semantic code search using ChromaDB.

    Features:
    - Semantic search across all code components
    - Multi-language support
    - Persistent storage
    """

    def __init__(self, persist_directory: str = "./data/chroma"):
        """Initialize the vector store."""
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)

        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True,
            )
        )

        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name="code_components",
            metadata={"hnsw:space": "cosine"}
        )

    def index_components(self, components: List[Dict[str, Any]]):
        """
        Index code components for semantic search.

        Args:
            components: List of component dictionaries from unified index
        """
        print(f"📚 Indexing {len(components)} components...")

        documents = []
        metadatas = []
        ids = []
        seen_ids: set = set()

        for i, component in enumerate(components):
            # Build a stable, non-empty string ID
            raw_id = component.get("id") or component.get("name")
            if raw_id:
                comp_id = str(raw_id)
            else:
                # Fallback: hash file path + index so it stays deterministic
                seed = f"{component.get('file_path', '')}::{i}"
                comp_id = "comp_" + hashlib.md5(seed.encode()).hexdigest()[:12]

            # Deduplicate: ChromaDB upsert tolerates duplicates but it's
            # cleaner to skip true duplicates within the same batch
            if comp_id in seen_ids:
                comp_id = f"{comp_id}__{i}"
            seen_ids.add(comp_id)

            # Create searchable text
            doc_text = self._create_document_text(component)

            # Metadata — all values must be primitive types (str/int/float/bool).
            # Use empty string instead of None to avoid ChromaDB rejection.
            metadata = {
                "name": str(component.get("name") or ""),
                "type": str(component.get("type") or ""),
                "layer": str(component.get("layer") or ""),
                "file_path": str(component.get("file_path") or ""),
                "description": str(component.get("description") or ""),
            }

            documents.append(doc_text)
            metadatas.append(metadata)
            ids.append(comp_id)

        # Add to ChromaDB (batched)
        batch_size = 100
        for i in range(0, len(documents), batch_size):
            batch_docs = documents[i:i + batch_size]
            batch_metas = metadatas[i:i + batch_size]
            batch_ids = ids[i:i + batch_size]

            self.collection.upsert(
                documents=batch_docs,
                metadatas=batch_metas,
                ids=batch_ids
            )

        print(f"✅ Indexed {len(components)} components")

    def _create_document_text(self, component: Dict[str, Any]) -> str:
        """Create searchable text from component."""
        parts = []

        # Name
        parts.append(component.get("name", ""))

        # Type
        parts.append(component.get("type", ""))

        # Layer
        parts.append(component.get("layer", ""))

        # Description
        if component.get("description"):
            parts.append(component["description"])

        # File path (for context)
        parts.append(component.get("file_path", ""))

        # Metadata
        metadata = component.get("metadata", {})

        # Add routes for controllers
        if metadata.get("routes"):
            for route in metadata["routes"]:
                parts.append(f"{route.get('method', '')} {route.get('path', '')}")

        # Add methods for services
        if metadata.get("methods"):
            for method in metadata["methods"]:
                parts.append(method.get("name", ""))

        # Add API calls
        if metadata.get("api_calls"):
            for api_call in metadata["api_calls"]:
                parts.append(f"{api_call.get('method', '')} {api_call.get('endpoint', '')}")

        return " ".join(filter(None, parts))

    def search(
        self,
        query: str,
        n_results: int = 10,
        layer_filter: Optional[str] = None,
        type_filter: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Semantic search for components.

        Args:
            query: Search query
            n_results: Number of results to return
            layer_filter: Filter by layer (e.g., "backend")
            type_filter: Filter by type (e.g., "controller")

        Returns:
            List of matching components with scores
        """
        where_filter = {}

        if layer_filter:
            where_filter["layer"] = layer_filter

        if type_filter:
            where_filter["type"] = type_filter

        # Search
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where_filter if where_filter else None,
        )

        # Format results
        formatted_results = []

        if results and results["ids"]:
            for i, comp_id in enumerate(results["ids"][0]):
                formatted_results.append({
                    "id": comp_id,
                    "score": 1 - results["distances"][0][i],  # Convert distance to similarity
                    "metadata": results["metadatas"][0][i],
                    "document": results["documents"][0][i],
                })

        return formatted_results

    def get_similar_components(
        self,
        component_id: str,
        n_results: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Find components similar to a given component.

        Args:
            component_id: Component ID to find similar items for
            n_results: Number of results

        Returns:
            List of similar components
        """
        # Get the component's document
        component = self.collection.get(ids=[component_id])

        if not component["documents"]:
            return []

        # Search for similar
        return self.search(component["documents"][0], n_results=n_results + 1)[1:]  # Exclude self

    def clear(self):
        """Clear all indexed data."""
        self.client.delete_collection("code_components")
        self.collection = self.client.get_or_create_collection(
            name="code_components",
            metadata={"hnsw:space": "cosine"}
        )

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store."""
        count = self.collection.count()

        return {
            "total_components": count,
            "persist_directory": str(self.persist_directory),
        }


def main():
    """CLI for vector store operations."""
    import argparse

    parser = argparse.ArgumentParser(description="Vector Store Operations")
    parser.add_argument("--index", help="Path to index JSON file")
    parser.add_argument("--search", help="Search query")
    parser.add_argument("--limit", type=int, default=10, help="Number of results")

    args = parser.parse_args()

    vector_store = VectorStore()

    if args.index:
        # Load and index
        with open(args.index, "r") as f:
            index_data = json.load(f)

        components = index_data.get("components", [])
        vector_store.index_components(components)

    if args.search:
        # Search
        results = vector_store.search(args.search, n_results=args.limit)

        print(f"\n🔍 Search results for: '{args.search}'\n")

        for i, result in enumerate(results, 1):
            meta = result["metadata"]
            print(f"{i}. {meta['name']} ({meta['type']})")
            print(f"   Layer: {meta['layer']}")
            print(f"   Score: {result['score']:.3f}")
            print(f"   File: {meta['file_path']}")
            print()


if __name__ == "__main__":
    main()
