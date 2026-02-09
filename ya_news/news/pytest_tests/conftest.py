from datetime import timedelta

import pytest
from django.conf import settings
from django.test.client import Client
from django.urls import reverse
from django.utils import timezone

from news.models import Comment, News

NEWS_LIMIT = settings.NEWS_COUNT_ON_HOME_PAGE
NEWS_CREATE_COUNT = NEWS_LIMIT + 1

COMMENT_TEXT = "Комментарий"
NEW_COMMENT_TEXT = "Новый текст комментария"


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username="author")


@pytest.fixture
def reader(django_user_model):
    return django_user_model.objects.create(username="reader")


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def reader_client(reader):
    client = Client()
    client.force_login(reader)
    return client


@pytest.fixture
def news():
    return News.objects.create(title="Заголовок", text="Текст")


@pytest.fixture
def comment(author, news):
    return Comment.objects.create(
        news=news,
        author=author,
        text=COMMENT_TEXT,
    )


@pytest.fixture
def home_url():
    return reverse("news:home")


@pytest.fixture
def login_url():
    return reverse("users:login")


@pytest.fixture
def signup_url():
    return reverse("users:signup")


@pytest.fixture
def logout_url():
    return reverse("users:logout")


@pytest.fixture
def detail_url(news):
    return reverse("news:detail", args=(news.id,))


@pytest.fixture
def edit_url(comment):
    return reverse("news:edit", args=(comment.id,))


@pytest.fixture
def delete_url(comment):
    return reverse("news:delete", args=(comment.id,))


@pytest.fixture
def news_list():
    now = timezone.now()
    items = []
    for i in range(NEWS_CREATE_COUNT):
        item = News.objects.create(title=f"News {i}", text="Text")
        items.append(item)

    for idx, item in enumerate(items):
        dt = now - timedelta(minutes=idx)
        News.objects.filter(pk=item.pk).update(date=dt)

    return items


@pytest.fixture
def comments_list(author, news):
    now = timezone.now()
    items = []
    for i in range(5):
        obj = Comment.objects.create(
            news=news,
            author=author,
            text=f"c{i}",
        )
        items.append(obj)

    for idx, obj in enumerate(items):
        dt = now - timedelta(minutes=(10 - idx))
        Comment.objects.filter(pk=obj.pk).update(created=dt)

    return items
