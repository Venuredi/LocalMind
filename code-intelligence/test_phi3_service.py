"""Test script for Phi3Service."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from llm.phi3_service import Phi3Service


def test_phi3_service():
    """Test Phi3 service functionality."""

    print("=" * 60)
    print("Testing Phi3 Service")
    print("=" * 60)

    # Initialize service
    print("\n1. Initializing Phi3Service...")
    service = Phi3Service()

    # Check availability
    print("\n2. Checking model availability...")
    if service.is_available():
        print("   ✅ Phi3 model is available")
    else:
        print("   ❌ Phi3 model not found")
        return False

    # Get model info
    print("\n3. Getting model information...")
    info = service.get_model_info()
    if info:
        print(f"   Model: {info['name']}")
        print(f"   Size: {info['size'] / (1024**3):.2f} GB")
        print(f"   Parameters: {info['parameter_size']}")
        print(f"   Quantization: {info['quantization']}")
        print(f"   Family: {info['family']}")

    # Test simple generation
    print("\n4. Testing simple generation...")
    try:
        response = service.generate_simple(
            "Say 'Hello from Phi3!' in one sentence",
            max_tokens=50
        )
        print(f"   ✅ Response: {response.strip()}")
    except Exception as e:
        print(f"   ❌ Simple generation failed: {e}")
        return False

    # Test chat generation with system prompt
    print("\n5. Testing chat generation with system prompt...")
    try:
        system_prompt = "You are a helpful coding assistant. Be concise."
        user_prompt = "Explain what a REST API is in one sentence."

        response = service.generate(
            prompt=user_prompt,
            system_prompt=system_prompt,
            max_tokens=100,
            temperature=0.7
        )
        print(f"   ✅ Response: {response.strip()}")
    except Exception as e:
        print(f"   ❌ Chat generation failed: {e}")
        return False

    # Test ontology-guided prompt generation (mock)
    print("\n6. Testing ontology-guided prompt generation...")
    try:
        system_instructions = """You are an ontology-guided code generation assistant.
Rules:
- Only use dependencies that are explicitly provided
- Follow the architecture pattern specified
- Do not invent new methods or classes"""

        ontology_context = """
Available Dependencies:
- IUserRepository (methods: GetById, Create, Update)
- IAuthService (methods: ValidateToken, GenerateToken)

Architecture: Controller -> Service -> Repository
"""

        user_request = "Create a user registration endpoint"

        full_prompt = f"""{ontology_context}

User Request: {user_request}

Generate a brief implementation plan (2-3 bullet points)."""

        response = service.generate(
            prompt=full_prompt,
            system_prompt=system_instructions,
            max_tokens=200,
            temperature=0.7
        )
        print(f"   ✅ Generated plan:\n{response.strip()}")
    except Exception as e:
        print(f"   ❌ Ontology-guided generation failed: {e}")
        return False

    print("\n" + "=" * 60)
    print("✅ All Phi3 Service tests passed!")
    print("=" * 60)

    return True


if __name__ == "__main__":
    success = test_phi3_service()
    sys.exit(0 if success else 1)
