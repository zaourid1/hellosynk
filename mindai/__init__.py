"""
MindAI - An open-source, local-first operating system for personal AI agents
"""

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv not installed, skip loading .env file
    pass

from mindai.core.mindai import MindAI
from mindai.core.memory import MemoryNode, MemoryGraph
from mindai.skills import BaseSkill, SkillRegistry

__version__ = "0.1.0"
__all__ = ["MindAI", "MemoryNode", "MemoryGraph", "BaseSkill", "SkillRegistry"]

