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


import pdb
from datetime import datetime
import pytest

from lsgraph import create_app
from lsgraph.config import SECRET_KEY
from lsgraph.models import AccessKey, Customer, db
from lsgraph.utils.access_key import AccessKey as AccessKeyGen


@pytest.fixture(scope="module")
def lsgraph_client():
    app = create_app()
    with app.test_client() as client:
        yield client


def create_customer(name, email):
    """Create a new customer"""
    app = create_app()
    with app.app_context():
        test_customer = Customer(email=email, name=name)
        db.session.add(test_customer)
        db.session.commit()
        customer_id = test_customer.id
        akg = AccessKeyGen(SECRET_KEY)
        access_id, access_secret = akg.generate_pair()
        test_keys = AccessKey(
            access_key=access_id,
            secret_key=access_secret,
            customer_id=customer_id,
            created_at=datetime.now(),
        )
        db.session.add(test_keys)
        db.session.commit()
    return customer_id, access_id, access_secret


def create_organization(name, customer_details, client):
    """Create a new organization"""
    _, access_id, access_secret = customer_details
    response = client.post(
        "/api/v1/organizations/",
        headers={"X-API-Key": access_id, "X-Auth-Token": access_secret},
        json={
            "name": name,
        },
    )
    assert response.status_code == 200
    return response.json


def create_skill_graph(skills_graph, org, customer_details, client):
    """Load a skills graph"""
    _, access_id, access_secret = customer_details
    org_id = org["id"]
    id_lookup = {None: org["root_skill"]["id"]}
    results = []
    for i, (parent, name) in enumerate(skills_graph):
        response = client.post(
            f"/api/v1/organizations/{org_id}/skills/",
            headers={"X-API-Key": access_id, "X-Auth-Token": access_secret},
            json={
                "name": "Skill 1",
                "description": "A new skill",
                "parent": id_lookup[parent],
            },
        )
        assert response.status_code == 200
        id_lookup[i] = response.json["id"]
        results.append(response.json)
    return results


def create_user(label, org, customer_details, client):
    """Create a user"""
    _, access_id, access_secret = customer_details
    org_id = org["id"]
    user = {"name": label, "email": f"{label}@learnershape.com"}
    response = client.post(
        f"/api/v1/organizations/{org_id}/users/",
        headers={"X-API-Key": access_id, "X-Auth-Token": access_secret},
        json=user,
    )
    assert response.status_code == 200
    return response.json


@pytest.fixture(scope="module")
def test_data_2org(lsgraph_client):
    """Create two customers/organizations for testing"""
    time = datetime.now().strftime("%Y%M%d-%H%m%S-%f")
    customer1 = create_customer(f"{time}_1", f"{time}_1@learnershape.com")
    customer2 = create_customer(f"{time}_2", f"{time}_2@learnershape.com")
    org1 = create_organization(f"{time}_1org", customer1, lsgraph_client)
    org2 = create_organization(f"{time}_2org", customer2, lsgraph_client)
    skills_graph1 = []
    skills_graph1.extend([[None, f"l1-{i}"] for i in range(5)])
    skills_graph1.extend([[len(skills_graph1) - 1, f"l2-{i}"] for i in range(5)])
    skills_graph1.extend([[len(skills_graph1) - 1, f"l3-{i}"] for i in range(5)])
    skills_graph2 = []
    skills_graph2.extend([[None, f"l1-{i}"] for i in range(3)])
    skills_graph2.extend([[len(skills_graph2) - 1, f"l2-{i}"] for i in range(9)])
    skills_graph2.extend([[len(skills_graph2) - 1, f"l3-{i}"] for i in range(7)])
    collection1 = {}
    collection2 = {}
    collection1["skills"] = create_skill_graph(
        skills_graph1, org1, customer1, lsgraph_client
    )
    collection2["skills"] = create_skill_graph(
        skills_graph2, org2, customer2, lsgraph_client
    )
    collection1["users"] = [
        create_user(f"{time}_1org_1u", org1, customer1, lsgraph_client),
        create_user(f"{time}_1org_2u", org1, customer1, lsgraph_client),
    ]
    collection2["users"] = [
        create_user(f"{time}_2org_1u", org2, customer2, lsgraph_client),
        create_user(f"{time}_2org_2u", org2, customer2, lsgraph_client),
    ]
    return ((customer1, org1, collection1), (customer2, org2, collection2))


@pytest.fixture(scope="module")
def lsgraph_admin_user():
    app = create_app()
    time = datetime.now().strftime("%Y%M%d-%H%m%S-%f")
    with app.app_context():
        test_customer = Customer(email=f"{time}@learnershape.com", name="Test")
        db.session.add(test_customer)
        db.session.commit()
        customer_id = test_customer.id
        akg = AccessKeyGen(SECRET_KEY)
        access_id, access_secret = akg.generate_pair()
        test_keys = AccessKey(
            access_key=access_id,
            secret_key=access_secret,
            customer_id=customer_id,
            created_at=datetime.now(),
        )
        db.session.add(test_keys)
        db.session.commit()
    yield customer_id, access_id, access_secret


@pytest.fixture(scope="module")
def lsgraph_organization(lsgraph_client, lsgraph_admin_user):
    time = datetime.now().strftime("%Y%M%d-%H%m%S-%f")
    customer_id, access_id, access_secret = lsgraph_admin_user
    response = lsgraph_client.post(
        "/api/v1/organizations/",
        headers={"X-API-Key": access_id, "X-Auth-Token": access_secret},
        json={
            "name": time,
        },
    )
    assert response.status_code == 200
    return response.json
