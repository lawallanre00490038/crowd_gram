from enum import Enum


class ContributorTaskStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    REDO = "redo"
    SUBMITTED = "submitted"
    ASSIGNED = "assigned"


class ReviewerTaskStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
