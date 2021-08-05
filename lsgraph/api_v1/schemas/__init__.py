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


from marshmallow import ValidationError

from .skill import SkillSchema, SkillManySchema
from .user import UserSchema, UserManySchema
from .organization import OrganizationSchema, OrganizationManySchema
from .profile import (
    ProfileSkillSchema,
    ProfileSchema,
    ProfileManySchema,
    ProfileSkillsSchema,
)
from .group import GroupSchema, GroupManySchema, GroupMembersSchema
from .job_recommendation import (
    JobRecommendationQuerySchema,
    JobRecommendationSchema,
    JobRecommendationManySchema,
)
from .workforce_planning import (
    WorkforcePlanningTargetSchema,
    WorkforcePlanningQuerySchema,
    WorkforcePlanningProfileRecommendationSchema,
    WorkforcePlanningUserRecommendationSchema,
    WorkforcePlanningTargetResultSchema,
    WorkforcePlanningUserResultSchema,
    WorkforcePlanningSchema,
)
from .resource import NewResourceSchema, ResourceSchema, ResourceManySchema
from .platform import PlatformSchema, PlatformManySchema
from .provider import ProviderSchema, ProviderManySchema
from .format import FormatSchema, FormatManySchema
from .offering import NewOfferingSchema, OfferingSchema, OfferingManySchema
