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
from lsgraph.api_v1.schemas import SkillSchema, SkillManySchema


def create_new_skill(skill_data):
    root_skill_id = (
        models.Organization.query.filter_by(customer_id=g.customer.id)
        .all()[0]
        .root_skill_id
    )
    root_skills = get_root_id(skill_data["parent"])
    if (skill_data["parent"] != root_skill_id) and root_skills.get(
        skill_data["parent"], False
    ) != root_skill_id:
        return Exception("Skill is not valid for organization")
    creator_id = None
    if skill_data.get("creator", False):
        creator_id = skill_data["creator"]["id"]
    new_skill = models.Skill(
        name=skill_data["name"],
        description=skill_data["description"],
        personal=skill_data["personal"],
        creator_id=creator_id,
    )
    db.session.add(new_skill)
    db.session.commit()
    db.session.add(
        models.SkillInclude(child_id=new_skill.id, parent_id=skill_data["parent"])
    )
    db.session.commit()
    return new_skill


def get_descendant_skills(skill_id):
    """Get all skills that originate from skill_id"""
    if not isinstance(skill_id, (list, tuple)):
        skill_id = [
            skill_id,
        ]
    topq = db.session.query(models.SkillInclude).filter(
        models.SkillInclude.parent_id.in_(skill_id)
    )
    topq = topq.cte("cte", recursive=True)
    bottomq = db.session.query(models.SkillInclude)
    bottomq = bottomq.join(topq, models.SkillInclude.parent_id == topq.c.child_id)
    recursive_q = topq.union(bottomq)
    final_q = db.session.query(recursive_q)
    children = defaultdict(list)
    for _, parent, child in final_q.all():
        children[parent].append(child)
    descendants = defaultdict(list)

    def collect_descendants(skill_id, children):
        output = []
        if skill_id not in children:
            return output
        output.extend(children[skill_id])
        for s_id in children[skill_id]:
            output.extend(collect_descendants(s_id, children))
        return output

    all_descendants = {s_id: collect_descendants(s_id, children) for s_id in skill_id}
    direct_children = {k: v for k, v in children.items() if k in skill_id}
    return all_descendants, direct_children


def get_ancestor_skills(skill_id):
    """Get all skills connecting root_id to skill_id"""
    if not isinstance(skill_id, (list, tuple)):
        skill_id = [
            skill_id,
        ]
    topq = db.session.query(models.SkillInclude).filter(
        models.SkillInclude.child_id.in_(skill_id)
    )
    topq = topq.cte("cte", recursive=True)
    bottomq = db.session.query(models.SkillInclude)
    bottomq = bottomq.join(topq, models.SkillInclude.child_id == topq.c.parent_id)
    recursive_q = topq.union(bottomq)
    final_q = db.session.query(recursive_q)
    parents = {child: parent for _, parent, child in final_q.all()}
    output = defaultdict(list)

    def build_path(output, skill_id, parents):
        extended = False
        for s_id in skill_id:
            if s_id in output:
                current = output[s_id][-1]
            else:
                current = s_id
            if current in parents:
                extended = True
                output[s_id].append(parents[current])
        if extended:
            build_path(output, skill_id, parents)

    build_path(output, skill_id, parents)
    return output


def get_root_id(skill_id):
    """Get the root IDs for a collection of skills"""
    output = get_ancestor_skills(skill_id)
    output = {k: v[-1] for k, v in output.items()}
    return output


def get_skill_details(skill_ids):
    """Get path, parent, child skills and number of descendants"""
    descendants, children = get_descendant_skills(skill_ids)
    ancestors = get_ancestor_skills(skill_ids)
    # Get skill details
    to_lookup = skill_ids[:]
    for k, v in children.items():
        to_lookup.extend(v)
    for k, v in ancestors.items():
        to_lookup.extend(v)
    to_lookup = list(set(to_lookup))
    skills = models.Skill.query.filter(models.Skill.id.in_(to_lookup)).all()
    skills = {i.id: i for i in skills}
    # Construct data set
    output = {
        skills[i].id: {
            "id": skills[i].id,
            "name": skills[i].name,
            "description": skills[i].description,
            "personal": skills[i].personal,
            "creator": skills[i].creator_id,
        }
        for i in skill_ids
    }
    for i in skill_ids:
        output[i]["path"] = "|".join([skills[j].name for j in reversed(ancestors[i])])
        output[i]["parent"] = ancestors[i][0] if ancestors[i] else None
        output[i]["child_skills"] = [
            {"id": skills[j].id, "name": skills[j].name} for j in children.get(i, [])
        ]
        output[i]["num_descendants"] = len(descendants[i])
    return output


@api.route("organizations/<org_uuid>/skills/")
class SkillsAPI(MethodView):
    @api.response(200, SkillManySchema)
    def get(self, org_uuid):
        """Get skills

        Get a list of all skills for the organization"""
        root_skill = (
            models.Skill.query.filter(
                models.Skill.id == models.Organization.root_skill_id
            )
            .filter(models.Organization.id == org_uuid)
            .one()
        )
        descendants, children = get_descendant_skills(root_skill.id)
        all_skill_ids = [
            root_skill.id,
        ] + descendants[root_skill.id]
        skill_output = get_skill_details(all_skill_ids)
        return {"skills": skill_output.values()}

    @api.arguments(SkillSchema, location="json")
    @api.response(200, SkillSchema)
    def post(self, skill_data, org_uuid):
        """Add a skill

        Add a new skill for the organization"""
        new_skill = create_new_skill(skill_data)
        return new_skill


@api.route("organizations/<org_uuid>/skills/<skill_uuid>/")
class SkillsDetailAPI(MethodView):
    @api.response(200, SkillSchema)
    def get(self, org_uuid, skill_uuid):
        """Get skill details

        Get detailed information on a specific skill"""
        abort(500)

    # @api.response(204)
    # def delete(self, org_uuid, skill_uuid):
    #     """Delete skill

    #     Delete a specific skill"""
    #     abort(500)
