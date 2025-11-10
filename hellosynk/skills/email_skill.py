"""
Email Skill - Manage email
"""

from typing import Dict, Any
from hellosynk.skills.base import BaseSkill, SkillParameter


class EmailSkill(BaseSkill):
    """Skill for managing email"""
    
    name = "email"
    description = "Send and manage emails: send, list, and search emails"
    version = "1.0.0"
    author = "HelloSynk Team"
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        # In a real implementation, this would connect to Gmail, Outlook, etc.
        self.sent_emails = []
    
    def get_parameters(self) -> list[SkillParameter]:
        return [
            SkillParameter(
                name="action",
                type="string",
                description="Action to perform: 'send', 'list', or 'search'",
                required=True,
            ),
            SkillParameter(
                name="to",
                type="string",
                description="Recipient email address (required for send)",
                required=False,
            ),
            SkillParameter(
                name="subject",
                type="string",
                description="Email subject (required for send)",
                required=False,
            ),
            SkillParameter(
                name="body",
                type="string",
                description="Email body (required for send)",
                required=False,
            ),
            SkillParameter(
                name="query",
                type="string",
                description="Search query (for search action)",
                required=False,
            ),
        ]
    
    async def execute(self, context: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute email action"""
        validated_params = self.validate_params(params)
        action = validated_params.get("action")
        
        if action == "send":
            return await self._send_email(validated_params)
        elif action == "list":
            return await self._list_emails(validated_params)
        elif action == "search":
            return await self._search_emails(validated_params)
        else:
            raise ValueError(f"Unknown action: {action}")
    
    async def _send_email(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Send an email"""
        to = params.get("to")
        subject = params.get("subject")
        body = params.get("body")
        
        if not to or not subject or not body:
            raise ValueError("to, subject, and body are required for sending emails")
        
        email = {
            "id": f"email_{len(self.sent_emails)}",
            "to": to,
            "subject": subject,
            "body": body,
            "status": "sent",
        }
        
        self.sent_emails.append(email)
        
        # In a real implementation, this would actually send the email
        return {
            "success": True,
            "email": email,
            "message": f"Email sent to {to}: {subject}",
        }
    
    async def _list_emails(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List emails"""
        # In a real implementation, this would query the actual email service
        return {
            "success": True,
            "emails": self.sent_emails,
            "count": len(self.sent_emails),
        }
    
    async def _search_emails(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Search emails"""
        query = params.get("query", "").lower()
        
        matching_emails = [
            email for email in self.sent_emails
            if query in email["subject"].lower() or query in email["body"].lower()
        ]
        
        return {
            "success": True,
            "emails": matching_emails,
            "count": len(matching_emails),
            "query": query,
        }


