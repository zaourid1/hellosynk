"""
Calendar Skill - Manage calendar events
"""

from datetime import datetime, timedelta
from typing import Dict, Any
from hellosynk.skills.base import BaseSkill, SkillParameter


class CalendarSkill(BaseSkill):
    """Skill for managing calendar events"""
    
    name = "calendar"
    description = "Manage calendar events: create, list, and delete events"
    version = "1.0.0"
    author = "HelloSynk Team"
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        # In a real implementation, this would connect to Google Calendar, Outlook, etc.
        self.events = []
    
    def get_parameters(self) -> list[SkillParameter]:
        return [
            SkillParameter(
                name="action",
                type="string",
                description="Action to perform: 'create', 'list', or 'delete'",
                required=True,
            ),
            SkillParameter(
                name="title",
                type="string",
                description="Event title (required for create)",
                required=False,
            ),
            SkillParameter(
                name="start_time",
                type="string",
                description="Start time in ISO format (required for create)",
                required=False,
            ),
            SkillParameter(
                name="duration",
                type="number",
                description="Duration in minutes (default: 60)",
                required=False,
                default=60,
            ),
            SkillParameter(
                name="event_id",
                type="string",
                description="Event ID (required for delete)",
                required=False,
            ),
        ]
    
    async def execute(self, context: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute calendar action"""
        validated_params = self.validate_params(params)
        action = validated_params.get("action")
        
        if action == "create":
            return await self._create_event(validated_params)
        elif action == "list":
            return await self._list_events(validated_params)
        elif action == "delete":
            return await self._delete_event(validated_params)
        else:
            raise ValueError(f"Unknown action: {action}")
    
    async def _create_event(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a calendar event"""
        title = params.get("title")
        start_time_str = params.get("start_time")
        duration = params.get("duration", 60)
        
        if not title or not start_time_str:
            raise ValueError("Title and start_time are required for creating events")
        
        try:
            start_time = datetime.fromisoformat(start_time_str)
        except ValueError:
            raise ValueError(f"Invalid start_time format: {start_time_str}")
        
        end_time = start_time + timedelta(minutes=duration)
        
        event = {
            "id": f"event_{datetime.now().timestamp()}",
            "title": title,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "duration": duration,
        }
        
        self.events.append(event)
        
        return {
            "success": True,
            "event": event,
            "message": f"Created calendar event: {title}",
        }
    
    async def _list_events(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List calendar events"""
        # In a real implementation, this would query the actual calendar service
        return {
            "success": True,
            "events": self.events,
            "count": len(self.events),
        }
    
    async def _delete_event(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a calendar event"""
        event_id = params.get("event_id")
        
        if not event_id:
            raise ValueError("event_id is required for deleting events")
        
        # Find and remove event
        for i, event in enumerate(self.events):
            if event["id"] == event_id:
                removed_event = self.events.pop(i)
                return {
                    "success": True,
                    "event": removed_event,
                    "message": f"Deleted event: {removed_event['title']}",
                }
        
        return {
            "success": False,
            "message": f"Event not found: {event_id}",
        }


