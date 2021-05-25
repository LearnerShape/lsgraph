import pdb
from datetime import datetime
import pytest

from lsgraph import create_app
from lsgraph.config import SECRET_KEY
from lsgraph.models import AccessKey, Customer, db
from lsgraph.utils.access_key import AccessKey as AccessKeyGen


@pytest.fixture
def lsgraph_client():
    app = create_app()
    with app.test_client() as client:
        yield client


@pytest.fixture
def lsgraph_admin_user():
    app = create_app()
    time = datetime.now().strftime("%Y%M%d%H%m%S")
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
    with app.app_context():
        db.session.delete(test_keys)
        db.session.delete(test_customer)
        db.session.commit()
