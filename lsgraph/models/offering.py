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


class Offering(db.Model):
    """Learning resource offerings

    A specific instance when a learning resource can be taken. Intended for courses
    that are run over specific dates, e.g. the next time the course will be run is
    the Spring 2022 semester"""

    id = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    name = db.Column(db.Text)
    resource_id = db.Column(UUID(as_uuid=True), db.ForeignKey("resource.id"))
    format_id = db.Column(UUID(as_uuid=True), db.ForeignKey("format.id"))
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    pace_min_hrs_per_week = db.Column(db.Float)
    pace_max_hrs_per_week = db.Column(db.Float)
    pace_num_weeks = db.Column(db.Integer)
    elapsed_duration = db.Column(db.Float)
    min_taught_duration = db.Column(db.Float)
    max_taught_duration = db.Column(db.Float)
    language = db.Column(db.String(128))
    cc_language = db.Column(db.String(128))
    free = db.Column(db.Boolean)
    free_audit = db.Column(db.Boolean)
    paid = db.Column(db.Boolean)
    certificate = db.Column(db.Boolean)
    quality = db.Column(db.Float)
    instructors = db.Column(db.Text)
