"""Skill framework for MindAI"""

from mindai.skills.base import BaseSkill
from mindai.skills.registry import SkillRegistry

# Import built-in skills (they will be auto-loaded by the registry)
try:
    from mindai.skills.calendar_skill import CalendarSkill
    from mindai.skills.email_skill import EmailSkill
    from mindai.skills.notion_skill import NotionSkill
except ImportError:
    pass

__all__ = ["BaseSkill", "SkillRegistry"]
