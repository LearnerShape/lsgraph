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
import numpy as np
import pdb

from lsgraph import models
from lsgraph.models import db
from lsgraph.api_v1 import api
from lsgraph.api_v1.schemas import (
    UserSchema,
    UserManySchema,
    JobRecommendationQuerySchema,
    JobRecommendationManySchema,
)
from lsgraph.api_v1.views.profiles import get_level_name
from ._shared import authorized_org


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


def collect_profile_information(job_rec, org_uuid, user_uuid):
    """Collect information needed for job recommendation"""
    user_profile = models.Profile.query.filter_by(
        organization_id=org_uuid, user_id=user_uuid
    ).one()
    query = models.Profile.query.filter_by(organization_id=org_uuid)
    if job_rec.get("profiles"):
        profiles = query.filter(models.Profile.id.in_(job_rec["profiles"])).all()
    else:
        profiles = query.filter(models.Profile.type.in_(job_rec["profile_types"])).all()
    profile_ids = [i.id for i in profiles]
    profile_ids.append(user_profile.id)
    profile_ids = list(set(profile_ids))
    profile_skills = models.ProfileSkill.query.filter(
        models.ProfileSkill.profile_id.in_(profile_ids)
    ).all()
    skill_ids = [i.skill_id for i in profile_skills]
    skill_ids = list(set(skill_ids))
    skills = models.Skill.query.filter(models.Skill.id.in_(skill_ids)).all()
    return user_profile, profiles, profile_skills, skills


class JobRecommendation:
    def __init__(
        self,
        levels,
        multiplier_threshold=1.0,
        multiplier_baseline=0.0,
        multiplier_offset=np.sqrt(2),
        multiplier_power=2,
        max_skills=5,
    ):
        """Initialise with parameters

        skill_rank: Dictionary mapping skill levels to numerical values
        Variables determining how embedding euclidean distances are
            converted to a multiplier on learning rate:
        multiplier_threshold: The maximum distance before the multiplier
            is set to baseline
        multiplier_baseline:  The multiplier used when multiplier reaches
            the threshold (distant skills should contribute little or
            nothing towards learning)
        multiplier_offset:    The minimum point for the learning speed
            conversion
        multiplier_power:     An exponent applied to the learning
            speed conversion
        max_skills:           The maximum number of close skills that modify
            required learning
        """
        self.levels = levels
        level_values = [i[1] for i in levels]
        self.max_skill_gap = max(level_values) - min(level_values)
        self.multiplier_threshold = multiplier_threshold
        self.multiplier_baseline = multiplier_baseline
        self.multiplier_offset = multiplier_offset
        self.multiplier_power = multiplier_power
        self.max_skills = max_skills

        self.profile_skills = defaultdict(dict)
        self.skills = {}

    def job_by_distance(self, source_profile, target_profile):
        """Convert a skill gap to a distance considering how
        skills are related"""
        source_skills = self.profile_skills[source_profile.id]
        target_skills = self.profile_skills[target_profile.id]
        total_distance = 0
        profile_sum = 0
        for t_id, t_level in target_skills.items():
            profile_sum += t_level
            s_level = source_skills.get(t_id, 0)
            if s_level >= t_level:
                continue
            all_multipliers = [
                (
                    self._get_learning_speed(self.skills[t_id], self.skills[i]),
                    j,
                )
                for i, j in source_skills.items()
                if (t_id != i)
            ]
            all_multipliers.sort(key=lambda x: x[0], reverse=True)
            d = t_level - s_level
            for multiplier, level in all_multipliers[: self.max_skills]:
                level_multiplier = min(t_level, level) - min(s_level, level)
                level_multiplier /= self.max_skill_gap
                d -= multiplier * d * level_multiplier
            total_distance += d
        if profile_sum == 0:
            fit = 100
        else:
            fit = 100 * (profile_sum - total_distance) / profile_sum
        fit = round(fit, 2)
        total_distance = round(total_distance, 2)
        return {
            "profile": self._build_profile_output(target_profile, target_skills),
            "distance": total_distance,
            "fit": fit,
        }

    def _build_profile_output(self, profile, skills):
        """Convert profile details to schema"""
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
                "skill": skill_id,
                "level_name": get_level_name(self.levels, skill_level),
                "level": skill_level,
            }
            for skill_id, skill_level in skills.items()
        ]
        return output

    def _get_learning_speed(self, embed1, embed2):
        """From two embeddings generate a training speed multiplier"""
        if (embed1 is None) or (embed2 is None):
            return self.multiplier_baseline
        d = np.linalg.norm(embed1 - embed2)
        if d > self.multiplier_threshold:
            return self.multiplier_baseline
        y = (self.multiplier_offset - d) / self.multiplier_offset
        y = y ** self.multiplier_power
        return y

    def multiple_jobs_by_distance(
        self, user_profile, target_profiles, profile_skills, skills
    ):
        """Evaluate distance for multiple target skill profiles"""
        for i in profile_skills:
            self.profile_skills[i.profile_id][i.skill_id] = i.level
        self.skills.update({i.id: i.skill_embedding for i in skills})
        results = []
        for ts in target_profiles:
            results.append(self.job_by_distance(user_profile, ts))
        results.sort(key=lambda x: x["fit"], reverse=True)
        return results


def job_recommendation(job_rec, org_uuid, user_uuid):
    """Generate job recommendations"""
    user_profile, profiles, profile_skills, skills = collect_profile_information(
        job_rec, org_uuid, user_uuid
    )
    levels = models.Level.query.filter_by(organization_id=org_uuid).all()
    levels = [(i.name, i.cutoff) for i in levels]
    levels.sort(key=lambda x: x[1])
    recommendation = JobRecommendation(levels)
    results = recommendation.multiple_jobs_by_distance(
        user_profile, profiles, profile_skills, skills
    )
    return results


def get_user_details(org_id, user_id=None):
    """Get all users for an organization"""
    users = models.User.query.filter_by(organization_id=org_id)
    if user_id:
        users = users.filter(models.User.id.in_(user_id))
    users = users.all()
    profiles = models.Profile.query.filter(
        models.Profile.user_id.in_([i.id for i in users])
    ).all()
    profiles = {i.user_id: i.id for i in profiles}
    output = [
        {"id": i.id, "email": i.email, "name": i.name, "profile": profiles[i.id]}
        for i in users
    ]
    return output


@api.route("organizations/<org_uuid>/users/")
class UsersAPI(MethodView):
    decorators = [authorized_org]

    @api.response(200, UserManySchema)
    def get(self, org_uuid):
        """Get users

        Get a list of all users within the organization"""
        users = get_user_details(org_uuid)
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
    decorators = [authorized_org]

    @api.response(200, UserSchema)
    def get(self, org_uuid, user_uuid):
        """Get user details

        Get detailed information on a specific user"""
        return get_user_details(
            org_uuid,
            [
                user_uuid,
            ],
        )

    # @api.response(204)
    # def delete(self, org_uuid, user_uuid):
    #     """Delete user

    #     Delete a specific user from the organization"""
    #     abort(500)


@api.route("organizations/<org_uuid>/users/<user_uuid>/job_recommendations/")
class JobRecommendationAPI(MethodView):
    decorators = [authorized_org]

    @api.arguments(JobRecommendationQuerySchema, location="json")
    @api.response(200, JobRecommendationManySchema)
    def post(self, job_rec, org_uuid, user_uuid):
        """Get job recommendations

        Generate job recommendations for the user"""
        recommendations = job_recommendation(job_rec, org_uuid, user_uuid)
        return {"recommendations": recommendations}
