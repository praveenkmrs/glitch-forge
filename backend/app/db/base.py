"""Import all models here for Alembic autogenerate to work.

This file is imported by alembic/env.py to discover all models.
Every time you create a new model, import it here!

Why this pattern?
- Alembic needs to see all models to generate migrations
- Central place to import models (one place to update)
- Clean dependency management
"""

from app.db.base_class import Base  # noqa: F401

# Import all models here (REQUIRED for Alembic autogenerate)
from app.models.user import User  # noqa: F401
from app.models.consultation_request import ConsultationRequest  # noqa: F401
from app.models.webhook_delivery import WebhookDelivery  # noqa: F401
from app.models.api_key import APIKey  # noqa: F401
