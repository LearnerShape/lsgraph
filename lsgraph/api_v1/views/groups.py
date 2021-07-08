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
from flask import g
from flask_smorest import abort
from marshmallow import ValidationError
import pdb

from lsgraph import models
from lsgraph.models import db
from lsgraph.api_v1 import api
from lsgraph.api_v1.schemas import GroupSchema, GroupManySchema, GroupMembersSchema


def create_new_group(group_data, org_uuid):
    """Create a new group record"""
    new_group = models.Group(
        organization_id=org_uuid,
        name=group_data["name"],
        whole_organization=group_data["whole_organization"],
    )
    db.session.add(new_group)
    db.session.commit()
    members = [i["id"] for i in group_data["members"]]
    # TODO check users belong to organization
    if group_data["whole_organization"]:
        members = [
            i.id for i in models.User.query.filter_by(organization_id=org_uuid).all()
        ]
    added_members = add_members(org_uuid, new_group.id, members)
    added_members = models.User.query.filter(models.User.id.in_(added_members)).all()
    output = {
        "id": new_group.id,
        "name": new_group.name,
        "whole_organization": new_group.whole_organization,
        "members": [{"id": i.id, "name": i.name} for i in added_members],
    }
    return output


def add_members(org_id, group_id, user_ids):
    """Add members to a group"""
    # Check that members belong to the organization
    users = models.User.query.filter(models.User.id.in_(user_ids)).all()
    users = {i.id: i for i in users}
    for i in user_ids:
        if (i not in users) or (str(users[i].organization_id) != org_id):
            abort(403, message=f"Unrecognized user: {i}")
    # Check that members have not already been added
    group_members = (
        models.GroupMember.query.filter(models.GroupMember.group_id == group_id)
        .filter(models.GroupMember.user_id.in_(user_ids))
        .all()
    )
    to_add = user_ids[:]
    for i in group_members:
        to_add.remove(i.user_id)
    # Add members
    for user_id in to_add:
        new_member = models.GroupMember(user_id=user_id, group_id=group_id)
        db.session.add(new_member)
    db.session.commit()
    return to_add


def get_group(org_id, group_id):
    """Get group information"""
    members = get_group_members(org_id, group_id)
    group = (
        models.Group.query.filter(models.Group.id == group_id)
        .filter(models.Group.organization_id == org_id)
        .one()
    )
    output = {
        "id": group.id,
        "name": group.name,
        "whole_organization": group.whole_organization,
        "members": members,
    }
    return output


def get_group_members(org_id, group_id):
    """Get members of a group"""
    members = (
        models.User.query.filter(models.User.id == models.GroupMember.user_id)
        .filter(models.GroupMember.group_id == group_id)
        .all()
    )
    return [{"id": i.id, "name": i.name} for i in members]


@api.route("organizations/<org_uuid>/groups/")
class GroupsAPI(MethodView):
    @api.response(200, GroupManySchema)
    def get(self, org_uuid):
        """Get groups"""
        groups = models.Group.query.filter_by(organization_id=org_uuid).all()
        return {"groups": groups}

    @api.arguments(GroupSchema, location="json")
    @api.response(200, GroupSchema)
    def post(self, group_data, org_uuid):
        """Add group"""
        new_group = create_new_group(group_data, org_uuid)
        return new_group


@api.route("organizations/<org_uuid>/groups/<group_uuid>/")
class GroupsDetailAPI(MethodView):
    @api.response(200, GroupSchema)
    def get(self, org_uuid, group_uuid):
        """Get group details"""
        group = get_group(org_uuid, group_uuid)
        return group

    @api.response(204)
    def delete(self, org_uuid, group_uuid):
        """Delete group"""
        group = models.Group.query.filter_by(
            organization_id=org_uuid, id=group_uuid
        ).one()
        # Delete members
        models.GroupMember.query.filter_by(group_id=group.id).delete()
        # Delete group
        db.session.delete(group)
        db.session.commit()


@api.route("organizations/<org_uuid>/groups/<group_uuid>/members/")
class GroupMembersAPI(MethodView):
    @api.response(200, GroupMembersSchema)
    def get(self, org_uuid, group_uuid):
        """Group members endpoint"""
        members = get_group_members(org_uuid, group_uuid)
        return {"members": members}

    @api.arguments(GroupMembersSchema, location="json")
    @api.response(200, GroupSchema)
    def post(self, members_data, org_uuid, group_uuid):
        """Update group members"""
        add_members(org_uuid, group_uuid, [i["id"] for i in members_data["members"]])
        members = get_group_members(org_uuid, group_uuid)
        return {"members": members}


@api.route("organizations/<org_uuid>/groups/<group_uuid>/members/<user_uuid>/")
class GroupMembersDetailAPI(MethodView):
    @api.response(204)
    def delete(self, org_uuid, group_uuid, user_uuid):
        """Delete group member"""
        member = (
            models.GroupMember.query.filter_by(group_id=group_uuid)
            .filter_by(user_id=user_uuid)
            .all()
        )
        if len(member) == 0:
            abort(404, message="Member not found")
        for i in member:
            db.session.delete(i)
        db.session.commit()
