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
from lsgraph.api_v1.schemas import OrganizationSchema, OrganizationManySchema


def create_root_skill():
    root = models.Skill(name="Root", description="")
    db.session.add(root)
    db.session.commit()
    return root.id


def save_level_mapping(org_id, mapping):
    for name, cutoff in mapping.items():
        db.session.add(models.Level(organization_id=org_id, name=name, cutoff=cutoff))
    db.session.commit()


def create_whole_org_group(org_id, name):
    new_group = models.Group(
        name=f"{name}:All members", organization_id=org_id, whole_organization=True
    )
    db.session.add(new_group)
    db.session.commit()


def create_new_organization(org_data):
    root_skill_id = create_root_skill()
    new_org = models.Organization(
        name=org_data["name"], customer_id=g.customer.id, root_skill_id=root_skill_id
    )
    db.session.add(new_org)
    db.session.commit()
    save_level_mapping(new_org.id, org_data["level_map"])
    create_whole_org_group(new_org.id, org_data["name"])
    output = {
        "id": new_org.id,
        "name": new_org.name,
        "root_skill": {"id": root_skill_id},
    }
    return output


@api.route("organizations/")
class OrganizationsAPI(MethodView):
    @api.response(200, OrganizationManySchema)
    def get(self):
        """Get organizations"""
        orgs = models.Organization.query.filter_by(customer_id=g.customer.id).all()
        return {"organizations": orgs}

    @api.arguments(OrganizationSchema, location="json")
    @api.response(200, OrganizationSchema)
    def post(self, org_data):
        """Add organization"""
        new_org = create_new_organization(org_data)
        return new_org


@api.route("organizations/<org_uuid>/")
class OrganizationsDetailAPI(MethodView):
    @api.response(200, OrganizationSchema)
    def get(self, org_uuid):
        """Get organization detail"""
        org = models.Organization.query.filter_by(id=org_uuid).one()
        levels = models.Level.query.filter_by(organization_id=org_uuid).all()
        levels.sort(key=lambda x: x.cutoff)
        output = {
            "name": org.name,
            "root_skill": {"id": org.root_skill_id},
            "level_map": {i.name: i.cutoff for i in levels},
        }
        return output

    @api.response(204)
    def delete(self, org_uuid):
        """Delete organization"""
        abort(500)
