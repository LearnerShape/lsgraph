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
from .user import UserSchema


class GroupMemberSchema(OrderedBaseSchema):
    id = fields.UUID()
    name = fields.String()


class GroupSchema(OrderedBaseSchema):
    id = fields.UUID(dump_only=True)
    name = fields.String()
    whole_organization = fields.Boolean(missing=False)
    members = fields.List(fields.Nested(lambda: GroupMemberSchema()), missing=[])


class GroupManySchema(OrderedBaseSchema):
    groups = fields.List(fields.Nested(lambda: GroupSchema))


class GroupMembersSchema(OrderedBaseSchema):
    members = fields.List(fields.Nested(lambda: GroupMemberSchema()))
