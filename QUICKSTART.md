# Quick Start Guide

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/zaourid1/hellosynk.git
   cd HelloSynk
   ```

2. **Install dependencies**
   ```bash
   pip install -e .
   ```

3. **Set up your API key**
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   # Or for Anthropic:
   export ANTHROPIC_API_KEY="your-api-key-here"
   ```

## Basic Usage

### Using the CLI

```bash
# Process a query
HelloSynk chat "Create a calendar event for tomorrow at 2pm"

# List installed skills
HelloSynk skill list

# Enable/disable skills
HelloSynk skill enable calendar
HelloSynk skill disable email

# Search memory
HelloSynk memory search "meeting"

# Add a memory
HelloSynk memory add "User prefers morning meetings" --type context

# Configure LLM
HelloSynk config set-llm --provider openai --model gpt-4 --api-key your-key
```

### Using the Python API

```python
import asyncio
from HelloSynk import HelloSynk
from HelloSynk.core.llm import LLMProvider

async def main():
    # Initialize HelloSynk
    agent = HelloSynk(
        llm_provider=LLMProvider.OPENAI,
        llm_model="gpt-4"
    )
    await agent.initialize()
    
    # Process a query
    result = await agent.process("Send an email to john@example.com about the meeting")
    print(result["response"])
    
    # Add memory
    await agent.add_memory("John is the project manager")
    
    # Search memory
    memories = await agent.search_memory("John")
    for memory in memories:
        print(memory.content)

asyncio.run(main())
```

## Creating Your First Skill

1. **Create a skill file** (`~/.HelloSynk/skills/my_skill.py`):

```python
from HelloSynk.skills import BaseSkill, SkillParameter

class MySkill(BaseSkill):
    name = "my_skill"
    description = "Does something useful"
    version = "1.0.0"
    author = "Your Name"
    
    def get_parameters(self):
        return [
            SkillParameter(
                name="input",
                type="string",
                description="Input parameter",
                required=True,
            ),
        ]
    
    async def execute(self, context, params):
        return {
            "success": True,
            "result": f"Processed: {params['input']}"
        }
```

2. **Restart HelloSynk** - your skill will be automatically discovered and loaded.

3. **Use your skill**:
   ```bash
   HelloSynk chat "Use my_skill with input 'test'"
   ```

## Next Steps

- Read the [Architecture Documentation](docs/ARCHITECTURE.md)
- Check out [Example Skills](examples/)
- Read [Contributing Guidelines](CONTRIBUTING.md)
- Explore the [API Documentation](docs/API.md) (coming soon)

## Troubleshooting

### LLM not initialized
Make sure you've set your API key:
```bash
export OPENAI_API_KEY="your-key"
# Or configure via CLI
HelloSynk config set-llm --provider openai --api-key your-key
```

### Skills not loading
- Check that skill files are in `~/.HelloSynk/skills/`
- Ensure skills inherit from `BaseSkill`
- Check for import errors in skill files

### Memory not persisting
- Check that `~/.HelloSynk/` directory exists and is writable
- Verify database file `~/.HelloSynk/HelloSynk.db` is being created

## Need Help?

- Open an issue on GitHub
- Check the documentation
- Join our community discussions


