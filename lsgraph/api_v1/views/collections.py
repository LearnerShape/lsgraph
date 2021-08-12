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


from flask.views import MethodView
import pdb

from lsgraph.api_v1 import api
from ._shared import authorized_org


@api.route("organizations/<org_uuid>/collections/")
class CollectionsAPI(MethodView):
    decorators = [authorized_org]

    @api.response(200, CollectionManySchema)
    def get(self, org_uuid=None):
        """Get collections

        Get a list of all collections for an organization
        """
        return "Hello"

    @api.arguments(CollectionSchema, location="json")
    @api.response(CollectionSchema, location="json")
    def post(self, collection_data, org_uuid):
        """Add collection

        Create a new collection for an organization
        """
        return "Hello"


@api.route("organizations/<org_uuid>/collections/<collection_uuid>/")
class CollectionsDetailAPI(MethodView):
    decorators = [authorized_org]

    @api.response(200, CollectionSchema)
    def get(self, org_uuid, collection_uuid):
        """Get collection details

        Get detailed information on a specific collection
        """
        return "Hello"

    @api.response(204)
    def delete(self, org_uuid, collection_uuid):
        """Delete collection

        Delete a collection from an organization

        """
        return "Hello"


@api.route("organizations/<org_uuid>/collections/<collection_uuid>/resources/")
class CollectionResourcesAPI(MethodView):
    decorators = [authorized_org]

    @api.response(200, CollectionResourcesSchema)
    def get(self, org_uuid, collection_uuid):
        """Get collection resources

        Get a list of resources for a specific collection
        """
        return "Hello"

    @api.arguments(CollectionResourcesSchema, location="json")
    @api.response(200, CollectionResourcesSchema)
    def post(self, resource_data, org_uuid, collection_uuid):
        """Update collection resources

        Add additional resources to a specific collection

        """
        return "Hello"


@api.route(
    "organizations/<org_uuid>/collections/<collection_uuid>/resources/<resource_uuid>/"
)
class CollectionResourcesDetailAPI(MethodView):
    decorators = [authorized_org]

    @api.response(204)
    def delete(self, org_uuid, collection_uuid, resource_uuid):
        """Delete collection resource

        Delete a specific resource from a collection

        """
        return "Hello"


@api.route("organizations/<org_uuid>/collections/<collection_uuid>/members/")
class CollectionMembersAPI(MethodView):
    decorators = [authorized_org]

    @api.response(200, CollectionMembersSchema)
    def get(self, org_uuid, collection_uuid):
        """Get collection members

        Get a list of members for a specific collection
        """
        return "Hello"

    @api.arguments(CollectionMembersSchema, location="json")
    @api.response(200, CollectionMembersSchema)
    def post(self, member_data, org_uuid, collection_uuid):
        """Update collection members

        Add additional members to a specific collection

        """
        return "Hello"


@api.route(
    "organizations/<org_uuid>/collections/<collection_uuid>/members/<member_uuid>/"
)
class CollectionMembersDetailAPI(MethodView):
    decorators = [authorized_org]

    @api.response(204)
    def delete(self, org_uuid, collection_uuid, member_uuid):
        """Delete collection member

        Delete a specific member from a collection

        """
        return "Hello"
