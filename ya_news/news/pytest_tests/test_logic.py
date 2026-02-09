from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment

pytestmark = pytest.mark.django_db

COMMENT_TEXT = "Комментарий"
NEW_TEXT = "Новый текст"


def test_anon_cant_create_comment(client, detail_url, login_url):
    Comment.objects.all().delete()
    before = Comment.objects.count()

    response = client.post(detail_url, data={"text": COMMENT_TEXT})

    assert Comment.objects.count() == before
    expected = f"{login_url}?next={detail_url}"
    assertRedirects(response, expected)


def test_auth_can_create_comment(author_client, author, news, detail_url):
    Comment.objects.all().delete()
    before = Comment.objects.count()

    response = author_client.post(detail_url, data={"text": COMMENT_TEXT})

    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == before + 1

    created = Comment.objects.get()
    assert created.text == COMMENT_TEXT
    assert created.author == author
    assert created.news == news


@pytest.mark.parametrize("bad_word", BAD_WORDS)
def test_bad_words_block_comment(author_client, detail_url, bad_word):
    Comment.objects.all().delete()
    before = Comment.objects.count()

    bad_text = f"текст {bad_word}"
    response = author_client.post(detail_url, data={"text": bad_text})

    assert response.status_code == HTTPStatus.OK
    assert Comment.objects.count() == before

    form = response.context["form"]
    assert "text" in form.errors
    assert WARNING in form.errors["text"][0]


def test_author_can_edit_own_comment(author_client, edit_url, comment):
    old = Comment.objects.get(pk=comment.pk)

    response = author_client.post(edit_url, data={"text": NEW_TEXT})
    assert response.status_code == HTTPStatus.FOUND

    updated = Comment.objects.get(pk=comment.pk)
    assert updated.text == NEW_TEXT
    assert updated.author == old.author
    assert updated.news == old.news


def test_author_can_delete_own_comment(author_client, delete_url, comment):
    before = Comment.objects.count()

    response = author_client.post(delete_url)
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == before - 1


def test_user_cant_edit_foreign_comment(reader_client, edit_url, comment):
    before = Comment.objects.get(pk=comment.pk)

    response = reader_client.post(edit_url, data={"text": NEW_TEXT})
    assert response.status_code == HTTPStatus.NOT_FOUND

    after = Comment.objects.get(pk=comment.pk)
    assert after.text == before.text
    assert after.author == before.author
    assert after.news == before.news


def test_user_cant_delete_foreign_comment(reader_client, delete_url, comment):
    before = Comment.objects.count()

    response = reader_client.post(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == before
