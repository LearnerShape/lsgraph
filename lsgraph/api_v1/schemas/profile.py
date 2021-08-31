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


from marshmallow import fields, validates_schema, ValidationError

from .shared import OrderedBaseSchema


class ProfileSkillSchema(OrderedBaseSchema):
    skill = fields.UUID(required=True)
    level_name = fields.String()
    level = fields.Float()

    @validates_schema
    def validate_level(self, data, **kwargs):
        # should only be evaluated on load, for dump we can pass both
        filled_level = 0
        filled_level += 1 if data.get("level_name", False) else 0
        filled_level += 1 if data.get("level", False) else 0
        if filled_level != 1:
            raise ValidationError("Level name *or* level must be set")


class ProfileSchema(OrderedBaseSchema):
    id = fields.UUID(dump_only=True)
    name = fields.String()
    description = fields.String()
    user_id = fields.UUID()
    type = fields.String()
    previous_versions = fields.List(
        fields.Nested(lambda: ProfileSchema(only=("id",))), dump_only=True
    )
    skills = fields.List(fields.Nested(lambda: ProfileSkillSchema()))


class ProfileManySchema(OrderedBaseSchema):
    profiles = fields.List(fields.Nested(lambda: ProfileSchema))


class ProfileSkillsSchema(OrderedBaseSchema):
    skills = fields.List(fields.Nested(lambda: ProfileSkillSchema))
