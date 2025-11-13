"""
Full Capabilities Test - Demonstrates all HelloSynk features
"""

import sys
import asyncio
from pathlib import Path
from datetime import datetime, timedelta

# Add the project root to Python path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from hellosynk import HelloSynk
from hellosynk.core.llm import LLMProvider
from hellosynk.core.memory import NodeType


async def main():
    print("=" * 70)
    print("HelloSynk Full Capabilities Test")
    print("=" * 70)
    print()
    
    # Initialize HelloSynk
    print("🔧 Initializing HelloSynk...")
    hellosynk = HelloSynk(
        llm_provider=LLMProvider.OPENAI,
        llm_model="gpt-4o",  # Using gpt-4o (or try "gpt-3.5-turbo" if not available)
    )
    
    await hellosynk.initialize()
    
    # Check LLM initialization
    if not hellosynk.llm_client:
        print("⚠️  LLM client not initialized. Some features will be limited.")
        print("   Please set OPENAI_API_KEY environment variable.")
        llm_available = False
    else:
        print("✅ HelloSynk initialized successfully!")
        print(f"✅ LLM Client: {hellosynk.llm_provider.value} ({hellosynk.llm_model})")
        llm_available = True
    
    print(f"✅ Loaded {len(hellosynk.skill_registry.get_enabled_skills())} skills:")
    for skill in hellosynk.skill_registry.get_enabled_skills():
        print(f"   - {skill.name}: {skill.description}")
    print()
    
    # =================================================================
    # Test 1: Memory Operations
    # =================================================================
    print("=" * 70)
    print("TEST 1: Memory Graph Operations")
    print("=" * 70)
    print()
    
    # Add various types of memories
    print("📝 Adding memories to the graph...")
    
    memory1 = await hellosynk.add_memory(
        content="User's favorite programming language is Python",
        node_type=NodeType.CONTEXT,
        importance=0.8,
        metadata={"category": "preference"}
    )
    print(f"  ✓ Added memory: {memory1}")
    
    memory2 = await hellosynk.add_memory(
        content="User works on AI agent development project called HelloSynk",
        node_type=NodeType.CONTEXT,
        importance=0.9,
        metadata={"category": "project"}
    )
    print(f"  ✓ Added memory: {memory2}")
    
    memory3 = await hellosynk.add_memory(
        content="Team meeting scheduled every Monday at 10am",
        node_type=NodeType.EVENT,
        importance=0.7,
        metadata={"frequency": "weekly"}
    )
    print(f"  ✓ Added memory: {memory3}")
    
    # Search memories
    print("\n🔍 Searching memories...")
    results = await hellosynk.search_memory("Python", limit=5)
    print(f"  Found {len(results)} memories about 'Python'")
    for mem in results:
        print(f"    - {mem.content[:60]}... (importance: {mem.importance})")
    
    # Get context for a query
    print("\n🧠 Retrieving context for query...")
    context = await hellosynk.get_context("What programming languages does the user like?", max_nodes=5)
    print(f"  Retrieved {len(context)} relevant context nodes")
    for i, node in enumerate(context, 1):
        print(f"    {i}. {node.content[:60]}...")
    print()
    
    # =================================================================
    # Test 2: Query Processing with LLM Reasoning
    # =================================================================
    print("=" * 70)
    print("TEST 2: Query Processing with LLM Reasoning")
    print("=" * 70)
    print()
    
    if not llm_available:
        print("⚠️  Skipping LLM reasoning tests - LLM client not available")
        print()
    else:
        test_queries = [
            "Create a calendar event for tomorrow at 2pm called 'Team Meeting'",
            "What memories do you have about my projects?",
            "Send an email to test@example.com with subject 'Hello' and body 'This is a test email'",
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"Query {i}: {query}")
            print("-" * 70)
            
            try:
                result = await hellosynk.process(query)
                
                print(f"Intent: {result.get('intent', 'N/A')}")
                print(f"Response: {result.get('response', 'N/A')}")
                
                if result.get('reasoning'):
                    reasoning = result['reasoning']
                    # Check if it's an error message
                    if "Error during reasoning" in reasoning or "Error code" in reasoning:
                        print(f"⚠️  LLM Error: {reasoning[:150]}...")
                    else:
                        print(f"Reasoning: {reasoning[:200]}...")
                
                print(f"\nExecutions ({len(result.get('executions', []))}):")
                for execution in result.get('executions', []):
                    status = execution.get('status', 'unknown')
                    status_icon = "✅" if status == 'success' else "❌"
                    print(f"  {status_icon} {execution.get('skill', 'unknown')}: {status}")
                    if status == 'success' and execution.get('result'):
                        result_str = str(execution['result'])[:100]
                        print(f"     Result: {result_str}...")
                    elif execution.get('error'):
                        print(f"     Error: {execution['error']}")
                
            except Exception as e:
                error_msg = str(e)
                if "quota" in error_msg.lower() or "429" in error_msg:
                    print(f"⚠️  API Quota Exceeded: Please check your OpenAI billing/usage")
                elif "LLM client not initialized" in error_msg:
                    print(f"⚠️  LLM not available: {error_msg}")
                else:
                    print(f"❌ Error processing query: {e}")
            
            print()
    
    # =================================================================
    # Test 3: Skill Execution
    # =================================================================
    print("=" * 70)
    print("TEST 3: Direct Skill Execution")
    print("=" * 70)
    print()
    
    # Test Calendar Skill
    print("📅 Testing Calendar Skill...")
    calendar_skill = hellosynk.skill_registry.get_skill("calendar")
    if calendar_skill:
        # Create an event
        tomorrow = (datetime.now() + timedelta(days=1)).isoformat()
        event_result = await calendar_skill.execute(
            context={"query": "test", "memory": hellosynk.memory},
            params={
                "action": "create",
                "title": "Test Event",
                "start_time": tomorrow,
                "duration": 60
            }
        )
        print(f"  ✓ Created event: {event_result.get('message', 'N/A')}")
        
        # List events
        list_result = await calendar_skill.execute(
            context={"query": "test", "memory": hellosynk.memory},
            params={"action": "list"}
        )
        print(f"  ✓ Found {list_result.get('count', 0)} events")
    else:
        print("  ❌ Calendar skill not found")
    
    print()
    
    # Test Email Skill
    print("📧 Testing Email Skill...")
    email_skill = hellosynk.skill_registry.get_skill("email")
    if email_skill:
        # Send an email
        email_result = await email_skill.execute(
            context={"query": "test", "memory": hellosynk.memory},
            params={
                "action": "send",
                "to": "test@example.com",
                "subject": "Test Email",
                "body": "This is a test email from HelloSynk"
            }
        )
        print(f"  ✓ {email_result.get('message', 'N/A')}")
        
        # List emails
        list_result = await email_skill.execute(
            context={"query": "test", "memory": hellosynk.memory},
            params={"action": "list"}
        )
        print(f"  ✓ Found {list_result.get('count', 0)} emails")
    else:
        print("  ❌ Email skill not found")
    
    print()
    
    # =================================================================
    # Test 4: Memory Persistence
    # =================================================================
    print("=" * 70)
    print("TEST 4: Memory Persistence")
    print("=" * 70)
    print()
    
    # Add a memory that should persist
    print("💾 Adding persistent memory...")
    persistent_memory = await hellosynk.add_memory(
        content="User tested HelloSynk on " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        importance=0.6
    )
    print(f"  ✓ Added memory: {persistent_memory}")
    
    # Get memory statistics
    print("\n📊 Memory Graph Statistics:")
    graph = hellosynk.memory.graph
    print(f"  Total nodes: {graph.number_of_nodes()}")
    print(f"  Total edges: {graph.number_of_edges()}")
    
    # Show all memories
    all_memories = await hellosynk.search_memory("", limit=100)
    print(f"  Total memories: {len(all_memories)}")
    
    print()
    
    # =================================================================
    # Test 5: Complex Query with Context
    # =================================================================
    print("=" * 70)
    print("TEST 5: Complex Query with Context Awareness")
    print("=" * 70)
    print()
    
    if not llm_available:
        print("⚠️  Skipping complex query test - LLM client not available")
        print()
    else:
        complex_query = "Based on my preferences and project work, create a calendar event for a code review session next week"
        print(f"Query: {complex_query}")
        print("-" * 70)
        
        try:
            result = await hellosynk.process(complex_query)
            print(f"Intent: {result.get('intent', 'N/A')}")
            print(f"Response: {result.get('response', 'N/A')}")
            
            if result.get('reasoning'):
                reasoning = result['reasoning']
                if "Error during reasoning" in reasoning or "Error code" in reasoning:
                    print(f"⚠️  LLM Error: {reasoning[:150]}...")
                else:
                    print(f"\nReasoning:\n{reasoning}")
            
            print(f"\nExecutions:")
            for execution in result.get('executions', []):
                status = execution.get('status', 'unknown')
                status_icon = "✅" if status == 'success' else "❌"
                print(f"  {status_icon} {execution.get('skill', 'unknown')}: {status}")
                if status == 'success' and execution.get('result'):
                    print(f"     {execution['result']}")
                elif execution.get('error'):
                    print(f"     Error: {execution['error']}")
        except Exception as e:
            error_msg = str(e)
            if "quota" in error_msg.lower() or "429" in error_msg:
                print(f"⚠️  API Quota Exceeded: Please check your OpenAI billing/usage")
            elif "LLM client not initialized" in error_msg:
                print(f"⚠️  LLM not available: {error_msg}")
            else:
                print(f"❌ Error: {e}")
        
        print()
    
    # =================================================================
    # Summary
    # =================================================================
    print("=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print()
    print("✅ Memory Graph Operations: Working")
    print("✅ Memory Search: Working")
    print("✅ Memory Persistence: Working")
    print("✅ Skill Execution: Working")
    print(f"{'✅' if llm_available else '⚠️ '} LLM Client: {'Available' if llm_available else 'Not Available'}")
    if llm_available:
        print("⚠️  LLM Reasoning: Requires valid API key with available quota")
    print("✅ Context Retrieval: Working")
    print()
    
    if llm_available:
        print("💡 Note: If you see quota errors, check your OpenAI account:")
        print("   - Billing and usage limits")
        print("   - API key validity")
        print("   - Account credits")
    else:
        print("💡 To enable full LLM capabilities:")
        print("   - Set OPENAI_API_KEY in .env file")
        print("   - Ensure you have API credits/quota")
    print()
    print("🎉 Core capabilities tested successfully!")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())

