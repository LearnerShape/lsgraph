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


from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()

__all__ = [
    "Organization",
    "Resource",
    "Format",
    "Offering",
    "Price",
    "Platform",
    "Provider",
    "Collection",
    "CollectionResource",
    "CollectionMember",
    "Group",
    "GroupMember",
    "QualityAttribute",
    "QualityValue",
    "Skill",
    "SkillInclude",
    "User",
    "Customer",
    "AccessKey",
    "Profile",
    "ProfileSkill",
]


from .organization import Organization
from .resource import Resource
from .format import Format
from .offering import Offering
from .price import Price
from .platform import Platform
from .provider import Provider
from .collection import Collection
from .collection_resource import CollectionResource
from .collection_member import CollectionMember
from .group import Group
from .group_member import GroupMember
from .quality_attribute import QualityAttribute
from .quality_value import QualityValue
from .skill import Skill
from .skill_include import SkillInclude
from .user import User
from .customer import Customer
from .access_key import AccessKey
from .profile import Profile
from .profile_skill import ProfileSkill
