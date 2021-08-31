# Copyright (C) 2021  Learnershape and contributors

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from sqlalchemy import Index
from sqlalchemy.dialects.postgresql import ARRAY, UUID
import uuid

from . import db
from ._shared import TSVECTOR


class Skill(db.Model):
    """A skill"""

    id = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    name = db.Column(db.Text)
    description = db.Column(db.Text)
    personal = db.Column(db.Boolean)
    creator_id = db.Column(UUID(as_uuid=True), db.ForeignKey("user.id"))
    skill_embedding = db.Column(ARRAY(db.Float))
    resource_recommendation_vector = db.Column(ARRAY(db.Float))
    __ts_vector__ = db.Column(
        TSVECTOR(),
        db.Computed(
            "to_tsvector('english', name)",
            persisted=True,
        ),
    )

    __table_args__ = (
        Index("ix_skill_name__ts_vector__", __ts_vector__, postgresql_using="gin"),
    )
