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

import pdb
import pytest

from .shared import create_skills


def test_skill_get(lsgraph_client, test_data_2org):
    (c1, org1, collection1), (c2, org2, collection2) = test_data_2org
    customer_id, access_id, access_secret = c1
    org_id = org1["id"]
    org_name = org1["name"]
    response = lsgraph_client.get(
        f"/api/v1/organizations/{org_id}/skills/",
        headers={"X-API-Key": access_id, "X-Auth-Token": access_secret},
    )
    assert response.status_code == 200
    assert "skills" in response.json.keys()
    skills = response.json["skills"]
    assert len(skills) == 16
    for i in [
        "id",
        "name",
        "description",
        "path",
        "personal",
        "creator",
        "child_skills",
        "num_descendants",
    ]:
        assert i in skills[0].keys()


def test_skill_get_query(lsgraph_client, test_data_2org):
    (c1, org1, collection1), (c2, org2, collection2) = test_data_2org
    customer_id, access_id, access_secret = c1
    org_id = org1["id"]
    org_name = org1["name"]
    # Create skills
    skills = create_skills(
        lsgraph_client, test_data_2org[0], skills=["apple", "pear", "apple banana"]
    )
    response = lsgraph_client.get(
        f"/api/v1/organizations/{org_id}/skills/?query=apple",
        headers={"X-API-Key": access_id, "X-Auth-Token": access_secret},
    )
    assert response.status_code == 200
    assert "skills" in response.json.keys()
    results = response.json["skills"]
    assert len(results) == 2
    for skill in results:
        assert "apple" in skill["name"]


def test_skill_post(lsgraph_client, test_data_2org):
    (c1, org1, collection1), (c2, org2, collection2) = test_data_2org
    customer_id, access_id, access_secret = c1
    org_id = org1["id"]
    org_name = org1["name"]
    # Get root skill id
    root_skill_id = org1["root_skill"]["id"]
    response = lsgraph_client.post(
        f"/api/v1/organizations/{org_id}/skills/",
        headers={"X-API-Key": access_id, "X-Auth-Token": access_secret},
        json={"name": "Skill 1", "description": "A new skill", "parent": root_skill_id},
    )
    assert response.status_code == 200
    assert response.json["name"] == "Skill 1"
