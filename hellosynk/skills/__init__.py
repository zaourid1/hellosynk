"""Skill framework for HelloSynk"""

from hellosynk.skills.base import BaseSkill
from hellosynk.skills.registry import SkillRegistry

# Import built-in skills (they will be auto-loaded by the registry)
try:
    from hellosynk.skills.calendar_skill import CalendarSkill
    from hellosynk.skills.email_skill import EmailSkill
    from hellosynk.skills.notion_skill import NotionSkill
except ImportError:
    pass

__all__ = ["BaseSkill", "SkillRegistry"]
