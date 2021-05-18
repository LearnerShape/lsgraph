import pdb
import pytest

from lsgraph import create_app


@pytest.mark.skip("Not written")
def test_organization_get(lsgraph_client):
    response = lsgraph_client.get("/api/v1/organizations")
    assert "Hello" in response.data.decode("utf-8")


@pytest.mark.skip("Not written")
def test_organization_create(lsgraph_client):
    assert False
