import pdb
import pytest

from lsgraph import create_app


@pytest.fixture
def lsgraph_client():
    app = create_app()
    with app.test_client() as client:
        yield client
