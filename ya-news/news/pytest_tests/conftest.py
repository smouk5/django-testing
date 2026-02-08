import pytest
from django.test.client import Client
from django.utils import timezone

from news.models import Comment, News


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create_user(username='author', password='pass')


@pytest.fixture
def reader(django_user_model):
    return django_user_model.objects.create_user(username='reader', password='pass')


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
    # Если у модели есть поле date/pub_date — обычно оно auto_now_add и можно не задавать.
    return News.objects.create(title='Заголовок', text='Текст')


@pytest.fixture
def comment(news, author):
    return Comment.objects.create(news=news, author=author, text='Комментарий')
