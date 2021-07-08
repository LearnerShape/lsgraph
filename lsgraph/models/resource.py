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


from sqlalchemy.dialects.postgresql import ARRAY, UUID
import uuid

from . import db


class Resource(db.Model):
    """Learning resources

    All types of learning resources including courses, videos, articles, etc.
    Each resource may be available in multiple formats and have multiple offerings,
    i.e. available online and in classroom on dates X, Y, and Z"""

    id = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    name = db.Column(db.Text)
    short_description = db.Column(db.Text)
    description = db.Column(db.Text)
    url = db.Column(db.Text)
    provider_id = db.Column(UUID(as_uuid=True), db.ForeignKey("provider.id"))
    platform_id = db.Column(UUID(as_uuid=True), db.ForeignKey("platform.id"))
    platform_level = db.Column(db.String(64))
    alt_id = db.Column(db.Text)
    syllabus = db.Column(db.Text)
    learning_outcomes = db.Column(db.Text)
    prerequisite_knowledge = db.Column(db.Text)
    retired = db.Column(db.Boolean)
    resource_recommendation_vector = db.Column(ARRAY(db.Float))
