import pdb
import pytest


from lsgraph import create_app


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
    response = lsgraph_client.post(
        "/api/v1/organizations/",
        headers={"X-API-Key": access_id, "X-Auth-Token": access_secret},
        json={"name": "Org1",},
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
    assert "Org1" in [i["name"] for i in response.json["organizations"]]
