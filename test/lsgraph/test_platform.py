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

from .shared import create_platform


def test_platforms_get(lsgraph_client, test_data_2org):
    """Get platform list"""
    (c1, org1, collection1), (c2, org2, collection2) = test_data_2org
    customer_id, access_id, access_secret = c1
    org_id = org1["id"]
    response = lsgraph_client.get(
        f"/api/v1/organizations/{org_id}/platforms/",
        headers={"X-API-Key": access_id, "X-Auth-Token": access_secret},
    )
    assert response.status_code == 200
    assert "platforms" in response.json.keys()


def test_platforms_post(lsgraph_client, test_data_2org):
    """Create a new platform"""
    (c1, org1, collection1), (c2, org2, collection2) = test_data_2org
    result = create_platform(lsgraph_client, test_data_2org[0])
    for i in ["id", "name", "description", "logo", "url"]:
        assert i in result.keys()


def test_platforms_get_detail(lsgraph_client, test_data_2org):
    """Get platform detail"""
    (c1, org1, collection1), (c2, org2, collection2) = test_data_2org
    customer_id, access_id, access_secret = c1
    org_id = org1["id"]
    result = create_platform(lsgraph_client, test_data_2org[0])
    platform_id = result["id"]
    response = lsgraph_client.get(
        f"/api/v1/organizations/{org_id}/platforms/{platform_id}/",
        headers={"X-API-Key": access_id, "X-Auth-Token": access_secret},
    )
    assert response.status_code == 200
    for i in ["id", "name", "description", "logo", "url"]:
        assert i in response.json.keys()


def test_platforms_delete(lsgraph_client, test_data_2org):
    """Delete platform"""
    (c1, org1, collection1), (c2, org2, collection2) = test_data_2org
    customer_id, access_id, access_secret = c1
    org_id = org1["id"]
    result = create_platform(lsgraph_client, test_data_2org[0])
    platform_id = result["id"]
    response = lsgraph_client.delete(
        f"/api/v1/organizations/{org_id}/platforms/{platform_id}/",
        headers={"X-API-Key": access_id, "X-Auth-Token": access_secret},
    )
    assert response.status_code == 204
