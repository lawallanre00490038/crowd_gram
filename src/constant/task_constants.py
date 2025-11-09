from enum import Enum


class ContributorTaskStatus(Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    REDO = "redo"
    SUBMITTED = "submitted"
    ASSIGNED = "assigned"
