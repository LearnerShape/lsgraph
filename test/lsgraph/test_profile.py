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


def test_profile_get(lsgraph_client, test_data_2org):
    (c1, org1, collection1), (c2, org2, collection2) = test_data_2org
    customer_id, access_id, access_secret = c1
    org_id = org1["id"]
    response = lsgraph_client.get(
        f"/api/v1/organizations/{org_id}/profiles/",
        headers={"X-API-Key": access_id, "X-Auth-Token": access_secret},
    )
    assert response.status_code == 200
    assert "profiles" in response.json.keys()


def test_profile_post(lsgraph_client, test_data_2org):
    (c1, org1, collection1), (c2, org2, collection2) = test_data_2org
    customer_id, access_id, access_secret = c1
    org_id = org1["id"]
    # Build a sample profile
    profile = {
        "name": "p1",
        "description": "p1 desc",
        "type": "job role",
        "skills": [
            {"skill": s["id"], "level_name": "Beginner"}
            for s in collection1["skills"][-2:]
        ],
    }
    # Post to API
    response = lsgraph_client.post(
        f"/api/v1/organizations/{org_id}/profiles/",
        headers={"X-API-Key": access_id, "X-Auth-Token": access_secret},
        json=profile,
    )
    assert response.status_code == 200
    for i in ["name", "description", "type", "skills"]:
        assert i in response.json.keys()


def test_profile_post_outside_org_skill(lsgraph_client, test_data_2org):
    (c1, org1, collection1), (c2, org2, collection2) = test_data_2org
    customer_id, access_id, access_secret = c1
    org_id = org1["id"]
    # Build a sample profile
    profile = {
        "name": "p1",
        "description": "p1 desc",
        "type": "job role",
        "skills": [
            {"skill": s["id"], "level_name": "Beginner"}
            for s in collection2["skills"][-2:]  # Skills from other organization
        ],
    }
    # Post to API
    response = lsgraph_client.post(
        f"/api/v1/organizations/{org_id}/profiles/",
        headers={"X-API-Key": access_id, "X-Auth-Token": access_secret},
        json=profile,
    )
    assert response.status_code == 403


def create_profile(
    lsgraph_client, org_details, profile_name=None, skills=[], profile_type="job role"
):
    """Create a profile"""
    (customer_id, access_id, access_secret), org, collection = org_details
    org_id = org["id"]
    time = datetime.now().strftime("%Y%M%d-%H%m%S-%f")
    if not profile_name:
        profile_name = f"profile_{time}"
    profile = {
        "name": profile_name,
        "description": f"Description for {profile_name}",
        "type": "job role",
        "skills": skills,
    }
    response = lsgraph_client.post(
        f"/api/v1/organizations/{org_id}/profiles/",
        headers={"X-API-Key": access_id, "X-Auth-Token": access_secret},
        json=profile,
    )
    assert response.status_code == 200
    return response.json


def test_profile_update_skills(lsgraph_client, test_data_2org):
    (c1, org1, collection1), (c2, org2, collection2) = test_data_2org
    customer_id, access_id, access_secret = c1
    org_id = org1["id"]
    new_profile = create_profile(
        lsgraph_client,
        test_data_2org[0],
        skills=[
            {"skill": i["id"], "level_name": "Beginner"}
            for i in collection1["skills"][-2:]
        ],
    )
    profile_id = new_profile["id"]
    skill_id = collection1["skills"][-3]["id"]
    skills_update = {"skills": [{"skill": skill_id, "level_name": "Beginner"}]}
    response = lsgraph_client.post(
        f"/api/v1/organizations/{org_id}/profiles/{profile_id}/skills/",
        headers={"X-API-Key": access_id, "X-Auth-Token": access_secret},
        json=skills_update,
    )
    assert response.status_code == 200
    response = lsgraph_client.get(
        f"/api/v1/organizations/{org_id}/profiles/",
        headers={"X-API-Key": access_id, "X-Auth-Token": access_secret},
    )
    saved_profile = [i for i in response.json["profiles"] if i["id"] == profile_id][0]
    skill_ids = [i["skill"] for i in saved_profile["skills"]]
    assert skill_id in skill_ids


def test_profile_update_levels(lsgraph_client, test_data_2org):
    (c1, org1, collection1), (c2, org2, collection2) = test_data_2org
    customer_id, access_id, access_secret = c1
    org_id = org1["id"]
    new_profile = create_profile(
        lsgraph_client,
        test_data_2org[0],
        skills=[
            {"skill": i["id"], "level_name": "Beginner"}
            for i in collection1["skills"][-2:]
        ],
    )
    profile_id = new_profile["id"]
    skill_id = collection1["skills"][-1]["id"]
    skills_update = {"skills": [{"skill": skill_id, "level_name": "Intermediate"}]}
    response = lsgraph_client.post(
        f"/api/v1/organizations/{org_id}/profiles/{profile_id}/skills/",
        headers={"X-API-Key": access_id, "X-Auth-Token": access_secret},
        json=skills_update,
    )
    assert response.status_code == 200
    response = lsgraph_client.get(
        f"/api/v1/organizations/{org_id}/profiles/",
        headers={"X-API-Key": access_id, "X-Auth-Token": access_secret},
    )
    saved_profile = [i for i in response.json["profiles"] if i["id"] == profile_id][0]
    levels = {i["skill"]: i["level_name"] for i in saved_profile["skills"]}
    assert levels[skill_id] == "Intermediate"


def test_profile_delete_skills(lsgraph_client, test_data_2org):
    (c1, org1, collection1), (c2, org2, collection2) = test_data_2org
    customer_id, access_id, access_secret = c1
    org_id = org1["id"]
    new_profile = create_profile(
        lsgraph_client,
        test_data_2org[0],
        skills=[
            {"skill": i["id"], "level_name": "Beginner"}
            for i in collection1["skills"][-2:]
        ],
    )
    profile_id = new_profile["id"]
    skill_id = collection1["skills"][-1]["id"]
    response = lsgraph_client.delete(
        f"/api/v1/organizations/{org_id}/profiles/{profile_id}/skills/{skill_id}/",
        headers={"X-API-Key": access_id, "X-Auth-Token": access_secret},
    )
    assert response.status_code == 204
    response = lsgraph_client.get(
        f"/api/v1/organizations/{org_id}/profiles/",
        headers={"X-API-Key": access_id, "X-Auth-Token": access_secret},
    )
    saved_profile = [i for i in response.json["profiles"] if i["id"] == profile_id][0]
    skill_ids = [i["skill"] for i in saved_profile["skills"]]
    assert skill_id not in skill_ids


def test_profile_delete(lsgraph_client, test_data_2org):
    (c1, org1, collection1), (c2, org2, collection2) = test_data_2org
    customer_id, access_id, access_secret = c1
    org_id = org1["id"]
    new_profile = create_profile(
        lsgraph_client,
        test_data_2org[0],
        skills=[
            {"skill": i["id"], "level_name": "Beginner"}
            for i in collection1["skills"][-2:]
        ],
    )
    profile_id = new_profile["id"]
    response = lsgraph_client.delete(
        f"/api/v1/organizations/{org_id}/profiles/{profile_id}/",
        headers={"X-API-Key": access_id, "X-Auth-Token": access_secret},
    )
    assert response.status_code == 204
    response = lsgraph_client.get(
        f"/api/v1/organizations/{org_id}/profiles/",
        headers={"X-API-Key": access_id, "X-Auth-Token": access_secret},
    )
    assert profile_id not in response.json["profiles"]
