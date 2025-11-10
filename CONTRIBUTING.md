# Contributing to HelloSynk

Thank you for your interest in contributing to HelloSynk! This document provides guidelines and instructions for contributing.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/yourusername/HelloSynk.git`
3. Install in development mode: `pip install -e ".[dev]"`
4. Create a new branch: `git checkout -b feature/your-feature-name`

## Development Setup

```bash
# Install dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black HelloSynk/

# Type checking
mypy HelloSynk/
```

## Creating Skills

Skills are the core extension mechanism in HelloSynk. To create a new skill:

1. Create a new file in `HelloSynk/skills/` or in `~/.HelloSynk/skills/`
2. Inherit from `BaseSkill` and implement the required methods
3. See `examples/create_custom_skill.py` for a template

Example:

```python
from HelloSynk.skills import BaseSkill, SkillParameter

class MySkill(BaseSkill):
    name = "my_skill"
    description = "What this skill does"
    version = "1.0.0"
    author = "Your Name"
    
    def get_parameters(self):
        return [
            SkillParameter(
                name="param1",
                type="string",
                description="Parameter description",
                required=True,
            ),
        ]
    
    async def execute(self, context, params):
        # Your skill logic here
        return {"success": True, "result": "..."}
```

## Code Style

- Follow PEP 8
- Use type hints
- Add docstrings to all classes and functions
- Keep functions focused and small

## Submitting Changes

1. Write tests for your changes
2. Ensure all tests pass: `pytest`
3. Update documentation if needed
4. Commit your changes: `git commit -m "Add feature: description"`
5. Push to your fork: `git push origin feature/your-feature-name`
6. Open a Pull Request

## Skill Marketplace

To publish a skill to the community:

1. Create your skill following the guidelines above
2. Add a README with usage examples
3. Submit a PR to add it to the official skill registry
4. Or host it yourself and share the link!

## Questions?

Open an issue or start a discussion in the GitHub Discussions forum.

Thank you for contributing! 🎉


