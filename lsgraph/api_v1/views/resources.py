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

from collections import defaultdict
from flask.views import MethodView
from flask import g
from flask_smorest import abort
from marshmallow import ValidationError
import pdb

from lsgraph import models
from lsgraph.models import db
from lsgraph.api_v1 import api
from lsgraph.api_v1.schemas import (
    ResourceQuerySchema,
    NewResourceSchema,
    ResourceSchema,
    ResourceManySchema,
    NewOfferingSchema,
    OfferingSchema,
    OfferingManySchema,
)
from ._shared import authorized_org


def prepare_provider(provider):
    return {
        "id": provider.id,
        "name": provider.name,
        "description": provider.description,
        "logo": provider.logo,
        "url": provider.url,
    }


def prepare_platform(platform):
    return {
        "id": platform.id,
        "name": platform.name,
        "description": platform.description,
        "logo": platform.logo,
        "url": platform.url,
        "subscription": platform.subscription,
        "free_trial": platform.free_trial,
    }


def prepare_offering(offering, formats):
    return {
        "id": offering.id,
        "name": offering.name,
        "format": {
            "id": formats[offering.format_id].id,
            "name": formats[offering.format_id].name,
            "description": formats[offering.format_id].description,
            "logo": formats[offering.format_id].logo,
        },
        "start_date": offering.start_date,
        "end_date": offering.end_date,
        "pace_min_hrs_per_week": offering.pace_min_hrs_per_week,
        "pace_max_hrs_per_week": offering.pace_max_hrs_per_week,
        "pace_num_weeks": offering.pace_num_weeks,
        "elapsed_duration": offering.elapsed_duration,
        "min_taught_duration": offering.min_taught_duration,
        "max_taught_duration": offering.max_taught_duration,
        "language": offering.language,
        "cc_language": offering.cc_language,
        "free": offering.free,
        "free_audit": offering.free_audit,
        "paid": offering.paid,
        "certificate": offering.certificate,
        "quality": offering.quality,
        "instructors": offering.instructors,
        "retired": offering.retired,
    }


def get_resources(org_uuid, resources):
    """Get resources"""
    # Get IDs
    resource_ids = [i.id for i in resources]
    provider_ids = list(set([i.provider_id for i in resources]))
    platform_ids = list(set([i.platform_id for i in resources]))
    # Get providers
    providers = (
        models.Provider.query.filter(models.Provider.organization_id == org_uuid)
        .filter(models.Provider.id.in_(provider_ids))
        .all()
    )
    providers = {i.id: i for i in providers}
    # Get platforms
    platforms = (
        models.Platform.query.filter(models.Platform.organization_id == org_uuid)
        .filter(models.Platform.id.in_(platform_ids))
        .all()
    )
    platforms = {i.id: i for i in platforms}
    # Get offerings
    offerings = (
        models.Offering.query.filter(models.Offering.organization_id == org_uuid)
        .filter(models.Offering.resource_id.in_(resource_ids))
        .all()
    )
    # Get formats
    format_ids = list(set([i.format_id for i in offerings]))
    formats = (
        models.Format.query.filter(models.Format.organization_id == org_uuid)
        .filter(models.Format.id.in_(format_ids))
        .all()
    )
    formats = {i.id: i for i in formats}
    resource_offerings = defaultdict(list)
    for offering in offerings:
        resource_offerings[offering.resource_id].append(offering)
    output = []
    for resource in resources:
        output.append(
            {
                "id": resource.id,
                "name": resource.name,
                "short_description": resource.short_description,
                "description": resource.description,
                "url": resource.url,
                "provider": prepare_provider(providers[resource.provider_id]),
                "platform": prepare_platform(platforms[resource.platform_id]),
                "platform_level": resource.platform_level,
                "alt_id": resource.alt_id,
                "syllabus": resource.syllabus,
                "learning_outcomes": resource.learning_outcomes,
                "prerequisite_knowledge": resource.prerequisite_knowledge,
                "retired": resource.retired,
                "offerings": [
                    prepare_offering(i, formats)
                    for i in resource_offerings[resource.id]
                ],
            }
        )
    return output


def create_new_resource(resource_data, org_uuid):
    """Create new resource"""
    provider = models.Provider.query.filter_by(
        id=resource_data["provider"], organization_id=org_uuid
    ).one()
    platform = models.Platform.query.filter_by(
        id=resource_data["platform"], organization_id=org_uuid
    ).one()
    new_resource = models.Resource(
        name=resource_data["name"],
        short_description=resource_data["short_description"],
        description=resource_data.get("description"),
        url=resource_data.get("url"),
        provider_id=provider.id,
        platform_id=platform.id,
        platform_level=resource_data.get("platform_level"),
        alt_id=resource_data.get("alt_id"),
        syllabus=resource_data.get("syllabus"),
        learning_outcomes=resource_data.get("learning_outcomes"),
        prerequisite_knowledge=resource_data.get("prerequisite_knowledge"),
        retired=resource_data.get("retired"),
        organization_id=org_uuid,
    )
    db.session.add(new_resource)
    db.session.commit()
    return new_resource


def create_new_offering(offering_data, org_uuid, resource_uuid):
    """Create a new offering"""
    format = models.Format.query.filter_by(
        id=offering_data["format"],
        organization_id=org_uuid,
    ).one()
    new_offering = models.Offering(
        name=offering_data["name"],
        resource_id=resource_uuid,
        format_id=format.id,
        start_date=offering_data["start_date"],
        end_date=offering_data["end_date"],
        pace_min_hrs_per_week=offering_data["pace_min_hrs_per_week"],
        pace_max_hrs_per_week=offering_data["pace_max_hrs_per_week"],
        pace_num_weeks=offering_data["pace_num_weeks"],
        elapsed_duration=offering_data["elapsed_duration"],
        min_taught_duration=offering_data["min_taught_duration"],
        max_taught_duration=offering_data["max_taught_duration"],
        language=offering_data["language"],
        cc_language=offering_data["cc_language"],
        free=offering_data["free"],
        free_audit=offering_data["free_audit"],
        paid=offering_data["paid"],
        certificate=offering_data["certificate"],
        quality=offering_data["quality"],
        instructors=offering_data["instructors"],
        organization_id=org_uuid,
        retired=offering_data["retired"],
    )
    db.session.add(new_offering)
    db.session.commit()
    return prepare_offering(new_offering, {format.id: format})


@api.route("organizations/<org_uuid>/resources/")
class ResourcesAPI(MethodView):
    decorators = [authorized_org]

    @api.arguments(ResourceQuerySchema, location="query")
    @api.response(200, ResourceManySchema)
    def get(self, query_data, org_uuid):
        """Get resources

        Get a list of all resources for an organization

        """
        resources = models.Resource.query.filter_by(organization_id=org_uuid).all()
        resources = get_resources(org_uuid, resources)
        return {"resources": resources}

    @api.arguments(NewResourceSchema, location="json")
    @api.response(200, ResourceSchema)
    def post(self, resource_data, org_uuid):
        """Add resource

        Create a new resource for an organization

        """
        new_resource = create_new_resource(resource_data, org_uuid)
        return get_resources(org_uuid, [new_resource])[0]


@api.route("organizations/<org_uuid>/resources/<resource_uuid>/")
class ResourcesDetailAPI(MethodView):
    decorators = [authorized_org]

    @api.response(200, ResourceSchema)
    def get(self, org_uuid, resource_uuid):
        """Get resource details

        Get detailed information on a specific resource

        """
        resource = models.Resource.query.filter_by(
            id=resource_uuid, organization_id=org_uuid
        ).one()
        resource = get_resources(org_uuid, [resource])[0]
        return resource

    @api.response(204)
    def delete(self, org_uuid, resource_uuid):
        """Delete resource

        Delete a resource from the organization
        """
        resource = models.Resource.query.filter_by(
            id=resource_uuid, organization_id=org_uuid
        ).one()
        resource.retired = True
        db.session.add(resource)
        db.session.commit()


@api.route("organizations/<org_uuid>/resources/<resource_uuid>/offerings/")
class ResourceOfferingsAPI(MethodView):
    decorators = [authorized_org]

    @api.arguments(NewOfferingSchema, location="json")
    @api.response(200, OfferingSchema)
    def post(self, offering_data, org_uuid, resource_uuid):
        """Add resource offering

        Create a new offering for a resource

        """
        new_offering = create_new_offering(offering_data, org_uuid, resource_uuid)
        return new_offering


@api.route(
    "organizations/<org_uuid>/resources/<resource_uuid>/offerings/<offering_uuid>/"
)
class ResourceOfferingDetailAPI(MethodView):
    decorators = [authorized_org]

    @api.response(204)
    def delete(self, org_uuid, resource_uuid, offering_uuid):
        """Delete offering

        Delete an offering from a resource"""
        offering = models.Offering.query.filter_by(
            id=offering_uuid, resource_id=resource_uuid, organization_id=org_uuid
        ).one()
        offering.retired = True
        db.session.add(offering)
        db.session.commit()
