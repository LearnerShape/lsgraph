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

from sqlalchemy.dialects.postgresql import UUID
import uuid

from . import db


class Provider(db.Model):
    """Provider of learning resources

    Additional details on providers"""

    id = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    name = db.Column(db.String(256))
    description = db.Column(db.Text)
    logo = db.Column(db.Text)
    url = db.Column(db.Text)
    organization_id = db.Column(
        UUID(as_uuid=True), db.ForeignKey("organization.id"), index=True
    )
