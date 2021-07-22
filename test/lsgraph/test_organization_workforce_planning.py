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


from datetime import datetime
import pdb
import pytest

from .test_profile import create_profile
from .test_user_job_recommendations import update_profile


def test_workforce_planning_list(lsgraph_client, test_data_2org):
    (c1, org1, collection1), (c2, org2, collection2) = test_data_2org
    customer_id, access_id, access_secret = c1
    org_id = org1["id"]
    # Create profiles
    profiles = []
    for i in range(4):
        new_profile = create_profile(
            lsgraph_client,
            test_data_2org[0],
            skills=[
                {"skill": i["id"], "level_name": "Beginner"}
                for i in collection1["skills"][-2 - i :]
            ],
        )
        profiles.append(new_profile)
    # Update skills for users
    users = {}
    for i, user in enumerate(collection1["users"]):
        updated_skills = update_profile(
            lsgraph_client,
            test_data_2org[0],
            user["profile"],
            [
                {"skill": i["id"], "level_name": "Beginner"}
                for i in collection1["skills"][-3 - i : -1]
            ],
        )
        users[user["id"]] = updated_skills
    # Workforce planning
    response = lsgraph_client.post(
        f"/api/v1/organizations/{org_id}/workforce_planning/",
        headers={"X-API-Key": access_id, "X-Auth-Token": access_secret},
        json={
            "users": [i["id"] for i in collection1["users"]],
            "targets": [
                {"profile": i["id"], "number_needed": 1, "max_training": 100}
                for i in profiles
            ],
        },
    )
    # Test results
    assert response.status_code == 200
    assert "targets_by_user" in response.json
    assert "users_by_target" in response.json
    profile_ids = [i["id"] for i in profiles]
    user_ids = [i["id"] for i in collection1["users"]]
    for i in response.json["targets_by_user"]:
        assert i["user"] in user_ids
        for j in i["recommendations"]:
            assert j["profile"] in profile_ids


def test_workforce_planning_group(lsgraph_client, test_data_2org):
    (c1, org1, collection1), (c2, org2, collection2) = test_data_2org
    customer_id, access_id, access_secret = c1
    org_id = org1["id"]
    # Create profiles
    profiles = []
    for i in range(4):
        new_profile = create_profile(
            lsgraph_client,
            test_data_2org[0],
            skills=[
                {"skill": i["id"], "level_name": "Beginner"}
                for i in collection1["skills"][-2 - i :]
            ],
        )
        profiles.append(new_profile)
    # Update skills for users
    users = {}
    for i, user in enumerate(collection1["users"]):
        updated_skills = update_profile(
            lsgraph_client,
            test_data_2org[0],
            user["profile"],
            [
                {"skill": i["id"], "level_name": "Beginner"}
                for i in collection1["skills"][-3 - i : -1]
            ],
        )
        users[user["id"]] = updated_skills
    # Get whole org group
    response = lsgraph_client.get(
        f"/api/v1/organizations/{org_id}/groups/",
        headers={"X-API-Key": access_id, "X-Auth-Token": access_secret},
    )
    group_id = [i["id"] for i in response.json["groups"] if i["whole_organization"]][0]
    # Workforce planning
    response = lsgraph_client.post(
        f"/api/v1/organizations/{org_id}/workforce_planning/",
        headers={"X-API-Key": access_id, "X-Auth-Token": access_secret},
        json={
            "groups": [group_id],
            "targets": [
                {"profile": i["id"], "number_needed": 1, "max_training": 100}
                for i in profiles
            ],
        },
    )
    # Test results
    assert response.status_code == 200
    assert "targets_by_user" in response.json
    assert "users_by_target" in response.json
    profile_ids = [i["id"] for i in profiles]
    user_ids = [i["id"] for i in collection1["users"]]
    for i in response.json["targets_by_user"]:
        assert i["user"] in user_ids
        for j in i["recommendations"]:
            assert j["profile"] in profile_ids
