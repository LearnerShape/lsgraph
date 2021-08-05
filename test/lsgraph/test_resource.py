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


from datetime import datetime, timedelta, timezone
import pdb
import pytest

from .test_provider import create_provider
from .test_platform import create_platform
from .test_format import create_format


def test_resources_get(lsgraph_client, test_data_2org):
    """Get resource list"""
    (c1, org1, collection1), (c2, org2, collection2) = test_data_2org
    customer_id, access_id, access_secret = c1
    org_id = org1["id"]
    response = lsgraph_client.get(
        f"/api/v1/organizations/{org_id}/resources/",
        headers={"X-API-Key": access_id, "X-Auth-Token": access_secret},
    )
    assert response.status_code == 200
    assert "resources" in response.json.keys()


def create_resource(lsgraph_client, org_details, resource_name=None):
    """Create a resource"""
    (customer_id, access_id, access_secret), org, collection = org_details
    org_id = org["id"]
    provider = create_provider(lsgraph_client, org_details)
    platform = create_platform(lsgraph_client, org_details)
    time = datetime.now().strftime("%Y%M%d-%H%m%S-%f")
    if not resource_name:
        resource_name = f"resource_{time}"
    resource = {
        "name": resource_name,
        "short_description": f"{resource_name}: description",
        "description": "test",
        "url": "http://test.com",
        "provider": provider["id"],
        "platform": platform["id"],
        "platform_level": "",
        "alt_id": "",
        "syllabus": "",
        "learning_outcomes": "",
        "prerequisite_knowledge": "",
        "retired": False,
    }
    response = lsgraph_client.post(
        f"/api/v1/organizations/{org_id}/resources/",
        headers={"X-API-Key": access_id, "X-Auth-Token": access_secret},
        json=resource,
    )
    assert response.status_code == 200
    return response.json


def test_resources_post(lsgraph_client, test_data_2org):
    """Create a new resource"""
    (c1, org1, collection1), (c2, org2, collection2) = test_data_2org
    result = create_resource(lsgraph_client, test_data_2org[0])
    for i in [
        "id",
        "name",
        "short_description",
        "description",
        "url",
        "provider",
        "platform",
        "platform_level",
        "alt_id",
        "syllabus",
        "learning_outcomes",
        "prerequisite_knowledge",
        "retired",
        "offerings",
    ]:
        assert i in result.keys()


def test_resources_get_detail(lsgraph_client, test_data_2org):
    """Get resource detail"""
    (c1, org1, collection1), (c2, org2, collection2) = test_data_2org
    customer_id, access_id, access_secret = c1
    org_id = org1["id"]
    result = create_resource(lsgraph_client, test_data_2org[0])
    resource_id = result["id"]
    response = lsgraph_client.get(
        f"/api/v1/organizations/{org_id}/resources/{resource_id}/",
        headers={"X-API-Key": access_id, "X-Auth-Token": access_secret},
    )
    assert response.status_code == 200
    for i in [
        "id",
        "name",
        "short_description",
        "description",
        "url",
        "provider",
        "platform",
        "platform_level",
        "alt_id",
        "syllabus",
        "learning_outcomes",
        "prerequisite_knowledge",
        "retired",
        "offerings",
    ]:
        assert i in response.json.keys()


def test_resources_delete(lsgraph_client, test_data_2org):
    """Delete resource"""
    (c1, org1, collection1), (c2, org2, collection2) = test_data_2org
    customer_id, access_id, access_secret = c1
    org_id = org1["id"]
    result = create_resource(lsgraph_client, test_data_2org[0])
    resource_id = result["id"]
    response = lsgraph_client.delete(
        f"/api/v1/organizations/{org_id}/resources/{resource_id}/",
        headers={"X-API-Key": access_id, "X-Auth-Token": access_secret},
    )
    assert response.status_code == 204


def create_offering(lsgraph_client, org_details, resource, offering_name=None):
    """Create a resource"""
    (customer_id, access_id, access_secret), org, collection = org_details
    org_id = org["id"]
    resource_id = resource["id"]
    format = create_format(lsgraph_client, org_details)
    time = datetime.now().strftime("%Y%M%d-%H%m%S-%f")
    if not offering_name:
        offering_name = f"offering_{time}"
    offering = {
        "name": offering_name,
        "format": format["id"],
        "start_date": (datetime.now(timezone.utc) + timedelta(days=1 * 7)).isoformat(),
        "end_date": (datetime.now(timezone.utc) + timedelta(days=6 * 7)).isoformat(),
        "pace_min_hrs_per_week": 1,
        "pace_max_hrs_per_week": 2,
        "pace_num_weeks": 5,
        "elapsed_duration": 3024000,
        "min_taught_duration": 5,
        "max_taught_duration": 10,
        "language": "en",
        "cc_language": "en",
        "free": False,
        "free_audit": True,
        "paid": True,
        "certificate": True,
        "quality": 4.7,
        "instructors": "Dr. Smith",
        "retired": False,
    }
    response = lsgraph_client.post(
        f"/api/v1/organizations/{org_id}/resources/{resource_id}/offerings/",
        headers={"X-API-Key": access_id, "X-Auth-Token": access_secret},
        json=offering,
    )
    assert response.status_code == 200
    return response.json


def test_resources_post_offering(lsgraph_client, test_data_2org):
    """Create a new offering"""
    (c1, org1, collection1), (c2, org2, collection2) = test_data_2org
    resource_result = create_resource(lsgraph_client, test_data_2org[0])
    offering_result = create_offering(
        lsgraph_client, test_data_2org[0], resource_result
    )
    for i in [
        "id",
        "name",
        "format",
        "start_date",
        "end_date",
        "pace_min_hrs_per_week",
        "pace_max_hrs_per_week",
        "pace_num_weeks",
        "elapsed_duration",
        "min_taught_duration",
        "max_taught_duration",
        "language",
        "cc_language",
        "free",
        "free_audit",
        "paid",
        "certificate",
        "quality",
        "instructors",
        "retired",
    ]:
        assert i in offering_result.keys()


def test_resources_delete_offering(lsgraph_client, test_data_2org):
    """Delete offering"""
    (c1, org1, collection1), (c2, org2, collection2) = test_data_2org
    customer_id, access_id, access_secret = c1
    org_id = org1["id"]
    resource_result = create_resource(lsgraph_client, test_data_2org[0])
    offering_result = create_offering(
        lsgraph_client, test_data_2org[0], resource_result
    )
    resource_id = resource_result["id"]
    offering_id = offering_result["id"]
    response = lsgraph_client.delete(
        f"/api/v1/organizations/{org_id}/resources/{resource_id}/offerings/{offering_id}/",
        headers={"X-API-Key": access_id, "X-Auth-Token": access_secret},
    )
    assert response.status_code == 204
