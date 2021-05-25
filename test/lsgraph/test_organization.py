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
    assert "Hello" in response.data.decode("utf-8")


@pytest.mark.skip("Not written")
def test_organization_create(lsgraph_client):
    assert False
