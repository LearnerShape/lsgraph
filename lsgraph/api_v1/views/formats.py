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
from lsgraph.api_v1.schemas import FormatSchema, FormatManySchema


def create_new_format(format_data, org_uuid):
    """Create new format"""
    new_format = models.Format(
        name=format_data["name"],
        description=format_data["description"],
        logo=format_data.get("logo"),
        organization_id=org_uuid,
    )
    db.session.add(new_format)
    db.session.commit()
    return new_format


@api.route("organizations/<org_uuid>/formats/")
class FormatsAPI(MethodView):
    @api.response(200, FormatManySchema)
    def get(self, org_uuid):
        """Get formats

        Get a list of all resource formats for an organization

        """
        formats = models.Format.query.filter_by(organization_id=org_uuid).all()
        return {"formats": formats}

    @api.arguments(FormatSchema, location="json")
    @api.response(200, FormatSchema)
    def post(self, format_data, org_uuid):
        """Add format

        Create a new format for resources in the organization

        """
        new_format = create_new_format(format_data, org_uuid)
        return new_format


@api.route("organizations/<org_uuid>/formats/<format_uuid>/")
class FormatsDetailAPI(MethodView):
    @api.response(200, FormatSchema)
    def get(self, org_uuid, format_uuid):
        """Get format details

        Get detailed information on a specific format

        """
        format = models.Format.query.filter_by(
            organization_id=org_uuid, id=format_uuid
        ).one()
        return format

    @api.response(204)
    def delete(self, org_uuid, format_uuid):
        """Delete format

        Delete a resource format from an organization
        """
        models.Format.query.filter_by(organization_id=org_uuid, id=format_uuid).delete()
        db.session.commit()
