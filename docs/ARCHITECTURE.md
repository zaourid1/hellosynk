# MindAI Architecture

## Overview

MindAI is built on a modular architecture with the following core components:

## Core Components

### 1. Memory Graph (`mindai.core.memory`)

The memory graph is a structured knowledge representation system that stores:
- **Nodes**: Entities, events, concepts, tasks, and context
- **Edges**: Relationships between nodes (related_to, part_of, caused_by, etc.)

The graph uses NetworkX for graph operations and supports:
- Node creation and retrieval
- Relationship management
- Context retrieval based on queries
- Node merging and deduplication

### 2. Storage Engine (`mindai.core.storage`)

The storage engine provides persistent storage using:
- **SQLite**: For structured data (skills, executions)
- **JSON**: For memory graph backups
- **File System**: For configuration and skill files

All data is stored locally in `~/.mindai/` by default.

### 3. LLM Integration (`mindai.core.llm`)

The LLM layer supports multiple providers:
- **OpenAI**: GPT-4, GPT-3.5, etc.
- **Anthropic**: Claude models
- **Local**: (Future) Local model support

The LLM is used for:
- Reasoning about user queries
- Determining which skills to execute
- Extracting parameters from natural language

### 4. Skill Framework (`mindai.skills`)

Skills are modular, executable components that:
- Inherit from `BaseSkill`
- Define parameters they accept
- Execute actions (email, calendar, etc.)
- Return structured results

Skills can be:
- Built-in (shipped with MindAI)
- User-defined (in `~/.mindai/skills/`)
- Community-published (future marketplace)

### 5. Skill Registry (`mindai.skills.registry`)

The registry manages:
- Skill discovery and loading
- Skill enable/disable
- Skill installation
- Skill metadata

### 6. Main Agent (`mindai.core.mindai`)

The `MindAI` class orchestrates everything:
- Initializes storage and memory
- Loads skills
- Processes user queries
- Coordinates LLM reasoning and skill execution
- Updates memory based on interactions

## Data Flow

1. **User Query** → `MindAI.process()`
2. **Context Retrieval** → Memory graph searches for relevant context
3. **Reasoning** → LLM analyzes query and determines actions
4. **Skill Execution** → Relevant skills are executed with parameters
5. **Memory Update** → Results are stored in the memory graph
6. **Response** → User receives natural language response

## Extension Points

### Creating Skills

1. Inherit from `BaseSkill`
2. Define `name`, `description`, `version`, `author`
3. Implement `get_parameters()` to define inputs
4. Implement `execute()` to perform actions
5. Save to `~/.mindai/skills/` or submit as PR

### Adding LLM Providers

1. Add provider to `LLMProvider` enum
2. Implement provider-specific logic in `LLMClient`
3. Add API key handling
4. Test with various models

### Custom Storage

The storage engine can be extended to support:
- Remote storage (with encryption)
- Different database backends
- Cloud sync (future)

## Security Considerations

- All data stored locally by default
- API keys stored in configuration (not committed)
- Skills run in the same process (sandboxing future work)
- Memory graph can be encrypted (future)

## Performance

- Memory graph uses efficient graph algorithms
- SQLite for fast local queries
- Async/await for non-blocking operations
- Lazy loading of skills and memory

## Future Enhancements

- Skill marketplace with discovery
- Local LLM support (Ollama, etc.)
- Multi-user support
- Skill sandboxing
- Memory graph encryption
- Cloud sync (optional)
- Web UI
- API server mode


