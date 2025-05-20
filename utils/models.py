from flask_sqlalchemy import SQLAlchemy
from datetime import date
from sqlalchemy.dialects.postgresql import ARRAY, JSONB

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "users"
    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    groups = db.relationship("Group", secondary="user_groups", back_populates="users")
    events = db.relationship("UserEvents", backref="user", cascade="all, delete-orphan")

class Group(db.Model):
    __tablename__ = "groups"
    group_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    users = db.relationship("User", secondary="user_groups", back_populates="groups")

class UserGroup(db.Model):
    __tablename__ = "user_groups"
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id", ondelete="CASCADE"), primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey("groups.group_id", ondelete="CASCADE"), primary_key=True)

class UserEvents(db.Model):
    __tablename__ = "user_events"
    event_id = db.Column(db.String, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id", ondelete="CASCADE"), primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    reason = db.Column(db.String(255))

class LLMEvent(db.Model):
    __tablename__ = "LLM_events"
    id = db.Column(db.String(64), primary_key=True)
    timestamp = db.Column(db.String(64), nullable=False)
    status = db.Column(db.String(16), nullable=False)
    event_string = db.Column(db.Text, nullable=False)
    persons = db.Column(ARRAY(db.String), nullable=False)
    groups = db.Column(ARRAY(db.String), nullable=False)
    returned_entry = db.Column(JSONB, nullable=True)

class Files(db.Model):
    __tablename__ = "files"
    file_id = db.Column(db.String(64), primary_key=True)
    file_path = db.Column(db.Text, nullable=False)