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


@pytest.mark.skip(reason="Not Implemented")
def test_collections_get(lsgraph_client, test_data_2org):
    """Get collections list"""
    (c1, org1, collection1), (c2, org2, collection2) = test_data_2org
    customer_id, access_id, access_secret = c1
    org_id = org1["id"]


@pytest.mark.skip(reason="Not Implemented")
def test_collections_post(lsgraph_client, test_data_2org):
    """Get collections list"""
    (c1, org1, collection1), (c2, org2, collection2) = test_data_2org
    customer_id, access_id, access_secret = c1
    org_id = org1["id"]


def create_collection(
    lsgraph_client, org_details, collection_name=None, resources=[], members=[]
):
    """Create a collection"""
    (customer_id, access_id, access_secret), org, collection = org_details
    org_id = org["id"]
    time = datetime.now().strftime("%Y%M%d-%H%m%S-%f")
    if not collection_name:
        collection_name = f"collection_{time}"


@pytest.mark.skip(reason="Not Implemented")
def test_collections_delete(lsgraph_client, test_data_2org):
    """Get collections list"""
    (c1, org1, collection1), (c2, org2, collection2) = test_data_2org
    customer_id, access_id, access_secret = c1
    org_id = org1["id"]


@pytest.mark.skip(reason="Not Implemented")
def test_collections_get_resources(lsgraph_client, test_data_2org):
    """Get collections list"""
    (c1, org1, collection1), (c2, org2, collection2) = test_data_2org
    customer_id, access_id, access_secret = c1
    org_id = org1["id"]


@pytest.mark.skip(reason="Not Implemented")
def test_collections_post_resources(lsgraph_client, test_data_2org):
    """Get collections list"""
    (c1, org1, collection1), (c2, org2, collection2) = test_data_2org
    customer_id, access_id, access_secret = c1
    org_id = org1["id"]


@pytest.mark.skip(reason="Not Implemented")
def test_collections_delete_resources(lsgraph_client, test_data_2org):
    """Get collections list"""
    (c1, org1, collection1), (c2, org2, collection2) = test_data_2org
    customer_id, access_id, access_secret = c1
    org_id = org1["id"]


@pytest.mark.skip(reason="Not Implemented")
def test_collections_get_members(lsgraph_client, test_data_2org):
    """Get collections list"""
    (c1, org1, collection1), (c2, org2, collection2) = test_data_2org
    customer_id, access_id, access_secret = c1
    org_id = org1["id"]


@pytest.mark.skip(reason="Not Implemented")
def test_collections_post_members(lsgraph_client, test_data_2org):
    """Get collections list"""
    (c1, org1, collection1), (c2, org2, collection2) = test_data_2org
    customer_id, access_id, access_secret = c1
    org_id = org1["id"]


@pytest.mark.skip(reason="Not Implemented")
def test_collections_delete_members(lsgraph_client, test_data_2org):
    """Get collections list"""
    (c1, org1, collection1), (c2, org2, collection2) = test_data_2org
    customer_id, access_id, access_secret = c1
    org_id = org1["id"]
