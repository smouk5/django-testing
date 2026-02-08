from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


@pytest.mark.django_db
class TestLogic:
    def test_anonymous_cannot_create_comment(self, client, news):
        url = reverse("news:detail", args=(news.id,))
        before = Comment.objects.count()

        response = client.post(url, data={"text": "Комментарий"})

        assert Comment.objects.count() == before
        login_url = reverse("users:login")
        expected = f"{login_url}?next={url}"
        assertRedirects(response, expected)

    def test_authorized_can_create_comment(self, author_client, author, news):
        url = reverse("news:detail", args=(news.id,))
        before = Comment.objects.count()

        response = author_client.post(url, data={"text": "Комментарий"})
        assert response.status_code in (HTTPStatus.FOUND, HTTPStatus.OK)
        assert Comment.objects.count() == before + 1

        created = Comment.objects.latest("id")
        assert created.author == author
        assert created.news == news

    def test_comment_with_bad_words_not_published(self, author_client, news):
        url = reverse("news:detail", args=(news.id,))
        before = Comment.objects.count()

        bad_text = f"Это {BAD_WORDS[0]}"
        response = author_client.post(url, data={"text": bad_text})

        assert Comment.objects.count() == before
        assert response.status_code == HTTPStatus.OK
        assert "form" in response.context
        assert WARNING in response.context["form"].errors["text"][0]

    def test_author_can_edit_and_delete_own_comment(self, author_client, comment):
        edit_url = reverse("news:edit", args=(comment.id,))
        delete_url = reverse("news:delete", args=(comment.id,))

        response = author_client.post(edit_url, data={"text": "Новый текст"})
        assert response.status_code in (HTTPStatus.FOUND, HTTPStatus.OK)
        comment.refresh_from_db()
        assert comment.text == "Новый текст"

        before = Comment.objects.count()
        response = author_client.post(delete_url)
        assert response.status_code in (HTTPStatus.FOUND, HTTPStatus.OK)
        assert Comment.objects.count() == before - 1

    def test_user_cannot_edit_or_delete_other_users_comment(self, reader_client, comment):
        edit_url = reverse("news:edit", args=(comment.id,))
        delete_url = reverse("news:delete", args=(comment.id,))

        response = reader_client.get(edit_url)
        assert response.status_code == HTTPStatus.NOT_FOUND

        response = reader_client.get(delete_url)
        assert response.status_code == HTTPStatus.NOT_FOUND
