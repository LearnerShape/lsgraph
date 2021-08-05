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
