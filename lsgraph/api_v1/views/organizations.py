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
from lsgraph.api_v1.schemas import (
    OrganizationSchema,
    OrganizationManySchema,
    WorkforcePlanningQuerySchema,
    WorkforcePlanningSchema,
)
from lsgraph.api_v1.views.users import JobRecommendation


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


def get_source_profiles(query_data, org_id):
    """Expand groups into users/source profiles"""
    if query_data.get("groups"):
        member_profiles = (
            models.Profile.query.filter(
                models.Profile.user_id == models.GroupMember.user_id
            )
            .filter(models.GroupMember.group_id.in_(query_data["groups"]))
            .filter(models.GroupMember.group_id == models.Group.id)
            .filter(models.Group.organization_id == org_id)
            .all()
        )
        return member_profiles
    user_profiles = (
        models.Profile.query.filter(models.Profile.organization_id == org_id)
        .filter(models.Profile.user_id.in_(query_data["users"]))
        .all()
    )
    return user_profiles


def collect_profile_information(query_data, source_profiles, org_id):
    """Get all needed profile information"""
    target_profile_ids = [i["profile"] for i in query_data["targets"]]
    target_profiles = (
        models.Profile.query.filter(models.Profile.organization_id == org_id)
        .filter(models.Profile.id.in_(target_profile_ids))
        .all()
    )
    profile_ids = [i.id for i in target_profiles]
    # Check that profiles belong to organization
    for i in target_profile_ids:
        if i not in profile_ids:
            abort(403)
    profile_ids.extend([i.id for i in source_profiles])
    profile_ids = list(set(profile_ids))
    profile_skills = models.ProfileSkill.query.filter(
        models.ProfileSkill.profile_id.in_(profile_ids)
    ).all()
    skill_ids = [i.skill_id for i in profile_skills]
    skill_ids = list(set(skill_ids))
    skills = models.Skill.query.filter(models.Skill.id.in_(skill_ids)).all()
    return target_profiles, profile_skills, skills


class WorkforcePlanner:
    """Optimize upskilling opportunities across a workforce"""

    def __init__(self):
        """Set initialization values for planning"""
        self.employees = []
        self.targets = []

    def add_employee(self, identifier):
        self.employees.append(identifier)

    def add_target(self, target):
        self.targets.append(target)

    def plan(self, job_rec):
        """Plan best target profiles for each employee"""
        distances = []
        employee_options = [0 for _ in range(len(self.employees))]
        target_options = [0 for _ in range(len(self.targets))]
        # Get distances
        distance_lookup = {}
        fit_lookup = {}
        for e_idx, e in enumerate(self.employees):
            distance_lookup[e] = {i["profile"]["id"]: i["distance"] for i in job_rec[e]}
            fit_lookup[e.user_id] = {i["profile"]["id"]: i["fit"] for i in job_rec[e]}

            for t_idx, t in enumerate(self.targets):
                d = distance_lookup[e][t["profile"]]
                if d > t["max_training"]:
                    continue
                distances.append((e_idx, t_idx, d))
                employee_options[e_idx] += 1
                target_options[t_idx] += 1
        distances.sort(key=lambda x: x[2], reverse=True)
        # Prune connections
        preserved_distances = []
        for d in distances:
            if (employee_options[d[0]] > len(self.targets)) and (
                target_options[d[1]] > self.targets[d[1]]["number_needed"]
            ):
                employee_options[d[0]] -= 1
                target_options[d[1]] -= 1
                continue
            preserved_distances.append(d)
        # Build results
        employee_targets = {
            i.user_id: {"user": i.user_id, "recommendations": []}
            for i in self.employees
        }
        target_employees = {
            i["profile"]: {"profile": i["profile"], "recommendations": []}
            for i in self.targets
        }
        for e_idx, t_idx, d in preserved_distances:
            e_id = self.employees[e_idx].user_id
            t_id = self.targets[t_idx]["profile"]
            employee_targets[e_id]["recommendations"].append(
                {"profile": t_id, "distance": d, "fit": fit_lookup[e_id][t_id]}
            )
            target_employees[t_id]["recommendations"].append(
                {"user": e_id, "distance": d, "fit": fit_lookup[e_id][t_id]}
            )
        for i in employee_targets:
            employee_targets[i]["recommendations"].sort(key=lambda x: x["distance"])
        for i in target_employees:
            target_employees[i]["recommendations"].sort(key=lambda x: x["distance"])
        return {
            "targets_by_user": employee_targets.values(),
            "users_by_target": target_employees.values(),
        }


def workforce_plan(query_data, org_id):
    """Create a workforce reskilling plan"""
    source_profiles = get_source_profiles(query_data, org_id)
    profiles, profile_skills, skills = collect_profile_information(
        query_data, source_profiles, org_id
    )
    levels = models.Level.query.filter_by(organization_id=org_id).all()
    levels = [(i.name, i.cutoff) for i in levels]
    levels.sort(key=lambda x: x[1])
    recommendation = JobRecommendation(levels)
    results = {}
    for source in source_profiles:
        results[source] = recommendation.multiple_jobs_by_distance(
            source, profiles, profile_skills, skills
        )
    workforce_planner = WorkforcePlanner()
    for source in source_profiles:
        workforce_planner.add_employee(source)
    for target in query_data["targets"]:
        workforce_planner.add_target(target)
    output_plan = workforce_planner.plan(results)
    return output_plan


@api.route("organizations/")
class OrganizationsAPI(MethodView):
    @api.response(200, OrganizationManySchema)
    def get(self):
        """Get organizations

        Get a list of all organizations"""
        orgs = models.Organization.query.filter_by(customer_id=g.customer.id).all()
        return {"organizations": orgs}

    @api.arguments(OrganizationSchema, location="json")
    @api.response(200, OrganizationSchema)
    def post(self, org_data):
        """Add organization

        Add a new organization to the customer account"""
        new_org = create_new_organization(org_data)
        return new_org


@api.route("organizations/<org_uuid>/")
class OrganizationsDetailAPI(MethodView):
    @api.response(200, OrganizationSchema)
    def get(self, org_uuid):
        """Get organization detail

        Get detailed information on a specific organization"""
        org = models.Organization.query.filter_by(id=org_uuid).one()
        levels = models.Level.query.filter_by(organization_id=org_uuid).all()
        levels.sort(key=lambda x: x.cutoff)
        output = {
            "name": org.name,
            "root_skill": {"id": org.root_skill_id},
            "level_map": {i.name: i.cutoff for i in levels},
        }
        return output

    # @api.response(204)
    # def delete(self, org_uuid):
    #     """Delete organization

    #     Delete a specific organization from the customer account"""
    #     abort(500)


@api.route("organizations/<org_uuid>/workforce_planning/")
class WorkforcePlanningAPI(MethodView):
    @api.arguments(WorkforcePlanningQuerySchema, location="json")
    @api.response(200, WorkforcePlanningSchema)
    def post(self, workforce_planning, org_uuid):
        """Workforce plan

        Create a workforce plan optimizing job recommendations
        across the organization"""
        plan = workforce_plan(workforce_planning, org_uuid)
        return plan
