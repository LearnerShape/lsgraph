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
from lsgraph.api_v1.schemas import PlatformSchema, PlatformManySchema


def create_new_platform(platform_data, org_uuid):
    """Create new platform"""
    new_platform = models.Platform(
        name=platform_data["name"],
        description=platform_data["description"],
        logo=platform_data.get("logo"),
        url=platform_data.get("url"),
        subscription=platform_data.get("subscription"),
        free_trial=platform_data.get("free_trial"),
        organization_id=org_uuid,
    )
    db.session.add(new_platform)
    db.session.commit()
    return new_platform


@api.route("organizations/<org_uuid>/platforms/")
class PlatformsAPI(MethodView):
    @api.response(200, PlatformManySchema)
    def get(self, org_uuid):
        """Get platforms

        Get a list of all resource platforms for an organization

        """
        platforms = models.Platform.query.filter_by(organization_id=org_uuid).all()
        return {"platforms": platforms}

    @api.arguments(PlatformSchema, location="json")
    @api.response(200, PlatformSchema)
    def post(self, platform_data, org_uuid):
        """Add platform

        Create a new platform for resources in the organization

        """
        new_platform = create_new_platform(platform_data, org_uuid)
        return new_platform


@api.route("organizations/<org_uuid>/platforms/<platform_uuid>/")
class PlatformsDetailAPI(MethodView):
    @api.response(200, PlatformSchema)
    def get(self, org_uuid, platform_uuid):
        """Get platform details

        Get detailed information on a specific platform

        """
        platform = models.Platform.query.filter_by(
            organization_id=org_uuid, id=platform_uuid
        ).one()
        return platform

    @api.response(204)
    def delete(self, org_uuid, platform_uuid):
        """Delete platform

        Delete a resource platform from an organization
        """
        models.Platform.query.filter_by(
            organization_id=org_uuid, id=platform_uuid
        ).delete()
        db.session.commit()
