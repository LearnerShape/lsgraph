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


def test_access_no_headers(lsgraph_client):
    response = lsgraph_client.get("/api/v1/organizations/")
    assert response.status_code == 403


def test_access_bad_headers(lsgraph_client):
    response = lsgraph_client.get(
        "/api/v1/organizations/",
        headers={"X-API-Key": "dummy", "X-Auth-Token": "dummy"},
    )
    assert response.status_code == 403


def test_organization_get(lsgraph_client, lsgraph_admin_user):
    customer_id, access_id, access_secret = lsgraph_admin_user
    response = lsgraph_client.get(
        "/api/v1/organizations/",
        headers={"X-API-Key": access_id, "X-Auth-Token": access_secret},
    )
    assert response.status_code == 200
    assert "organizations" in response.json.keys()


def test_organization_create(lsgraph_client, lsgraph_admin_user):
    customer_id, access_id, access_secret = lsgraph_admin_user
    org_name = datetime.now().strftime("%Y%M%d-%H%m%S-%f")
    response = lsgraph_client.post(
        "/api/v1/organizations/",
        headers={"X-API-Key": access_id, "X-Auth-Token": access_secret},
        json={
            "name": org_name,
        },
    )
    assert response.status_code == 200
    assert "id" in response.json
    assert "name" in response.json
    response = lsgraph_client.get(
        "/api/v1/organizations/",
        headers={"X-API-Key": access_id, "X-Auth-Token": access_secret},
    )
    assert response.status_code == 200
    assert "organizations" in response.json.keys()
    assert org_name in [i["name"] for i in response.json["organizations"]]


def test_organization_get_detail(
    lsgraph_client, lsgraph_admin_user, lsgraph_organization
):
    customer_id, access_id, access_secret = lsgraph_admin_user
    org_id = lsgraph_organization["id"]
    org_name = lsgraph_organization["name"]
    response = lsgraph_client.get(
        f"/api/v1/organizations/{org_id}/",
        headers={"X-API-Key": access_id, "X-Auth-Token": access_secret},
    )
    assert response.status_code == 200
    assert "name" in response.json.keys()
    assert "root_skill" in response.json.keys()
    assert "level_map" in response.json.keys()
