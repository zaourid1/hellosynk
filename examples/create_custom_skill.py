"""
Example: Creating a Custom Skill
"""

from mindai.skills import BaseSkill, SkillParameter
from typing import Dict, Any


class WeatherSkill(BaseSkill):
    """A custom skill for getting weather information"""
    
    name = "weather"
    description = "Get current weather information for a location"
    version = "1.0.0"
    author = "Your Name"
    
    def get_parameters(self) -> list[SkillParameter]:
        return [
            SkillParameter(
                name="location",
                type="string",
                description="City or location name",
                required=True,
            ),
            SkillParameter(
                name="units",
                type="string",
                description="Temperature units: 'celsius' or 'fahrenheit'",
                required=False,
                default="celsius",
            ),
        ]
    
    async def execute(self, context: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the weather skill"""
        validated_params = self.validate_params(params)
        location = validated_params["location"]
        units = validated_params.get("units", "celsius")
        
        # In a real implementation, you would call a weather API here
        # For this example, we'll return mock data
        return {
            "success": True,
            "location": location,
            "temperature": 22 if units == "celsius" else 72,
            "units": units,
            "condition": "sunny",
            "humidity": 65,
            "message": f"Weather in {location}: 22°C, sunny",
        }


# To use this skill, save it to ~/.mindai/skills/weather_skill.py
# Then restart MindAI - it will automatically discover and load the skill


