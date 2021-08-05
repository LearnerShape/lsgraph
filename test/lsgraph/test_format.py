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


def test_formats_get(lsgraph_client, test_data_2org):
    """Get format list"""
    (c1, org1, collection1), (c2, org2, collection2) = test_data_2org
    customer_id, access_id, access_secret = c1
    org_id = org1["id"]
    response = lsgraph_client.get(
        f"/api/v1/organizations/{org_id}/formats/",
        headers={"X-API-Key": access_id, "X-Auth-Token": access_secret},
    )
    assert response.status_code == 200
    assert "formats" in response.json.keys()


def create_format(lsgraph_client, org_details, format_name=None):
    """Create a format"""
    (customer_id, access_id, access_secret), org, collection = org_details
    org_id = org["id"]
    time = datetime.now().strftime("%Y%M%d-%H%m%S-%f")
    if not format_name:
        format_name = f"format_{time}"
    format = {"name": format_name, "description": f"{format_name}: description"}
    response = lsgraph_client.post(
        f"/api/v1/organizations/{org_id}/formats/",
        headers={"X-API-Key": access_id, "X-Auth-Token": access_secret},
        json=format,
    )
    assert response.status_code == 200
    return response.json


def test_formats_post(lsgraph_client, test_data_2org):
    """Create a new format"""
    (c1, org1, collection1), (c2, org2, collection2) = test_data_2org
    result = create_format(lsgraph_client, test_data_2org[0])
    for i in [
        "id",
        "name",
        "description",
        "logo",
    ]:
        assert i in result.keys()


def test_formats_get_detail(lsgraph_client, test_data_2org):
    """Get format detail"""
    (c1, org1, collection1), (c2, org2, collection2) = test_data_2org
    customer_id, access_id, access_secret = c1
    org_id = org1["id"]
    result = create_format(lsgraph_client, test_data_2org[0])
    format_id = result["id"]
    response = lsgraph_client.get(
        f"/api/v1/organizations/{org_id}/formats/{format_id}/",
        headers={"X-API-Key": access_id, "X-Auth-Token": access_secret},
    )
    assert response.status_code == 200
    for i in [
        "id",
        "name",
        "description",
        "logo",
    ]:
        assert i in response.json.keys()


def test_formats_delete(lsgraph_client, test_data_2org):
    """Delete format"""
    (c1, org1, collection1), (c2, org2, collection2) = test_data_2org
    customer_id, access_id, access_secret = c1
    org_id = org1["id"]
    result = create_format(lsgraph_client, test_data_2org[0])
    format_id = result["id"]
    response = lsgraph_client.delete(
        f"/api/v1/organizations/{org_id}/formats/{format_id}/",
        headers={"X-API-Key": access_id, "X-Auth-Token": access_secret},
    )
    assert response.status_code == 204
