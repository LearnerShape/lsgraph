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
from lsgraph.api_v1.schemas import ProviderSchema, ProviderManySchema


def create_new_provider(provider_data, org_uuid):
    """Create new provider"""
    new_provider = models.Provider(
        name=provider_data["name"],
        description=provider_data["description"],
        logo=provider_data.get("logo"),
        url=provider_data.get("url"),
        organization_id=org_uuid,
    )
    db.session.add(new_provider)
    db.session.commit()
    return new_provider


@api.route("organizations/<org_uuid>/providers/")
class ProvidersAPI(MethodView):
    @api.response(200, ProviderManySchema)
    def get(self, org_uuid):
        """Get providers

        Get a list of all resource providers for an organization

        """
        providers = models.Provider.query.filter_by(organization_id=org_uuid).all()
        return {"providers": providers}

    @api.arguments(ProviderSchema, location="json")
    @api.response(200, ProviderSchema)
    def post(self, provider_data, org_uuid):
        """Add provider

        Create a new provider for resources in the organization

        """
        new_provider = create_new_provider(provider_data, org_uuid)
        return new_provider


@api.route("organizations/<org_uuid>/providers/<provider_uuid>/")
class ProvidersDetailAPI(MethodView):
    @api.response(200, ProviderSchema)
    def get(self, org_uuid, provider_uuid):
        """Get provider details

        Get detailed information on a specific provider

        """
        provider = models.Provider.query.filter_by(
            organization_id=org_uuid, id=provider_uuid
        ).one()
        return provider

    @api.response(204)
    def delete(self, org_uuid, provider_uuid):
        """Delete platform

        Delete a resource platform from an organization
        """
        models.Provider.query.filter_by(
            organization_id=org_uuid, id=provider_uuid
        ).delete()
        db.session.commit()
