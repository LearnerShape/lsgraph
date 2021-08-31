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

from .shared import (
    create_resource,
    create_collection,
    add_members_to_collection,
    add_resources_to_collection,
    create_user,
)


def test_collections_get(lsgraph_client, test_data_2org):
    """Get collections list"""
    (c1, org1, collection1), (c2, org2, collection2) = test_data_2org
    customer_id, access_id, access_secret = c1
    org_id = org1["id"]
    response = lsgraph_client.get(
        f"/api/v1/organizations/{org_id}/collections/",
        headers={"X-API-Key": access_id, "X-Auth-Token": access_secret},
    )
    assert response.status_code == 200
    assert "collections" in response.json.keys()


def test_collections_post(lsgraph_client, test_data_2org):
    """Create collection"""
    (c1, org1, collection1), (c2, org2, collection2) = test_data_2org
    customer_id, access_id, access_secret = c1
    org_id = org1["id"]
    time = datetime.now().strftime("%Y%M%d-%H%m%S-%f")
    collection = {"name": f"collection_{time}", "public": False}
    response = lsgraph_client.post(
        f"/api/v1/organizations/{org_id}/collections/",
        headers={"X-API-Key": access_id, "X-Auth-Token": access_secret},
        json=collection,
    )
    assert response.status_code == 200
    for i in ["id", "name", "public"]:
        assert i in response.json.keys()


def test_collections_get_detail(lsgraph_client, test_data_2org):
    """Get collection detail"""
    (c1, org1, collection1), (c2, org2, collection2) = test_data_2org
    customer_id, access_id, access_secret = c1
    org_id = org1["id"]
    collection = create_collection(lsgraph_client, test_data_2org[0])
    collection_id = collection["id"]
    response = lsgraph_client.get(
        f"/api/v1/organizations/{org_id}/collections/{collection_id}/",
        headers={"X-API-Key": access_id, "X-Auth-Token": access_secret},
    )
    assert response.status_code == 200
    for i in ["id", "name", "public"]:
        assert i in response.json.keys()


def test_collections_delete(lsgraph_client, test_data_2org):
    """Delete collection"""
    (c1, org1, collection1), (c2, org2, collection2) = test_data_2org
    customer_id, access_id, access_secret = c1
    org_id = org1["id"]
    collection = create_collection(lsgraph_client, test_data_2org[0])
    collection_id = collection["id"]
    response = lsgraph_client.delete(
        f"/api/v1/organizations/{org_id}/collections/{collection_id}/",
        headers={"X-API-Key": access_id, "X-Auth-Token": access_secret},
    )
    assert response.status_code == 204


def test_collections_get_resources(lsgraph_client, test_data_2org):
    """Get collection resources list"""
    (c1, org1, collection1), (c2, org2, collection2) = test_data_2org
    customer_id, access_id, access_secret = c1
    org_id = org1["id"]
    collection = create_collection(lsgraph_client, test_data_2org[0])
    collection_id = collection["id"]
    response = lsgraph_client.get(
        f"/api/v1/organizations/{org_id}/collections/{collection_id}/resources/",
        headers={"X-API-Key": access_id, "X-Auth-Token": access_secret},
    )
    assert response.status_code == 200


def test_collections_post_resources(lsgraph_client, test_data_2org):
    """Add new resource to collection"""
    (c1, org1, collection1), (c2, org2, collection2) = test_data_2org
    customer_id, access_id, access_secret = c1
    org_id = org1["id"]
    collection = create_collection(lsgraph_client, test_data_2org[0])
    collection_id = collection["id"]
    org_resources = [
        create_resource(lsgraph_client, test_data_2org[0]) for _ in range(10)
    ]
    resources = {"resources": [{"resource_id": i["id"]} for i in org_resources]}
    response = lsgraph_client.post(
        f"/api/v1/organizations/{org_id}/collections/{collection_id}/resources/",
        headers={"X-API-Key": access_id, "X-Auth-Token": access_secret},
        json=resources,
    )
    assert response.status_code == 200


def test_collections_delete_resources(lsgraph_client, test_data_2org):
    """Delete collection resource"""
    (c1, org1, collection1), (c2, org2, collection2) = test_data_2org
    customer_id, access_id, access_secret = c1
    org_id = org1["id"]
    collection = create_collection(lsgraph_client, test_data_2org[0])
    collection_id = collection["id"]
    resources = add_resources_to_collection(
        lsgraph_client, test_data_2org[0], collection
    )
    resource_id = resources["resources"][0]["resource_id"]
    response = lsgraph_client.delete(
        f"/api/v1/organizations/{org_id}/collections/{collection_id}/resources/{resource_id}/",
        headers={"X-API-Key": access_id, "X-Auth-Token": access_secret},
    )
    assert response.status_code == 204


def test_collections_get_members(lsgraph_client, test_data_2org):
    """Get collection members list"""
    (c1, org1, collection1), (c2, org2, collection2) = test_data_2org
    customer_id, access_id, access_secret = c1
    org_id = org1["id"]
    collection = create_collection(lsgraph_client, test_data_2org[0])
    collection_id = collection["id"]
    response = lsgraph_client.get(
        f"/api/v1/organizations/{org_id}/collections/{collection_id}/members/",
        headers={"X-API-Key": access_id, "X-Auth-Token": access_secret},
    )
    assert response.status_code == 200


def test_collections_post_members(lsgraph_client, test_data_2org):
    """Add members to collection"""
    (c1, org1, collection1), (c2, org2, collection2) = test_data_2org
    customer_id, access_id, access_secret = c1
    org_id = org1["id"]
    collection = create_collection(lsgraph_client, test_data_2org[0])
    collection_id = collection["id"]
    members = {"members": [{"user_id": i["id"]} for i in collection1["users"]]}
    response = lsgraph_client.post(
        f"/api/v1/organizations/{org_id}/collections/{collection_id}/members/",
        headers={"X-API-Key": access_id, "X-Auth-Token": access_secret},
        json=members,
    )
    assert response.status_code == 200


def test_collections_delete_members(lsgraph_client, test_data_2org):
    """Delete member from collection"""
    (c1, org1, collection1), (c2, org2, collection2) = test_data_2org
    customer_id, access_id, access_secret = c1
    org_id = org1["id"]
    collection = create_collection(lsgraph_client, test_data_2org[0])
    collection_id = collection["id"]
    members = add_members_to_collection(lsgraph_client, test_data_2org[0], collection)
    member_id = members["members"][0]["user_id"]
    response = lsgraph_client.delete(
        f"/api/v1/organizations/{org_id}/collections/{collection_id}/members/{member_id}/",
        headers={"X-API-Key": access_id, "X-Auth-Token": access_secret},
    )
    assert response.status_code == 204
    get_members = lsgraph_client.get(
        f"/api/v1/organizations/{org_id}/collections/{collection_id}/members/",
        headers={"X-API-Key": access_id, "X-Auth-Token": access_secret},
    )
    remaining_members = [i["user_id"] for i in get_members.json["members"]]
    assert member_id not in remaining_members
