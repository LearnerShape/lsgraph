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

from .shared import create_group


def test_groups_get(lsgraph_client, test_data_2org):
    """Get group list"""
    (c1, org1, collection1), (c2, org2, collection2) = test_data_2org
    customer_id, access_id, access_secret = c1
    org_id = org1["id"]
    response = lsgraph_client.get(
        f"/api/v1/organizations/{org_id}/groups/",
        headers={"X-API-Key": access_id, "X-Auth-Token": access_secret},
    )
    assert response.status_code == 200
    assert "groups" in response.json.keys()


def test_groups_post_whole_org(lsgraph_client, test_data_2org):
    """Create a whole organization to a group"""
    (c1, org1, collection1), (c2, org2, collection2) = test_data_2org
    customer_id, access_id, access_secret = c1
    org_id = org1["id"]
    time = datetime.now().strftime("%Y%M%d-%H%m%S-%f")
    group = {"name": f"group_{time}", "whole_organization": True}
    response = lsgraph_client.post(
        f"/api/v1/organizations/{org_id}/groups/",
        headers={"X-API-Key": access_id, "X-Auth-Token": access_secret},
        json=group,
    )
    assert response.status_code == 200
    for i in ["id", "name", "whole_organization", "members"]:
        assert i in response.json.keys()
    assert len(response.json["members"]) == 2
    for i in ["id", "name"]:
        for j in response.json["members"]:
            assert i in j


def test_groups_post_subset(lsgraph_client, test_data_2org):
    """Add a specific list of users to a group"""
    (c1, org1, collection1), (c2, org2, collection2) = test_data_2org
    customer_id, access_id, access_secret = c1
    org_id = org1["id"]
    time = datetime.now().strftime("%Y%M%d-%H%m%S-%f")
    group = {
        "name": f"group_{time}",
        "members": [
            {"id": collection1["users"][0]["id"]},
        ],
    }
    response = lsgraph_client.post(
        f"/api/v1/organizations/{org_id}/groups/",
        headers={"X-API-Key": access_id, "X-Auth-Token": access_secret},
        json=group,
    )
    assert response.status_code == 200
    for i in ["id", "name", "whole_organization", "members"]:
        assert i in response.json.keys()
    assert len(response.json["members"]) == 1
    for i in ["id", "name"]:
        for j in response.json["members"]:
            assert i in j


def test_groups_outside_org_members(lsgraph_client, test_data_2org):
    """Get error if adding a user from outside the organization"""
    (c1, org1, collection1), (c2, org2, collection2) = test_data_2org
    customer_id, access_id, access_secret = c1
    org_id = org1["id"]
    time = datetime.now().strftime("%Y%M%d-%H%m%S-%f")
    group = {
        "name": f"group_{time}",
        "members": [
            {"id": collection2["users"][0]["id"]},  # user from other org
        ],
    }
    response = lsgraph_client.post(
        f"/api/v1/organizations/{org_id}/groups/",
        headers={"X-API-Key": access_id, "X-Auth-Token": access_secret},
        json=group,
    )
    assert response.status_code == 403


def test_groups_get_members(lsgraph_client, test_data_2org):
    """Get members for an existing group"""
    (c1, org1, collection1), (c2, org2, collection2) = test_data_2org
    customer_id, access_id, access_secret = c1
    org_id = org1["id"]
    # Create group
    new_group = create_group(
        lsgraph_client,
        test_data_2org[0],
        members=[
            {
                "id": i["id"],
            }
            for i in collection1["users"]
        ],
    )
    group_id = new_group["id"]
    # Add member
    response = lsgraph_client.get(
        f"/api/v1/organizations/{org_id}/groups/{group_id}/members/",
        headers={"X-API-Key": access_id, "X-Auth-Token": access_secret},
    )
    assert response.status_code == 200
    assert len(response.json["members"]) == len(collection1["users"])
    for i in ["id", "name"]:
        for j in response.json["members"]:
            assert i in j


def test_groups_add_members(lsgraph_client, test_data_2org):
    """Add users to an existing group"""
    (c1, org1, collection1), (c2, org2, collection2) = test_data_2org
    customer_id, access_id, access_secret = c1
    org_id = org1["id"]
    time = datetime.now().strftime("%Y%M%d-%H%m%S-%f")
    # Create group
    new_group = create_group(lsgraph_client, test_data_2org[0])
    group_id = new_group["id"]
    # Add member
    members = {"members": [{"id": i["id"]} for i in collection1["users"]]}
    response = lsgraph_client.post(
        f"/api/v1/organizations/{org_id}/groups/{group_id}/members/",
        headers={"X-API-Key": access_id, "X-Auth-Token": access_secret},
        json=members,
    )
    assert response.status_code == 200
    assert len(response.json["members"]) == len(collection1["users"])
    for i in ["id", "name"]:
        for j in response.json["members"]:
            assert i in j


def test_group_delete_members(lsgraph_client, test_data_2org):
    """Delete users from a group"""
    (c1, org1, collection1), (c2, org2, collection2) = test_data_2org
    customer_id, access_id, access_secret = c1
    org_id = org1["id"]
    new_group = create_group(
        lsgraph_client,
        test_data_2org[0],
        members=[
            {
                "id": i["id"],
            }
            for i in collection1["users"]
        ],
    )
    group_id = new_group["id"]
    # Delete member
    user_id = collection1["users"][0]["id"]
    response = lsgraph_client.delete(
        f"/api/v1/organizations/{org_id}/groups/{group_id}/members/{user_id}/",
        headers={"X-API-Key": access_id, "X-Auth-Token": access_secret},
    )
    assert response.status_code == 204
    # Check that user is not in the group
    response = lsgraph_client.get(
        f"/api/v1/organizations/{org_id}/groups/{group_id}/members/",
        headers={"X-API-Key": access_id, "X-Auth-Token": access_secret},
    )
    assert response.status_code == 200
    member_ids = [i["id"] for i in response.json["members"]]
    assert user_id not in member_ids


def test_group_delete(lsgraph_client, test_data_2org):
    """Delete entire group"""
    (c1, org1, collection1), (c2, org2, collection2) = test_data_2org
    customer_id, access_id, access_secret = c1
    org_id = org1["id"]
    new_group = create_group(
        lsgraph_client,
        test_data_2org[0],
        members=[
            {
                "id": i["id"],
            }
            for i in collection1["users"]
        ],
    )
    group_id = new_group["id"]
    # Delete member
    user_id = collection1["users"][0]["id"]
    response = lsgraph_client.delete(
        f"/api/v1/organizations/{org_id}/groups/{group_id}/",
        headers={"X-API-Key": access_id, "X-Auth-Token": access_secret},
    )
    assert response.status_code == 204
    # Check that user is not in the group
    response = lsgraph_client.get(
        f"/api/v1/organizations/{org_id}/groups/",
        headers={"X-API-Key": access_id, "X-Auth-Token": access_secret},
    )
    assert response.status_code == 200
    group_ids = [i["id"] for i in response.json["groups"]]
    assert group_id not in group_ids
