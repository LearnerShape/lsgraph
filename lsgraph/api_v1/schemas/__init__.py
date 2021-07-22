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


from marshmallow import Schema, fields, validates_schema, ValidationError


class OrderedBaseSchema(Schema):
    class Meta:
        ordered = True


class UserSchema(OrderedBaseSchema):
    id = fields.UUID()
    email = fields.Email()
    name = fields.String()
    profile = fields.UUID(dump_only=True)


class UserManySchema(OrderedBaseSchema):
    users = fields.List(fields.Nested(lambda: UserSchema))


class SkillSchema(OrderedBaseSchema):
    id = fields.UUID(dump_only=True)
    name = fields.String(required=True)
    description = fields.String()
    path = fields.String(dump_only=True)
    parent = fields.UUID(required=True, load_only=True)
    personal = fields.Boolean(missing=False)
    creator = fields.Nested(UserSchema(only=("id",)))
    child_skills = fields.List(
        fields.Nested(lambda: SkillSchema(only=("id", "name"))), dump_only=True
    )
    num_descendants = fields.Integer(dump_only=True)


class SkillManySchema(OrderedBaseSchema):
    skills = fields.List(fields.Nested(lambda: SkillSchema))


class OrganizationSchema(OrderedBaseSchema):
    id = fields.UUID(dump_only=True)
    name = fields.String()
    root_skill = fields.Nested(SkillSchema(only=("id",)), dump_only=True)
    level_map = fields.Mapping(
        fields.String,
        fields.Float,
        missing={
            "No knowledge": 0.0,
            "Beginner": 1.0,
            "Intermediate": 2.0,
            "Advanced": 3.0,
            "Expert": 4.0,
        },
    )


class OrganizationManySchema(OrderedBaseSchema):
    organizations = fields.List(fields.Nested(lambda: OrganizationSchema))


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


class GroupSchema(OrderedBaseSchema):
    id = fields.UUID(dump_only=True)
    name = fields.String()
    whole_organization = fields.Boolean(missing=False)
    members = fields.List(
        fields.Nested(lambda: UserSchema(only=("id", "name"))), missing=[]
    )


class GroupManySchema(OrderedBaseSchema):
    groups = fields.List(fields.Nested(lambda: GroupSchema))


class GroupMembersSchema(OrderedBaseSchema):
    members = fields.List(fields.Nested(lambda: UserSchema(only=("id", "name"))))


class JobRecommendationQuerySchema(OrderedBaseSchema):
    profiles = fields.List(fields.UUID())
    profile_types = fields.List(fields.String())


class JobRecommendationSchema(OrderedBaseSchema):
    distance = fields.Float()
    fit = fields.Float()
    profile = fields.Nested(lambda: ProfileSchema())


class JobRecommendationManySchema(OrderedBaseSchema):
    recommendations = fields.List(fields.Nested(lambda: JobRecommendationSchema()))


class WorkforcePlanningTargetSchema(OrderedBaseSchema):
    profile = fields.UUID()
    number_needed = fields.Integer()
    max_training = fields.Float()


class WorkforcePlanningQuerySchema(OrderedBaseSchema):
    users = fields.List(fields.UUID())
    groups = fields.List(fields.UUID())
    targets = fields.List(fields.Nested(lambda: WorkforcePlanningTargetSchema()))


class WorkforcePlanningProfileRecommendationSchema(OrderedBaseSchema):
    distance = fields.Float()
    fit = fields.Float()
    profile = fields.UUID()


class WorkforcePlanningUserRecommendationSchema(OrderedBaseSchema):
    distance = fields.Float()
    fit = fields.Float()
    user = fields.UUID()


class WorkforcePlanningTargetResultSchema(OrderedBaseSchema):
    profile = fields.UUID()
    recommendations = fields.List(
        fields.Nested(lambda: WorkforcePlanningUserRecommendationSchema())
    )


class WorkforcePlanningUserResultSchema(OrderedBaseSchema):
    user = fields.UUID()
    recommendations = fields.List(
        fields.Nested(lambda: WorkforcePlanningProfileRecommendationSchema())
    )


class WorkforcePlanningSchema(OrderedBaseSchema):
    users_by_target = fields.List(
        fields.Nested(lambda: WorkforcePlanningTargetResultSchema())
    )
    targets_by_user = fields.List(
        fields.Nested(lambda: WorkforcePlanningUserResultSchema())
    )
