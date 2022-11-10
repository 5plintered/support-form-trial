import os
import tempfile
import sys
sys.path.append('.')
from support import *
from config import *

import pytest


import flask

@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
    })
    # Create a test client using the Flask application configured for testing
    with app.test_client() as testing_client:
        # Establish an application context
        with app.app_context():
            yield testing_client  # this is where the testing happens!
   
@pytest.fixture()
def client(app):
    return app.test_client()

def test_should_load_main_page(app):
    """Start with a blank database."""
    print(app)

    response = app.get('/')
    assert response.status_code == 200

def test_should_load_email_input(app):
    """Start with a blank database."""
    config = config_items('fields')
    response = app.get('/')
    
    html = response.data.decode()
    # print(html)

    formsData = {"email":"@@@@"}
    response = app.post('/', data=formsData)
    print(response.data.decode())
    print(response.status_code)

    assert '<input class="required enabled" id="email" name="email" required type="text" value="">&nbsp;@dug.com' in html
