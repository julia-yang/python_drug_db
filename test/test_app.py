from flask import Flask
import pytest

@pytest.fixture()
def app():
    app = Flask(__name__)
    app.config.update({
        "TESTING": True,
    })
    yield app



@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()


def test_name_search(client):
    response = client.post("/search", data={
        "search": "Amyvid",
        "select": "Name",
    })
    assert response.status_code == 200