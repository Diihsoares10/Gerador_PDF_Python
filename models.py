from datetime import datetime
from sqlalchemy import UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from flask_dance.consumer.storage.sqla import OAuthConsumerMixin
from flask_login import UserMixin

from app import db


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.String, primary_key=True)
    email = db.Column(db.String, unique=True, nullable=True)
    first_name = db.Column(db.String, nullable=True)
    last_name = db.Column(db.String, nullable=True)
    profile_image_url = db.Column(db.String, nullable=True)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class OAuth(OAuthConsumerMixin, db.Model):
    user_id = db.Column(db.String, db.ForeignKey(User.id))
    browser_session_key = db.Column(db.String, nullable=False)
    user = db.relationship(User)

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "browser_session_key",
            "provider",
            name="uq_user_browser_session_key_provider",
        ),
    )


class Submission(db.Model):
    """Stores both drafts and completed form submissions."""

    __tablename__ = "submissions"

    id = db.Column(db.Integer, primary_key=True)

    # Public token to resume editing without login
    resume_token = db.Column(db.String(36), unique=True, nullable=False, index=True)

    # Optional owner (when the user logs in / claims the draft)
    user_id = db.Column(db.String, db.ForeignKey(User.id), nullable=True)

    # Flexible field storage
    data = db.Column(JSONB, nullable=False, default=dict)

    # Lifecycle
    status = db.Column(db.String(20), default="draft", nullable=False)  # draft | completed
    progress = db.Column(db.Integer, default=0, nullable=False)         # 0..100

    # Helpful denormalised columns for quick admin search
    nome = db.Column(db.String(255), nullable=True, index=True)
    cpf = db.Column(db.String(20), nullable=True, index=True)
    email = db.Column(db.String(255), nullable=True, index=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
