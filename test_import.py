#!/usr/bin/env python3
"""Simple test to verify mindai can be imported"""

import sys

print(f"Python version: {sys.version}")
print(f"Python executable: {sys.executable}")
print(f"Python path: {sys.path[:3]}...")  # First 3 entries

try:
    import mindai
    print("✅ Successfully imported mindai")
    print(f"✅ MindAI location: {mindai.__file__}")
    
    from mindai import MindAI
    print("✅ Successfully imported MindAI class")
    
    from mindai.core.llm import LLMProvider
    print("✅ Successfully imported LLMProvider")
    
    print("\n✅ All imports successful! The module is working correctly.")
    print("\nNote: You still need to set your API key to run the full example.")
    print("   You can do this by:")
    print("   1. Creating a .env file with OPENAI_API_KEY=your-key")
    print("   2. Or exporting: export OPENAI_API_KEY='your-key'")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("\nTroubleshooting:")
    print("1. Make sure you've installed the package: pip install -e .")
    print("2. Make sure you're using the same Python that has mindai installed")
    print("3. Try: python3 -m pip install -e .")
    sys.exit(1)

