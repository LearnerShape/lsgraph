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
from .profile import ProfileSchema


class JobRecommendationQuerySchema(OrderedBaseSchema):
    profiles = fields.List(fields.UUID())
    profile_types = fields.List(fields.String())


class JobRecommendationSchema(OrderedBaseSchema):
    distance = fields.Float()
    fit = fields.Float()
    profile = fields.Nested(lambda: ProfileSchema())


class JobRecommendationManySchema(OrderedBaseSchema):
    recommendations = fields.List(fields.Nested(lambda: JobRecommendationSchema()))
