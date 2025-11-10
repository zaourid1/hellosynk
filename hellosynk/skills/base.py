"""
Base Skill Class - Foundation for all HelloSynk skills
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field


class SkillParameter(BaseModel):
    """Definition of a skill parameter"""
    name: str
    type: str  # "string", "number", "boolean", "object", "array"
    description: str
    required: bool = False
    default: Optional[Any] = None


class BaseSkill(ABC):
    """Base class for all HelloSynk skills"""
    
    # Skill metadata (must be overridden)
    name: str = ""
    description: str = ""
    version: str = "1.0.0"
    author: str = ""
    
    # Skill configuration
    enabled: bool = True
    config: Dict[str, Any] = {}
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the skill"""
        if config:
            self.config.update(config)
    
    @abstractmethod
    async def execute(
        self,
        context: Dict[str, Any],
        params: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Execute the skill
        
        Args:
            context: Context dictionary containing:
                - query: The user's query
                - memory: MemoryGraph instance
                - user_id: Optional user identifier
            params: Parameters for the skill execution
        
        Returns:
            Dictionary with execution results
        """
        pass
    
    def get_parameters(self) -> List[SkillParameter]:
        """
        Get the list of parameters this skill accepts
        
        Override this method to define skill parameters
        """
        return []
    
    def validate_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and sanitize parameters"""
        parameter_defs = {p.name: p for p in self.get_parameters()}
        validated = {}
        
        for param_def in parameter_defs.values():
            if param_def.name in params:
                validated[param_def.name] = params[param_def.name]
            elif param_def.required:
                if param_def.default is not None:
                    validated[param_def.name] = param_def.default
                else:
                    raise ValueError(f"Required parameter '{param_def.name}' is missing")
            elif param_def.default is not None:
                validated[param_def.name] = param_def.default
        
        return validated
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """Get a configuration value"""
        return self.config.get(key, default)
    
    def set_config(self, key: str, value: Any):
        """Set a configuration value"""
        self.config[key] = value
    
    def enable(self):
        """Enable the skill"""
        self.enabled = True
    
    def disable(self):
        """Disable the skill"""
        self.enabled = False
    
    def __repr__(self) -> str:
        return f"<Skill: {self.name} v{self.version}>"


