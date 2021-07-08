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
from lsgraph.api_v1.schemas import ProfileSchema, ProfileManySchema, ProfileSkillsSchema
from lsgraph.api_v1.views.skills import get_root_id


def get_levels(org_uuid):
    """Get level map information"""
    levels = models.Level.query.filter_by(organization_id=org_uuid).all()
    levels = [(i.name, i.cutoff) for i in levels]
    levels.sort(key=lambda x: x[1])
    return levels


def get_level_name(levels, val):
    """Convert an numeric level to a text label"""
    levels.sort(key=lambda x: x[1])
    for (label, cutoff), (_, next_cutoff) in zip(levels, levels[1:]):
        if val < cutoff:
            return ""
        if val < next_cutoff:
            return label
    return levels[-1][0]


def build_output(profile, skills, levels):
    """Convert output to dict"""
    output = {
        "id": profile.id,
        "name": profile.name,
        "description": profile.description,
        "user_id": profile.user_id,
        "type": profile.type,
        "previous_versions": [],
    }
    output["skills"] = [
        {
            "skill": i.skill_id,
            "level_name": get_level_name(levels, i.level),
            "level": i.level,
        }
        for i in skills
    ]
    return output


def get_profile(org_uuid, profile_uuid):
    """Get detailed information on one profile"""
    levels = get_levels(org_uuid)
    profile = models.Profile.query.filter_by(
        organization_uuid=org_uuid, id=profile_uuid
    ).one()
    skills = models.ProfileSkill.query.filter_by(profile_uuid=profile.id).all()
    return build_output(profile, skills, levels)


def get_profiles(org_uuid, types=None, user=False):
    """Get all profiles for an organization

    The results returned are restricted to exclude user profiles by default
    and only most recent versions

    TODO: Add exclusion of older versions"""
    levels = get_levels(org_uuid)
    profiles_query = models.Profile.query.filter_by(
        organization_id=org_uuid,
    )
    if types:
        profiles_query = profiles_query.filter(models.Profile.type.in_(types))
    if user:
        profiles_query = profiles_query.filter(models.Profile.user_id.isnot(None))
    else:
        profiles_query = profiles_query.filter(models.Profile.user_id.is_(None))
    profiles = profiles_query.all()
    skills = models.ProfileSkill.query.filter(
        models.ProfileSkill.profile_id.in_([i.id for i in profiles])
    ).all()
    grouped_skills = defaultdict(list)
    for i in skills:
        grouped_skills[i.profile_id].append(i)
    return [build_output(p, grouped_skills[p.id], levels) for p in profiles]


def create_new_profile(org_uuid, profile_data):
    """Create a new profile"""
    skill_map = validate_skills(org_uuid, profile_data["skills"])
    new_profile = models.Profile(
        name=profile_data["name"],
        description=profile_data["description"],
        organization_id=org_uuid,
        type=profile_data["type"],
    )
    db.session.add(new_profile)
    db.session.commit()
    skills = add_skills(org_uuid, new_profile.id, skill_map)
    output = {
        "id": new_profile.id,
        "name": new_profile.name,
        "description": new_profile.description,
        "user_id": new_profile.user_id,
        "type": new_profile.type,
        "previous_versions": [],
        "skills": skills,
    }
    return output


def validate_skills(org_uuid, profile_skills):
    """Validate and prep skills to database"""
    skill_map = []
    levels = get_levels(org_uuid)
    root_ids = get_root_id([i["skill"] for i in profile_skills])
    for s in profile_skills:
        # Check skill permissions
        if root_ids[s["skill"]] != g.organizations[org_uuid].root_skill_id:
            abort(403, message="Skill is not valid for organization")
        # Check levels
        if s.get("level", False):
            if not (levels[0][1] <= s["level"] <= levels[-1][1]):
                abort(403, message=f"Level is out of range: {s['level']}")
            level = s["level"]
        else:
            match = [i for i in levels if i[0] == s["level_name"]]
            if len(match) != 1:
                abort(403, message="Level name not recognized")
            level = match[0][1]
        skill_map.append((s["skill"], level))
    return skill_map


def add_skills(org_id, profile_id, skill_map):
    """Add skills to a profile"""
    levels = get_levels(org_id)
    new_profile_skills = []
    for skill_id, level in skill_map:
        new_profile_skill = models.ProfileSkill(
            profile_id=profile_id,
            skill_id=skill_id,
            level=level,
        )
        db.session.add(new_profile_skill)
        new_profile_skills.append(new_profile_skill)
    db.session.commit()
    output = [
        {
            "skill": ns.skill_id,
            "level_name": get_level_name(levels, ns.level),
            "level": ns.level,
        }
        for ns in new_profile_skills
    ]
    return output


@api.route("organizations/<org_uuid>/profiles/")
class ProfilesAPI(MethodView):
    @api.response(200, ProfileManySchema)
    def get(self, org_uuid):
        """Get profiles"""
        profiles = get_profiles(org_uuid)
        return {"profiles": profiles}

    @api.arguments(ProfileSchema, location="json")
    @api.response(200, ProfileSchema)
    def post(self, profile_data, org_uuid):
        """Add profile"""
        new_profile = create_new_profile(org_uuid, profile_data)
        return new_profile


@api.route("organizations/<org_uuid>/profiles/<profile_uuid>/")
class ProfilesDetailAPI(MethodView):
    @api.response(200, ProfileSchema)
    def get(self, org_uuid, profile_uuid):
        """Get profile details"""
        profile = get_profile(org_uuid, profile_uuid)
        return profile

    @api.response(204)
    def delete(self, org_uuid, profile_uuid):
        """Delete profile"""
        profile = models.Profile.query.filter_by(
            organization_id=org_uuid, id=profile_uuid
        ).one()
        # Delete skills
        models.ProfileSkill.query.filter_by(profile_id=profile.id).delete()
        # Delete profile
        db.session.delete(profile)
        db.session.commit()


@api.route("organizations/<org_uuid>/profiles/<profile_uuid>/skills/")
class ProfileSkillsAPI(MethodView):
    @api.response(200, ProfileSkillsSchema)
    def get(self, org_uuid, profile_uuid):
        """Get profile skills"""
        skills = get_profile(org_uuid, profile_uuid)["skills"]
        return {"skills": skills}

    @api.arguments(ProfileSkillsSchema, location="json")
    @api.response(200, ProfileSkillsSchema)
    def post(self, skills_data, org_uuid, profile_uuid):
        """Update profile skills"""
        profile = models.Profile.query.filter_by(
            organization_id=org_uuid, id=profile_uuid
        ).one()
        skill_map = validate_skills(org_uuid, skills_data["skills"])
        added_skills = add_skills(org_uuid, profile_uuid, skill_map)
        return {"skills": added_skills}


@api.route("organizations/<org_uuid>/profiles/<profile_uuid>/skills/<skill_uuid>/")
class ProfileSkillsDetailAPI(MethodView):
    @api.response(204)
    def delete(self, org_uuid, profile_uuid, skill_uuid):
        """Delete profile skills"""
        skill = (
            models.ProfileSkill.query.filter_by(profile_id=profile_uuid)
            .filter_by(skill_id=skill_uuid)
            .all()
        )
        if len(skill) == 0:
            abort(404, message="Skill not found")
        for i in skill:
            db.session.delete(i)
        db.session.commit()
