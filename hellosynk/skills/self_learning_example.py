"""
Example usage of the Self-Learning Skill with MIT SEAL framework

This demonstrates how to use the self-learning skill to:
1. Learn from successful interactions
2. Generate self-edits
3. Recall and adapt based on learned patterns
"""

import asyncio
from hellosynk.core.hellosynk import HelloSynk
from hellosynk.skills.self_learning_skill import SelfLearningSkill


async def example_usage():
    """Example of using the self-learning skill"""
    
    # Initialize HelloSynk
    agent = HelloSynk()
    await agent.initialize()
    
    # Get the self-learning skill
    self_learning = agent.skill_registry.get_skill("self_learning")
    
    if not self_learning:
        print("Self-learning skill not found!")
        return
    
    # Example 1: Learn from a successful interaction
    print("=== Example 1: Learning from Success ===")
    result = await self_learning.execute(
        context={
            "query": "Schedule a meeting with John tomorrow at 2pm",
            "memory": agent.memory,
            "user_id": "user123",
        },
        params={
            "action": "learn",
            "pattern": "When user asks to schedule meeting, extract: person, date, time",
            "context": {
                "person": "John",
                "date": "tomorrow",
                "time": "2pm",
            },
            "outcome": "success",
            "feedback": "Successfully created calendar event",
        },
    )
    print(f"Learning result: {result}\n")
    
    # Example 2: Learn from a failure
    print("=== Example 2: Learning from Failure ===")
    result = await self_learning.execute(
        context={
            "query": "Send email to team about project update",
            "memory": agent.memory,
            "user_id": "user123",
        },
        params={
            "action": "learn",
            "pattern": "When user asks to send email, verify recipient list first",
            "context": {
                "recipients": "team",
                "subject": "project update",
            },
            "outcome": "failure",
            "feedback": "Failed: recipient list was empty",
        },
    )
    print(f"Learning result: {result}\n")
    
    # Example 3: Recall learned patterns
    print("=== Example 3: Recalling Patterns ===")
    result = await self_learning.execute(
        context={
            "query": "Schedule a meeting",
            "memory": agent.memory,
            "user_id": "user123",
        },
        params={
            "action": "recall",
            "query": "schedule meeting",
        },
    )
    print(f"Found {result['count']} relevant patterns:")
    for pattern in result["patterns"]:
        print(f"  - {pattern['pattern']} (success rate: {pattern['success_rate']:.2%})")
    print()
    
    # Example 4: Generate self-edits
    print("=== Example 4: Generating Self-Edits ===")
    result = await self_learning.execute(
        context={
            "query": "Generate training data",
            "memory": agent.memory,
            "user_id": "user123",
        },
        params={
            "action": "generate_edits",
        },
    )
    print(f"Generated {result['count']} self-edits")
    if result["self_edits"]:
        print("Sample self-edit:")
        print(f"  Instruction: {result['self_edits'][0]['instruction']}")
        print(f"  Success rate: {result['self_edits'][0]['success_rate']:.2%}")
    print()
    
    # Example 5: Adapt behavior based on learned patterns
    print("=== Example 5: Adapting Behavior ===")
    result = await self_learning.execute(
        context={
            "query": "Schedule a meeting with Sarah next week",
            "memory": agent.memory,
            "user_id": "user123",
        },
        params={
            "action": "adapt",
            "query": "schedule meeting",
        },
    )
    if result["success"]:
        adaptation = result["adaptation"]
        print(f"Recommended pattern: {adaptation['pattern']}")
        print(f"Confidence: {adaptation['confidence']:.2%}")
        print(f"Reasoning: {adaptation['reasoning']}")
    print()
    
    # Example 6: Evaluate patterns
    print("=== Example 6: Evaluating Patterns ===")
    result = await self_learning.execute(
        context={
            "query": "Evaluate learning",
            "memory": agent.memory,
            "user_id": "user123",
        },
        params={
            "action": "evaluate",
        },
    )
    print(f"Total patterns: {result['total_patterns']}")
    print("Top patterns:")
    for pattern in result["top_patterns"][:3]:
        print(f"  - {pattern['pattern']} (quality: {pattern['quality_score']:.2f})")
    print()
    
    # Get learning statistics
    print("=== Learning Statistics ===")
    stats = self_learning.get_learning_stats()
    print(f"Total patterns learned: {stats['total_patterns']}")
    print(f"Overall success rate: {stats['overall_success_rate']:.2%}")
    print(f"Total self-edits: {stats['total_self_edits']}")
    
    # Save memory
    await agent.storage.save_memory_graph(agent.memory)


if __name__ == "__main__":
    asyncio.run(example_usage())

