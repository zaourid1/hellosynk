"""
Basic Usage Example - How to use MindAI
"""

import sys
from pathlib import Path

# Add the project root to Python path so we can import mindai
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import asyncio
from hellosynk import HelloSynk
from hellosynk.core.llm import LLMProvider


async def main():
    # Initialize MindAI
    # Make sure to set your API key in environment variable or via config
    hellosynk = HelloSynk(
        llm_provider=LLMProvider.OPENAI,
        llm_model="gpt-4",
        # llm_api_key="your-api-key-here"  # Or set OPENAI_API_KEY env var
    )
    
    # Initialize the system (loads memory, skills, etc.)
    await hellosynk.initialize()
    
    # Check if LLM client is initialized
    if not hellosynk.llm_client:
        print("⚠️  LLM client not initialized. API key required for processing queries.")
        print("   To fix: Set OPENAI_API_KEY environment variable or pass llm_api_key parameter.")
        print("\n   Demonstrating memory functionality (doesn't require LLM)...\n")
    else:
        # Process a query (only if LLM client is available)
        print("Processing query...\n")
        result = await hellosynk.process("Create a calendar event for tomorrow at 2pm called 'Team Meeting'")
        
        print("Query:", result["query"])
        print("Response:", result["response"])
        print("Intent:", result["intent"])
        print("\nExecutions:")
        for execution in result["executions"]:
            print(f"  - {execution['skill']}: {execution['status']}")
            if execution["status"] == "success":
                print(f"    Result: {execution['result']}")
        print()
    
    # Add a memory manually (works without LLM)
    print("Adding memory...")
    memory_id = await hellosynk.add_memory(
        content="User prefers meetings in the afternoon",
        importance=0.7,
    )
    print(f"✓ Added memory: {memory_id}\n")
    
    # Add another memory
    memory_id2 = await hellosynk.add_memory(
        content="Team meeting scheduled for tomorrow at 2pm",
        importance=0.8,
    )
    print(f"✓ Added memory: {memory_id2}\n")
    
    # Search memory (works without LLM)
    print("Searching memory...")
    results = await hellosynk.search_memory("meeting", limit=5)
    print(f"✓ Found {len(results)} memories about meetings")
    for i, mem in enumerate(results, 1):
        print(f"  {i}. {mem.content} (importance: {mem.importance})")


if __name__ == "__main__":
    asyncio.run(main())


