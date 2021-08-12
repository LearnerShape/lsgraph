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


class CollectionResourceSchema(OrderedBaseSchema):
    resource_id = fields.UUID()


class CollectionMemberSchema(OrderedBaseSchema):
    user_id = fields.UUID()
    group_id = fields.UUID()
    edit = fields.Boolean()


class CollectionSchema(OrderedBaseSchema):
    id = fields.UUID()
    name = fields.String()
    public = fields.Boolean()


class CollectionManySchema(OrderedBaseSchema):
    collections = fields.List(fields.Nested(lambda: CollectionSchema))


class CollectionResourcesSchema(OrderedBaseSchema):
    resources = fields.List(fields.Nested(lambda: CollectionResourceSchema()))


class CollectionMembersSchema(OrderedBaseSchema):
    members = fields.List(fields.Nested(lambda: CollectionMemberSchema()))
