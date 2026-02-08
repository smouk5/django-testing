from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects


@pytest.mark.django_db
class TestRoutes:
    def test_home_page_available_for_anonymous(self, client):
        url = reverse("news:home")
        response = client.get(url)
        assert response.status_code == HTTPStatus.OK

    def test_detail_page_available_for_anonymous(self, client, news):
        url = reverse("news:detail", args=(news.id,))
        response = client.get(url)
        assert response.status_code == HTTPStatus.OK

    def test_auth_pages_available_for_anonymous(self, client):
        for name in ("users:login", "users:signup"):
            url = reverse(name)
            response = client.get(url)
            assert response.status_code == HTTPStatus.OK

        logout_url = reverse("users:logout")
        response = client.get(logout_url)
        assert response.status_code != HTTPStatus.NOT_FOUND

    def test_edit_delete_comment_available_for_author(self, author_client, comment):
        for name in ("news:edit", "news:delete"):
            url = reverse(name, args=(comment.id,))
            response = author_client.get(url)
            assert response.status_code == HTTPStatus.OK

    def test_anonymous_redirected_from_edit_delete_to_login(self, client, comment):
        login_url = reverse("users:login")
        for name in ("news:edit", "news:delete"):
            url = reverse(name, args=(comment.id,))
            response = client.get(url)
            expected = f"{login_url}?next={url}"
            assertRedirects(response, expected)

    def test_user_cannot_edit_or_delete_other_users_comment(
        self, reader_client, comment
    ):
        for name in ("news:edit", "news:delete"):
            url = reverse(name, args=(comment.id,))
            response = reader_client.get(url)
            assert response.status_code == HTTPStatus.NOT_FOUND
