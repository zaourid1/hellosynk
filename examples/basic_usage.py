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
from mindai import MindAI
from mindai.core.llm import LLMProvider


async def main():
    # Initialize MindAI
    # Make sure to set your API key in environment variable or via config
    mindai = MindAI(
        llm_provider=LLMProvider.OPENAI,
        llm_model="gpt-4",
        # llm_api_key="your-api-key-here"  # Or set OPENAI_API_KEY env var
    )
    
    # Initialize the system (loads memory, skills, etc.)
    await mindai.initialize()
    
    # Process a query
    result = await mindai.process("Create a calendar event for tomorrow at 2pm called 'Team Meeting'")
    
    print("Query:", result["query"])
    print("Response:", result["response"])
    print("Intent:", result["intent"])
    print("\nExecutions:")
    for execution in result["executions"]:
        print(f"  - {execution['skill']}: {execution['status']}")
        if execution["status"] == "success":
            print(f"    Result: {execution['result']}")
    
    # Add a memory manually
    memory_id = await mindai.add_memory(
        content="User prefers meetings in the afternoon",
        importance=0.7,
    )
    print(f"\nAdded memory: {memory_id}")
    
    # Search memory
    results = await mindai.search_memory("meeting", limit=5)
    print(f"\nFound {len(results)} memories about meetings")


if __name__ == "__main__":
    asyncio.run(main())


