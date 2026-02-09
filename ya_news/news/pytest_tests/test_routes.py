from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects
from pytest_lazyfixture import lazy_fixture as lf

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    "url_fixture, expected_status, client_fixture",
    (
        ("home_url", HTTPStatus.OK, lf("client")),
        ("detail_url", HTTPStatus.OK, lf("client")),
        ("login_url", HTTPStatus.OK, lf("client")),
        ("signup_url", HTTPStatus.OK, lf("client")),
    ),
)
def test_public_pages_status(
    request,
    url_fixture,
    expected_status,
    client_fixture,
):
    url = request.getfixturevalue(url_fixture)
    response = client_fixture.get(url)
    assert response.status_code == expected_status


def test_logout_available_for_anonymous(client, logout_url):
    response = client.post(logout_url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    "url_fixture, client_fixture, expected_status",
    (
        ("edit_url", lf("author_client"), HTTPStatus.OK),
        ("delete_url", lf("author_client"), HTTPStatus.OK),
        ("edit_url", lf("reader_client"), HTTPStatus.NOT_FOUND),
        ("delete_url", lf("reader_client"), HTTPStatus.NOT_FOUND),
    ),
)
def test_edit_delete_statuses(
    request,
    url_fixture,
    client_fixture,
    expected_status,
):
    url = request.getfixturevalue(url_fixture)
    response = client_fixture.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize("url_fixture", ("edit_url", "delete_url"))
def test_anon_redirected_to_login(
    request,
    client,
    login_url,
    url_fixture,
):
    url = request.getfixturevalue(url_fixture)
    expected = f"{login_url}?next={url}"
    response = client.get(url)
    assertRedirects(response, expected)
