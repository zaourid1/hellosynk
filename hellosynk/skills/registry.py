"""
Skill Registry - Manages skill discovery, loading, and execution
"""

import importlib
import importlib.util
import pkgutil
from pathlib import Path
from typing import Dict, List, Optional, Type, Any
import json

from hellosynk.skills.base import BaseSkill


class SkillRegistry:
    """Registry for managing HelloSynk skills"""
    
    def __init__(self, skills_dir: Optional[Path] = None):
        if skills_dir is None:
            # Default to user's skills directory
            skills_dir = Path.home() / ".hellosynk" / "skills"
        self.skills_dir = Path(skills_dir)
        self.skills_dir.mkdir(parents=True, exist_ok=True)
        
        self.skills: Dict[str, BaseSkill] = {}
        self.skill_classes: Dict[str, Type[BaseSkill]] = {}
    
    async def load_skills(self):
        """Load all available skills"""
        # Load built-in skills
        self._load_builtin_skills()
        
        # Load user skills
        self._load_user_skills()
    
    def _load_builtin_skills(self):
        """Load built-in skills from the skills package"""
        try:
            import hellosynk.skills as skills_package
            skills_path = Path(skills_package.__file__).parent if hasattr(skills_package, '__file__') else None
            
            if skills_path and skills_path.exists():
                # Import all skill modules
                for _, name, _ in pkgutil.iter_modules([str(skills_path)]):
                    if name.startswith("_") or name in ["base", "registry"]:
                        continue
                    
                    try:
                        module = importlib.import_module(f"hellosynk.skills.{name}")
                        # Look for Skill classes in the module
                        for attr_name in dir(module):
                            attr = getattr(module, attr_name)
                            if (
                                isinstance(attr, type)
                                and issubclass(attr, BaseSkill)
                                and attr != BaseSkill
                            ):
                                self.register_skill(attr)
                    except Exception as e:
                        print(f"Warning: Failed to load skill module '{name}': {e}")
            
            # Also try direct imports for known skills
            try:
                from hellosynk.skills.calendar_skill import CalendarSkill
                self.register_skill(CalendarSkill)
            except ImportError:
                pass
            
            try:
                from hellosynk.skills.email_skill import EmailSkill
                self.register_skill(EmailSkill)
            except ImportError:
                pass
            
            try:
                from hellosynk.skills.notion_skill import NotionSkill
                self.register_skill(NotionSkill)
            except ImportError:
                pass
        except ImportError:
            pass
    
    def _load_user_skills(self):
        """Load user-defined skills from the skills directory"""
        if not self.skills_dir.exists():
            return
        
        # Load skills from Python files
        for skill_file in self.skills_dir.glob("*.py"):
            try:
                spec = importlib.util.spec_from_file_location(
                    skill_file.stem, skill_file
                )
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    # Look for Skill classes
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if (
                            isinstance(attr, type)
                            and issubclass(attr, BaseSkill)
                            and attr != BaseSkill
                        ):
                            self.register_skill(attr)
            except Exception as e:
                print(f"Warning: Failed to load user skill '{skill_file}': {e}")
    
    def register_skill(self, skill_class: Type[BaseSkill]):
        """Register a skill class"""
        if not issubclass(skill_class, BaseSkill):
            raise ValueError(f"{skill_class} is not a subclass of BaseSkill")
        
        # Create instance
        skill = skill_class()
        
        if not skill.name:
            raise ValueError(f"Skill {skill_class} must have a name")
        
        self.skill_classes[skill.name] = skill_class
        self.skills[skill.name] = skill
    
    def get_skill(self, name: str) -> Optional[BaseSkill]:
        """Get a skill by name"""
        return self.skills.get(name)
    
    def get_enabled_skills(self) -> List[BaseSkill]:
        """Get all enabled skills"""
        return [skill for skill in self.skills.values() if skill.enabled]
    
    def get_all_skills(self) -> List[BaseSkill]:
        """Get all skills (enabled and disabled)"""
        return list(self.skills.values())
    
    def enable_skill(self, name: str):
        """Enable a skill"""
        skill = self.skills.get(name)
        if skill:
            skill.enable()
        else:
            raise ValueError(f"Skill '{name}' not found")
    
    def disable_skill(self, name: str):
        """Disable a skill"""
        skill = self.skills.get(name)
        if skill:
            skill.disable()
        else:
            raise ValueError(f"Skill '{name}' not found")
    
    def install_skill(self, skill_path: str):
        """Install a skill from a file path"""
        skill_file = Path(skill_path)
        if not skill_file.exists():
            raise FileNotFoundError(f"Skill file not found: {skill_path}")
        
        # Copy to skills directory
        target_path = self.skills_dir / skill_file.name
        import shutil
        shutil.copy(skill_file, target_path)
        
        # Reload skills
        self._load_user_skills()
    
    def list_skills(self) -> List[Dict[str, Any]]:
        """List all registered skills"""
        return [
            {
                "name": skill.name,
                "description": skill.description,
                "version": skill.version,
                "author": skill.author,
                "enabled": skill.enabled,
            }
            for skill in self.skills.values()
        ]

