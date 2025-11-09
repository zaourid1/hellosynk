# MindAI

> An open-source, local-first operating system for personal AI agents

MindAI is a lightweight layer that gives any LLM persistent memory, reasoning, and the ability to take actions across apps. It runs on-device, stores context in a structured memory graph, and executes "skills" — small modular scripts that connect to services like email, Notion, or calendar.

## Features

- 🧠 **Persistent Memory Graph**: Structured memory system that maintains context across sessions
- 🤖 **Reasoning Engine**: Advanced reasoning capabilities for LLM agents
- 🔌 **Skill System**: Modular, extensible skills that connect to any service
- 💾 **Local-First**: All data stored locally, privacy-focused
- 🛠️ **Developer-Friendly**: Easy-to-use framework for building and publishing skills
- 🏪 **Skill Marketplace**: Discover and install skills from the community

## Architecture

```
mindai/
├── core/           # Core system components
│   ├── memory/     # Memory graph system
│   ├── llm/        # LLM integration layer
│   └── storage/    # Local storage engine
├── skills/         # Skill framework and registry
├── api/            # API layer (optional)
├── cli/            # Command-line interface
└── examples/       # Example skills
```

## Quick Start

### Installation

```bash
pip install -e .
```

### Basic Usage

```python
from mindai import MindAI
from mindai.skills import SkillRegistry

# Initialize MindAI
agent = MindAI()

# Load skills
registry = SkillRegistry()
registry.load_skills()

# Use the agent
response = agent.process("Check my calendar for tomorrow")
```

### Creating a Skill

```python
from mindai.skills import BaseSkill

class MySkill(BaseSkill):
    name = "my_skill"
    description = "Description of what this skill does"
    
    def execute(self, context, params):
        # Your skill logic here
        return {"result": "success"}
```

## Development

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run CLI
mindai --help
```

## Skills Marketplace

Browse and install skills from the community:

```bash
mindai skill search email
mindai skill install email-manager
```

## License

MIT License - see LICENSE file for details

