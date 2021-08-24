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


def create_user(lsgraph_client, org_details):
    """Create a new user"""
    (customer_id, access_id, access_secret), org, _ = org_details
    org_id = org["id"]
    time = datetime.now().strftime("%Y%M%d-%H%m%S-%f")
    user = {"name": f"user_{time}", "email": f"user_{time}@learnershape.com"}
    response = lsgraph_client.post(
        f"/api/v1/organizations/{org_id}/users/",
        headers={"X-API-Key": access_id, "X-Auth-Token": access_secret},
        json=user,
    )
    assert response.status_code == 200
    return response.json


def create_skills(lsgraph_client, org_details, root_skill=None, skills=5):
    """Create skills

    root_skill: parent skill to use
    skills: number to automatically generate or list of names or list of dicts"""
    (customer_id, access_id, access_secret), org, collection = org_details
    org_id = org["id"]
    time = datetime.now().strftime("%Y%M%d-%H%m%S-%f")
    if not root_skill:
        root_skill = org["root_skill"]["id"]
    if isinstance(skills, int):
        skills = [
            {"name": f"skill_{time}_{i}", "description": ""} for i in range(skills)
        ]
    if isinstance(skills, list):
        skills = [{"name": i, "description": ""} for i in skills]
    results = []
    for i in range(len(skills)):
        new_skill = skills[i]
        if not new_skill.get("parent", False):
            new_skill["parent"] = root_skill
        response = lsgraph_client.post(
            f"/api/v1/organizations/{org_id}/skills/",
            headers={"X-API-Key": access_id, "X-Auth-Token": access_secret},
            json=new_skill,
        )
        assert response.status_code == 200
        results.append(response.json)
    return results


def create_group(lsgraph_client, org_details, group_name=None, members=[]):
    """Create a group"""
    (customer_id, access_id, access_secret), org, collection = org_details
    org_id = org["id"]
    time = datetime.now().strftime("%Y%M%d-%H%m%S-%f")
    if not group_name:
        group_name = f"group_{time}"
    group = {
        "name": group_name,
        "members": members,
    }
    response = lsgraph_client.post(
        f"/api/v1/organizations/{org_id}/groups/",
        headers={"X-API-Key": access_id, "X-Auth-Token": access_secret},
        json=group,
    )
    assert response.status_code == 200
    return response.json


def create_collection(lsgraph_client, org_details, collection_name=None, public=False):
    """Create a collection"""
    (customer_id, access_id, access_secret), org, collection = org_details
    org_id = org["id"]
    time = datetime.now().strftime("%Y%M%d-%H%m%S-%f")
    if not collection_name:
        collection_name = f"collection_{time}"
    collection = {"name": collection_name, "public": public}
    response = lsgraph_client.post(
        f"/api/v1/organizations/{org_id}/collections/",
        headers={"X-API-Key": access_id, "X-Auth-Token": access_secret},
        json=collection,
    )
    assert response.status_code == 200
    return response.json


def add_resources_to_collection(lsgraph_client, org_details, collection, resources=5):
    """Add resources to a collection"""
    (customer_id, access_id, access_secret), org, _ = org_details
    org_id = org["id"]
    collection_id = collection["id"]
    if isinstance(resources, int):
        resources = [
            create_resource(lsgraph_client, org_details) for _ in range(resources)
        ]
        resources = {"resources": [{"resource_id": i["id"]} for i in resources]}
    response = lsgraph_client.post(
        f"/api/v1/organizations/{org_id}/collections/{collection_id}/resources/",
        headers={"X-API-Key": access_id, "X-Auth-Token": access_secret},
        json=resources,
    )
    assert response.status_code == 200
    return response.json


def add_members_to_collection(lsgraph_client, org_details, collection, members=5):
    """Add resources to a collection"""
    (customer_id, access_id, access_secret), org, _ = org_details
    org_id = org["id"]
    collection_id = collection["id"]
    if isinstance(members, int):
        users = [create_user(lsgraph_client, org_details) for _ in range(members)]
        members = {"members": [{"user_id": i["id"], "edit": False} for i in users]}
    response = lsgraph_client.post(
        f"/api/v1/organizations/{org_id}/collections/{collection_id}/members/",
        headers={"X-API-Key": access_id, "X-Auth-Token": access_secret},
        json=members,
    )
    assert response.status_code == 200
    return response.json


def create_provider(lsgraph_client, org_details, provider_name=None):
    """Create a provider"""
    (customer_id, access_id, access_secret), org, collection = org_details
    org_id = org["id"]
    time = datetime.now().strftime("%Y%M%d-%H%m%S-%f")
    if not provider_name:
        provider_name = f"provider_{time}"
    provider = {"name": provider_name, "description": f"{provider_name}: description"}
    response = lsgraph_client.post(
        f"/api/v1/organizations/{org_id}/providers/",
        headers={"X-API-Key": access_id, "X-Auth-Token": access_secret},
        json=provider,
    )
    assert response.status_code == 200
    return response.json


def create_platform(lsgraph_client, org_details, platform_name=None):
    """Create a platform"""
    (customer_id, access_id, access_secret), org, collection = org_details
    org_id = org["id"]
    time = datetime.now().strftime("%Y%M%d-%H%m%S-%f")
    if not platform_name:
        platform_name = f"platform_{time}"
    platform = {"name": platform_name, "description": f"{platform_name}: description"}
    response = lsgraph_client.post(
        f"/api/v1/organizations/{org_id}/platforms/",
        headers={"X-API-Key": access_id, "X-Auth-Token": access_secret},
        json=platform,
    )
    assert response.status_code == 200
    return response.json


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
