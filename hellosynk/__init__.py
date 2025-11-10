"""
HelloSynk - An open-source, local-first operating system for personal AI agents
"""

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    from pathlib import Path
    
    # Get the project root (parent directory of hellosynk package)
    project_root = Path(__file__).parent.parent
    env_file = project_root / ".env"
    
    # Load .env file from project root
    load_dotenv(dotenv_path=env_file)
except ImportError:
    # python-dotenv not installed, skip loading .env file
    pass
except Exception:
    # If .env file doesn't exist or other error, continue without it
    pass

from hellosynk.core.hellosynk import HelloSynk
from hellosynk.core.memory import MemoryNode, MemoryGraph
from hellosynk.skills import BaseSkill, SkillRegistry

__version__ = "0.1.0"
__all__ = ["HelloSynk", "MemoryNode", "MemoryGraph", "BaseSkill", "SkillRegistry"]

