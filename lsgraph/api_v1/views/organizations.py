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
from flask import abort, current_app, g, jsonify, request
from marshmallow import ValidationError
import pdb

from lsgraph import models
from lsgraph.models import db
from ..schemas import OrganizationSchema


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
        name=org_data["name"], customer_id=g.customer, root_skill_id=root_skill_id
    )
    db.session.add(new_org)
    db.session.commit()
    save_level_mapping(new_org.id, org_data["level_map"])
    create_whole_org_group(new_org.id, org_data["name"])
    return new_org


class OrganizationsAPI(MethodView):
    org_schema = OrganizationSchema()
    orgs_schema = OrganizationSchema(many=True)

    def get(self):
        """Organizations endpoint

        .. :quickref: Get organizations

        """
        orgs = models.Organization.query.filter_by(customer_id=g.customer).all()
        return jsonify({"organizations": self.orgs_schema.dump(orgs)})

    def post(self):
        """Organization creation endpoint

        .. :quickref: Create new organization

        """
        try:
            data = self.org_schema.load(request.json)
        except ValidationError as err:
            return {"status_code": 422, "status_message": err.messages}, 422
        new_org = create_new_organization(data)
        return jsonify(self.org_schema.dump(new_org))


class OrganizationsDetailAPI(MethodView):
    def get(self, org_uuid):
        """Organization detail endpoint

        .. :quickref: Get organization detail

        """
        return "Hello"

    def put(self, org_uuid):
        """Organization update endpoint

        .. :quickref: Update organization

        """
        return "Hello"

    def delete(self, org_uuid):
        """Organization deletion endpoint

        .. :quickref: Delete organization

        """
        return "Hello"
