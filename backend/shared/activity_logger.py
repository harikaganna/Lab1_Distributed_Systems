from datetime import datetime, timezone
from .database import get_db


def log_activity(action: str, entity_type: str, entity_id: str, user_id: str = None, details: dict = None):
    """Write an activity log entry to MongoDB."""
    try:
        db = get_db()
        db.activity_logs.insert_one({
            "action": action,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "user_id": user_id,
            "details": details or {},
            "timestamp": datetime.now(timezone.utc),
        })
    except Exception:
        pass  # never let logging break the main flow
