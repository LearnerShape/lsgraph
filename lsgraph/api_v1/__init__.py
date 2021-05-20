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


from flask import Blueprint

api = Blueprint("api_v1", __name__, url_prefix="/api/v1")

from .views import *

# Organizations
api.add_url_rule("organizations/", view_func=OrganizationsAPI.as_view("organizations"))
api.add_url_rule(
    "organizations/<org_uuid>/",
    view_func=OrganizationsDetailAPI.as_view("organizations_detail"),
)

# Graphs
api.add_url_rule("graphs/", view_func=GraphsAPI.as_view("graphs"))
api.add_url_rule(
    "graphs/<graph_uuid>/",
    view_func=GraphsDetailAPI.as_view("graphs_detail"),
)

# Skills
api.add_url_rule(
    "organizations/<org_uuid>/skills/", view_func=SkillsAPI.as_view("skills")
)
api.add_url_rule(
    "organizations/<org_uuid>/skills/<skill_uuid>/",
    view_func=SkillsDetailAPI.as_view("skills_detail"),
)

# Resources
api.add_url_rule(
    "organizations/<org_uuid>/resources/", view_func=ResourcesAPI.as_view("resources")
)
api.add_url_rule(
    "organizations/<org_uuid>/resources/<resource_uuid>/",
    view_func=ResourcesDetailAPI.as_view("resources_detail"),
)

# Groups
api.add_url_rule(
    "organizations/<org_uuid>/groups/", view_func=GroupsAPI.as_view("groups")
)
api.add_url_rule(
    "organizations/<org_uuid>/groups/<group_uuid>/",
    view_func=GroupsDetailAPI.as_view("groups_detail"),
)

# Collections
api.add_url_rule("collections/", view_func=CollectionsAPI.as_view("collections"))
api.add_url_rule(
    "organizations/<org_uuid>/collections/",
    view_func=CollectionsAPI.as_view("org_collections"),
)
api.add_url_rule(
    "collections/<collection_uuid>/",
    view_func=CollectionsDetailAPI.as_view("collections_detail"),
)
api.add_url_rule(
    "organizations/<org_uuid>/collections/<collection_uuid>/",
    view_func=CollectionsDetailAPI.as_view("org_collections_detail"),
)
api.add_url_rule(
    "collections/<collection_uuid>/resources/",
    view_func=CollectionResourcesAPI.as_view("collections_resources"),
)
api.add_url_rule(
    "organizations/<org_uuid>/collections/<collection_uuid>/resources/",
    view_func=CollectionResourcesAPI.as_view("org_collections_resources"),
)

# Pathways
api.add_url_rule(
    "organizations/<org_uuid>/pathways/", view_func=PathwaysAPI.as_view("pathways")
)
api.add_url_rule(
    "organizations/<org_uuid>/pathways/<pathway_uuid>/",
    view_func=PathwaysDetailAPI.as_view("pathways_detail"),
)

# Users
api.add_url_rule("organizations/<org_uuid>/users/", view_func=UsersAPI.as_view("users"))
api.add_url_rule(
    "organizations/<org_uuid>/users/<user_uuid>/",
    view_func=UsersDetailAPI.as_view("users_detail"),
)

# Profiles
api.add_url_rule(
    "organizations/<org_uuid>/profiles/", view_func=ProfilesAPI.as_view("profiles")
)
api.add_url_rule(
    "organizations/<org_uuid>/profiles/<profile_uuid>/",
    view_func=ProfilesDetailAPI.as_view("profiles_detail"),
)