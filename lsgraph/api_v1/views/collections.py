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
from sqlalchemy import or_

from lsgraph import models
from lsgraph.models import db
from lsgraph.api_v1 import api
from lsgraph.api_v1.schemas import (
    CollectionManySchema,
    CollectionSchema,
    CollectionResourcesSchema,
    CollectionMembersSchema,
)
from ._shared import authorized_org


def get_collection(org_uuid, collection_uuid):
    collection = models.Collection.query.filter_by(
        id=collection_uuid, organization_id=org_uuid
    ).one()
    return collection


def create_new_collection(collection_data, org_uuid):
    """Create a new collection"""
    new_collection = models.Collection(
        name=collection_data["name"],
        public=collection_data["public"],
        organization_id=org_uuid,
    )
    db.session.add(new_collection)
    db.session.commit()
    return new_collection


def update_resources(resource_data, org_uuid, collection_uuid):
    """Update collection resources"""
    # Check that resources belong to the organization
    resource_ids = [i["resource_id"] for i in resource_data["resources"]]
    org_resources = (
        models.Resource.query.filter(models.Resource.id.in_(resource_ids))
        .filter_by(organization_id=org_uuid)
        .all()
    )
    org_resources = {i.id for i in org_resources}
    for i in resource_ids:
        if i not in org_resources:
            abort(403, message=f"Unrecognized resource, {i}")
    # Check that resources have not already been added
    collection_resources = (
        models.CollectionResource.query.filter(
            models.CollectionResource.collection_id == collection_uuid
        )
        .filter(models.CollectionResource.resource_id.in_(resource_ids))
        .all()
    )
    to_add = resource_ids[:]
    for i in collection_resources:
        to_add.remove(i.resource_id)
    for i in to_add:
        db.session.add(
            models.CollectionResource(collection_id=collection_uuid, resource_id=i)
        )
    db.session.commit()
    return [{"resource_id": i} for i in to_add]


def build_member(member):
    output = {"edit": member.edit}
    if member.user_id:
        output["user_id"] = member.user_id
    if member.group_id:
        output["group_id"] = member.group_id
    return output


def update_members(member_data, org_uuid, collection_uuid):
    """Update collection members"""
    # Check that members belong to the organization
    user_ids = [i["user_id"] for i in member_data["members"] if "user_id" in i]
    group_ids = [i["group_id"] for i in member_data["members"] if "group_id" in i]
    org_users = (
        models.User.query.filter(models.User.id.in_(user_ids))
        .filter_by(organization_id=org_uuid)
        .all()
    )
    org_users = {i.id for i in org_users}
    org_groups = (
        models.Group.query.filter(models.Group.id.in_(group_ids))
        .filter_by(organization_id=org_uuid)
        .all()
    )
    org_groups = {i.id for i in org_groups}
    for i in user_ids:
        if i not in org_users:
            abort(403, message=f"Unrecognized user, {i}")
    for i in group_ids:
        if i not in org_groups:
            abort(403, message=f"Unrecognized group, {i}")
    # Check that resources have not already been added
    collection_members = (
        models.CollectionMember.query.filter(
            models.CollectionMember.collection_id == collection_uuid
        )
        .filter(
            or_(
                models.CollectionMember.user_id.in_(user_ids),
                models.CollectionMember.group_id.in_(group_ids),
            )
        )
        .all()
    )
    added_users = {i.user_id: i for i in collection_members}
    added_groups = {i.group_id for i in collection_members}
    to_return = []
    for i in member_data["members"]:
        if "user_id" in i:
            if i["user_id"] in added_users:
                m = added_users[i["user_id"]]
                m.edit = i["edit"]
            else:
                m = models.CollectionMember(
                    collection_id=collection_uuid, user_id=i["user_id"], edit=i["edit"]
                )
        elif "group_id" in i:
            if i["group_id"] in added_groups:
                m = added_groups[i["group_id"]]
                m.edit = i["edit"]
            else:
                m = models.CollectionMember(
                    collection_id=collection_uuid,
                    group_id=i["group_id"],
                    edit=i["edit"],
                )
        db.session.add(m)
        to_return.append(m)
    db.session.commit()
    return [build_member(i) for i in to_return]


@api.route("organizations/<org_uuid>/collections/")
class CollectionsAPI(MethodView):
    decorators = [authorized_org]

    @api.response(200, CollectionManySchema)
    def get(self, org_uuid=None):
        """Get collections

        Get a list of all collections for an organization
        """
        collections = models.Collection.query.filter_by(organization_id=org_uuid).all()
        return {"collections": collections}

    @api.arguments(CollectionSchema, location="json")
    @api.response(200, CollectionSchema)
    def post(self, collection_data, org_uuid):
        """Add collection

        Create a new collection for an organization
        """
        new_collection = create_new_collection(collection_data, org_uuid)
        return new_collection


@api.route("organizations/<org_uuid>/collections/<collection_uuid>/")
class CollectionsDetailAPI(MethodView):
    decorators = [authorized_org]

    @api.response(200, CollectionSchema)
    def get(self, org_uuid, collection_uuid):
        """Get collection details

        Get detailed information on a specific collection
        """
        collection = models.Collection.query.filter_by(
            id=collection_uuid, organization_id=org_uuid
        ).one()
        return collection

    @api.response(204)
    def delete(self, org_uuid, collection_uuid):
        """Delete collection

        Delete a collection from an organization

        """
        collection = models.Collection.query.filter_by(
            id=collection_uuid, organization_id=org_uuid
        ).one()
        # Delete resources
        models.CollectionResource.query.filter_by(collection_id=collection.id).delete()
        # Delete members
        models.CollectionMember.query.filter_by(collection_id=collection.id).delete()
        # Delete collection
        db.session.delete(collection)
        db.session.commit()


@api.route("organizations/<org_uuid>/collections/<collection_uuid>/resources/")
class CollectionResourcesAPI(MethodView):
    decorators = [authorized_org]

    @api.response(200, CollectionResourcesSchema)
    def get(self, org_uuid, collection_uuid):
        """Get collection resources

        Get a list of resources for a specific collection
        """
        collection = get_collection(org_uuid, collection_uuid)
        resources = models.CollectionResource.query.filter_by(
            collection_id=collection.id
        ).all()
        return {"resources": resources}

    @api.arguments(CollectionResourcesSchema, location="json")
    @api.response(200, CollectionResourcesSchema)
    def post(self, resource_data, org_uuid, collection_uuid):
        """Update collection resources

        Add additional resources to a specific collection

        """
        collection = get_collection(org_uuid, collection_uuid)
        resources = update_resources(resource_data, org_uuid, collection.id)
        return {"resources": resources}


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
        collection = get_collection(org_uuid, collection_uuid)
        models.CollectionResource.query.filter_by(
            resource_id=resource_uuid, collection_id=collection.id
        ).delete()
        db.session.commit()


@api.route("organizations/<org_uuid>/collections/<collection_uuid>/members/")
class CollectionMembersAPI(MethodView):
    decorators = [authorized_org]

    @api.response(200, CollectionMembersSchema)
    def get(self, org_uuid, collection_uuid):
        """Get collection members

        Get a list of members for a specific collection
        """
        collection = get_collection(org_uuid, collection_uuid)
        members = models.CollectionMember.query.filter_by(
            collection_id=collection.id
        ).all()
        return {"members": members}

    @api.arguments(CollectionMembersSchema, location="json")
    @api.response(200, CollectionMembersSchema)
    def post(self, member_data, org_uuid, collection_uuid):
        """Update collection members

        Add additional members to a specific collection

        """
        collection = get_collection(org_uuid, collection_uuid)
        members = update_members(member_data, org_uuid, collection.id)
        return {"members": members}


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
        collection = get_collection(org_uuid, collection_uuid)
        models.CollectionMember.query.filter_by(collection_id=collection.id).filter(
            or_(
                models.CollectionMember.user_id == member_uuid,
                models.CollectionMember.group_id == member_uuid,
            )
        ).delete()
        db.session.commit()
