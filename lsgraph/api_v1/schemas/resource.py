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
from .offering import OfferingSchema
from .platform import PlatformSchema
from .provider import ProviderSchema


class ResourceQuerySchema(OrderedBaseSchema):
    query = fields.String()
    user = fields.UUID()
    skill = fields.UUID()


class NewResourceSchema(OrderedBaseSchema):
    id = fields.UUID()
    name = fields.String(required=True)
    short_description = fields.String(required=True)
    description = fields.String()
    url = fields.Url()
    provider = fields.UUID()
    platform = fields.UUID()
    platform_level = fields.String()
    alt_id = fields.String()
    syllabus = fields.String()
    learning_outcomes = fields.String()
    prerequisite_knowledge = fields.String()
    retired = fields.Boolean(default=False, missing=False)


class ResourceSchema(OrderedBaseSchema):
    id = fields.UUID()
    name = fields.String(required=True)
    short_description = fields.String(required=True)
    description = fields.String()
    url = fields.Url()
    provider = fields.Nested(lambda: ProviderSchema())
    platform = fields.Nested(lambda: PlatformSchema())
    platform_level = fields.String()
    alt_id = fields.String()
    syllabus = fields.String()
    learning_outcomes = fields.String()
    prerequisite_knowledge = fields.String()
    retired = fields.Boolean(missing=False)
    offerings = fields.List(fields.Nested(lambda: OfferingSchema()))


class ResourceManySchema(OrderedBaseSchema):
    resources = fields.List(fields.Nested(lambda: ResourceSchema()))
