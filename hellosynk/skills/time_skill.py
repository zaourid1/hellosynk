"""
Time Skill - Provide current date and time information
"""

from datetime import datetime, timezone
from typing import Any, Dict, Optional

try:
    from zoneinfo import ZoneInfo
except ImportError:  # Python <3.9
    ZoneInfo = None  # type: ignore

from hellosynk.skills.base import BaseSkill, SkillParameter


COMMON_TZ_ALIASES = {
    "pst": "America/Los_Angeles",
    "pdt": "America/Los_Angeles",
    "est": "America/New_York",
    "edt": "America/New_York",
    "cst": "America/Chicago",
    "cdt": "America/Chicago",
    "mst": "America/Denver",
    "mdt": "America/Denver",
    "bst": "Europe/London",
    "gmt": "Etc/GMT",
    "cet": "Europe/Paris",
    "cest": "Europe/Paris",
    "ist": "Asia/Kolkata",
    "jst": "Asia/Tokyo",
    "kst": "Asia/Seoul",
    "aest": "Australia/Sydney",
    "aedt": "Australia/Sydney",
    # Common city names
    "toronto": "America/Toronto",
    "new york": "America/New_York",
    "nyc": "America/New_York",
    "los angeles": "America/Los_Angeles",
    "la": "America/Los_Angeles",
    "chicago": "America/Chicago",
    "london": "Europe/London",
    "paris": "Europe/Paris",
    "tokyo": "Asia/Tokyo",
    "sydney": "Australia/Sydney",
    "mumbai": "Asia/Kolkata",
    "delhi": "Asia/Kolkata",
    "beijing": "Asia/Shanghai",
    "shanghai": "Asia/Shanghai",
    "seoul": "Asia/Seoul",
}


def _normalize_timezone(value: Any) -> Optional[str]:
    if value is None:
        return None
    if isinstance(value, str):
        trimmed = value.strip()
        if not trimmed:
            return None
        lower = trimmed.lower()
        if lower in ("local", "auto"):
            return "local"
        if lower in ("utc", "z", "coordinated universal time"):
            return "utc"
        if lower in COMMON_TZ_ALIASES:
            return COMMON_TZ_ALIASES[lower]
        return trimmed  # Assume IANA name
    return str(value)


class TimeSkill(BaseSkill):
    """Skill for retrieving current date and time"""

    name = "time"
    description = "Provide the current local or UTC time"
    version = "1.1.0"
    author = "HelloSynk Team"

    def get_parameters(self) -> list[SkillParameter]:
        return [
            SkillParameter(
                name="timezone",
                type="string",
                description="Timezone to use: 'local', 'utc', common abbreviations (e.g. 'PST'), or IANA name (e.g. 'America/New_York')",
                required=False,
                default="local",
            ),
            SkillParameter(
                name="format",
                type="string",
                description="Datetime format string (Python strftime).",
                required=False,
                default="%Y-%m-%d %H:%M:%S",
            ),
        ]

    async def execute(self, context: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        """Return the current time in the requested timezone and format"""
        validated_params = self.validate_params(params)

        tz_info = _normalize_timezone(validated_params.get("timezone", "local"))
        fallback_message = None

        if tz_info in (None, "local"):
            now = datetime.now()
            tz_label = "local"
        elif tz_info == "utc":
            now = datetime.now(timezone.utc)
            tz_label = "utc"
        else:
            if ZoneInfo is None:
                fallback_message = "IANA timezone support requires Python 3.9+"
                now = datetime.now()
                tz_label = "local"
            else:
                try:
                    zone = ZoneInfo(tz_info)
                except Exception:
                    fallback_message = f"Unsupported timezone '{tz_info}', using local time instead."
                    now = datetime.now()
                    tz_label = "local"
                else:
                    now = datetime.now(zone)
                    tz_label = tz_info

        fmt_value = validated_params.get("format", "%Y-%m-%d %H:%M:%S")
        if not isinstance(fmt_value, str) or not fmt_value:
            fmt_value = "%Y-%m-%d %H:%M:%S"

        try:
            formatted = now.strftime(fmt_value)
        except Exception:
            formatted = now.isoformat()

        result = {
            "success": True,
            "timezone": tz_label,
            "iso": now.isoformat(),
            "formatted": formatted,
        }
        if fallback_message:
            result["message"] = fallback_message
        return result
