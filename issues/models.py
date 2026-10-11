"""Domain entities for the bug tracker.

These are intentionally plain Python classes (not Django ORM models), matching
the OOP exercise. Persistence is handled by the JSON storage module.
"""

from abc import ABC, abstractmethod


class BaseEntity(ABC):
    @abstractmethod
    def validate(self):
        """Raise ValueError when this entity contains invalid data."""

    def to_dict(self):
        return dict(self.__dict__)


class Reporter(BaseEntity):
    def __init__(self, id, name, email, team):
        self.id = id
        self.name = name
        self.email = email
        self.team = team

    def validate(self):
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("Name cannot be empty")
        if not isinstance(self.email, str) or "@" not in self.email:
            raise ValueError("Invalid email")
        if not isinstance(self.team, str) or not self.team.strip():
            raise ValueError("Team cannot be empty")


class Issue(BaseEntity):
    STATUSES = frozenset({"open", "in_progress", "resolved", "closed"})
    PRIORITIES = frozenset({"low", "medium", "high", "critical"})

    def __init__(self, id, title, description, status, priority, reporter_id, created_at=None):
        self.id = id
        self.title = title
        self.description = description
        self.status = status
        self.priority = priority
        self.reporter_id = reporter_id
        if created_at is not None:
            self.created_at = created_at

    def validate(self):
        if not isinstance(self.title, str) or not self.title.strip():
            raise ValueError("Title cannot be empty")
        if not isinstance(self.description, str):
            raise ValueError("Description must be a string")
        if self.status not in self.STATUSES:
            raise ValueError("Status must be one of: " + ", ".join(sorted(self.STATUSES)))
        if self.priority not in self.PRIORITIES:
            raise ValueError("Priority must be one of: " + ", ".join(sorted(self.PRIORITIES)))
        if isinstance(self.reporter_id, bool) or not isinstance(self.reporter_id, int) or self.reporter_id < 1:
            raise ValueError("reporter_id must be a positive integer")

    def describe(self):
        return f"{self.title} [{self.priority}]"


class CriticalIssue(Issue):
    def describe(self):
        return f"[URGENT] {self.title} — needs immediate attention"


class LowPriorityIssue(Issue):
    def describe(self):
        return f"{self.title} — low priority, handle when free"
