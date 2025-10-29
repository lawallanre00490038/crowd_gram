from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Enum
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class Agent(Base):
    __tablename__ = "agents"
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True)

    name = Column(String)
    email = Column(String, unique=True)
    password_hash = Column(String)
    has_organization = Column(String)
    company = Column(String)

    phone = Column(String)
    gender = Column(String)
    location = Column(String)
    languages = Column(String)
    industry = Column(String)
    primary_device = Column(String)
    dialect_fluency = Column(String)

    education = Column(String)
    preferences = Column(String)
    device = Column(String)  # replaced by primary device?
    internet = Column(String)  # replaced by internet_quality?

    referrer = Column(String)
    referrer_id = Column(Integer)
    status = Column(Enum("pending", "eligible",
                    "ineligible", name="status_enum"))
    score = Column(Integer, default=0)

    # time stamp
    created_at = Column(DateTime, default=datetime.utcnow)  # NOUVEAU
    updated_at = Column(DateTime, default=datetime.utcnow,
                        onupdate=datetime.utcnow)  # NOUVEAU


class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True)
    type = Column(String)
    data = Column(String)
    assigned_to = Column(Integer, ForeignKey("agents.id"))
    status = Column(String)
    score = Column(Integer)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)


class Submission(Base):
    __tablename__ = "submissions"
    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey("tasks.id"))
    agent_id = Column(Integer, ForeignKey("agents.id"))
    media_id = Column(String)
    timestamp = Column(DateTime)
    qa_score = Column(Integer)
    status = Column(String)
