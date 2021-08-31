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


def update_profile(lsgraph_client, org_details, profile_id, skills):
    """Update an existing profile"""
    (customer_id, access_id, access_secret), org, collection = org_details
    org_id = org["id"]
    skill_update = {
        "skills": skills,
    }
    response = lsgraph_client.post(
        f"/api/v1/organizations/{org_id}/profiles/{profile_id}/skills/",
        headers={"X-API-Key": access_id, "X-Auth-Token": access_secret},
        json=skill_update,
    )
    assert response.status_code == 200
    return response.json


def test_job_recommendation_list(lsgraph_client, test_data_2org):
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
    # Update skills for user
    update_profile(
        lsgraph_client,
        test_data_2org[0],
        collection1["users"][0]["profile"],
        [
            {"skill": i["id"], "level_name": "Beginner"}
            for i in collection1["skills"][-3:]
        ],
    )
    # Job recommendations
    user_id = collection1["users"][0]["id"]
    response = lsgraph_client.post(
        f"/api/v1/organizations/{org_id}/users/{user_id}/job_recommendations/",
        headers={"X-API-Key": access_id, "X-Auth-Token": access_secret},
        json={"profiles": [i["id"] for i in profiles]},
    )
    # Test results
    assert response.status_code == 200
    assert "recommendations" in response.json
    last_fit = 100
    for i, j in zip(profiles, response.json["recommendations"]):
        assert i["id"] == j["profile"]["id"]
        assert j["fit"] <= last_fit
        last_fit = j["fit"]


def test_job_recommendation_type(lsgraph_client, test_data_2org):
    (c1, org1, collection1), (c2, org2, collection2) = test_data_2org
    customer_id, access_id, access_secret = c1
    org_id = org1["id"]
    # Create profiles
    profiles = []
    time = datetime.now().strftime("%Y%M%d-%H%m%S-%f")
    for i in range(4):
        new_profile = create_profile(
            lsgraph_client,
            test_data_2org[0],
            skills=[
                {"skill": i["id"], "level_name": "Beginner"}
                for i in collection1["skills"][-2 - i :]
            ],
            profile_type=time,
        )
        profiles.append(new_profile)
    # Update skills for user
    update_profile(
        lsgraph_client,
        test_data_2org[0],
        collection1["users"][0]["profile"],
        [
            {"skill": i["id"], "level_name": "Beginner"}
            for i in collection1["skills"][-3:]
        ],
    )
    # Job recommendations
    user_id = collection1["users"][0]["id"]
    response = lsgraph_client.post(
        f"/api/v1/organizations/{org_id}/users/{user_id}/job_recommendations/",
        headers={"X-API-Key": access_id, "X-Auth-Token": access_secret},
        json={"profile_types": [time]},
    )
    # Test results
    assert response.status_code == 200
    assert "recommendations" in response.json
    last_fit = 100
    for i, j in zip(profiles, response.json["recommendations"]):
        assert i["id"] == j["profile"]["id"]
        assert j["fit"] <= last_fit
        last_fit = j["fit"]
