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


from marshmallow import fields, ValidationError

from .shared import OrderedBaseSchema
from .format import FormatSchema


class NewOfferingSchema(OrderedBaseSchema):
    id = fields.UUID(dump_only=True)
    name = fields.String()
    format = fields.UUID()
    start_date = fields.AwareDateTime()
    end_date = fields.AwareDateTime()
    pace_min_hrs_per_week = fields.Float()
    pace_max_hrs_per_week = fields.Float()
    pace_num_weeks = fields.Float()
    elapsed_duration = fields.Float()
    min_taught_duration = fields.Float()
    max_taught_duration = fields.Float()
    language = fields.String()
    cc_language = fields.String()
    free = fields.Boolean()
    free_audit = fields.Boolean()
    paid = fields.Boolean()
    certificate = fields.Boolean()
    quality = fields.Float()
    instructors = fields.String()
    retired = fields.Boolean()


class OfferingSchema(OrderedBaseSchema):
    id = fields.UUID(dump_only=True)
    name = fields.String()
    format = fields.Nested(FormatSchema)
    start_date = fields.AwareDateTime()
    end_date = fields.AwareDateTime()
    pace_min_hrs_per_week = fields.Float()
    pace_max_hrs_per_week = fields.Float()
    pace_num_weeks = fields.Float()
    elapsed_duration = fields.Float()
    min_taught_duration = fields.Float()
    max_taught_duration = fields.Float()
    language = fields.String()
    cc_language = fields.String()
    free = fields.Boolean()
    free_audit = fields.Boolean()
    paid = fields.Boolean()
    certificate = fields.Boolean()
    quality = fields.Float()
    instructors = fields.String()
    retired = fields.Boolean()


class OfferingManySchema(OrderedBaseSchema):
    offerings = fields.List(fields.Nested(lambda: OfferingSchema))
