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
from lsgraph.api_v1.schemas import UserSchema, UserManySchema, JobRecommendationQuerySchema, JobRecommendationManySchema


def create_new_user(user_data, org_uuid):
    """Create a new user record"""
    # Add to user table
    new_user = models.User(
        name=user_data["name"], email=user_data["email"], organization_id=org_uuid
    )
    db.session.add(new_user)
    db.session.commit()
    # Create user profile
    new_profile = models.Profile(
        name=user_data["name"],
        organization_id=org_uuid,
        user_id=new_user.id,
        type="user_profile",
    )
    db.session.add(new_profile)
    db.session.commit()
    # Add to whole org group
    whole_org_group = models.Group.query.filter_by(
        organization_id=org_uuid, whole_organization=True
    ).all()
    for group in whole_org_group:
        new_member = models.GroupMember(user_id=new_user.id, group_id=group.id)
        db.session.add(new_member)
    db.session.commit()
    output = {
        "id": new_user.id,
        "email": new_user.email,
        "name": new_user.name,
        "profile": new_profile.id,
    }
    return output


@api.route("organizations/<org_uuid>/users/")
class UsersAPI(MethodView):
    @api.response(200, UserManySchema)
    def get(self, org_uuid):
        """Get users

        Get a list of all users within the organization"""
        users = models.User.query.filter_by(organization_id=org_uuid).all()
        return {"users": users}

    @api.arguments(UserSchema, location="json")
    @api.response(200, UserSchema)
    def post(self, user_data, org_uuid):
        """Add user

        Add a new user to the organization"""
        new_user = create_new_user(user_data, org_uuid)
        return new_user


@api.route("organizations/<org_uuid>/users/<user_uuid>/")
class UsersDetailAPI(MethodView):
    @api.response(200, UserSchema)
    def get(self, org_uuid, user_uuid):
        """Get user details"""
        return models.User.query.filter_by(id=user_uuid, organization_id=org_uuid).one()

    @api.response(204)
    def delete(self, org_uuid, user_uuid):
        """Delete user"""
        abort(500)


@api.route("organizations/<org_uuid>/users/<user_uuid>/job_recommendations/")
class UsersDetailAPI(MethodView):
    @api.arguments(JobRecommendationQuerySchema, location="json")
    @api.response(200, JobRecommendationManySchema)
    def get(self, org_uuid, user_uuid):
        """Get job recommendations"""
        abort(500)
