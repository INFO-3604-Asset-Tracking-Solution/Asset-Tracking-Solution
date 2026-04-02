import pytest
import logging
from App.main import create_app
from App.database import db, create_db 

LOGGER = logging.getLogger(__name__)

# This fixture creates an empty database for the test and deletes it after the tests are done. It is automatically used by all tests in this module (autouse=True) and is shared across all tests in the module (scope="module").
@pytest.fixture(autouse=True, scope="module")
def empty_db():
    app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///test.db'})
    with app.app_context():
        create_db()
        yield app.test_client()
        db.drop_all()