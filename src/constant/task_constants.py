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
    REDO = "redo"
    REJECTED = "rejected"

class TaskType(str, Enum):
    AUDIO = "audio"
    TEXT = "text"
    VIDEO = "video"
    IMAGE = "image"

