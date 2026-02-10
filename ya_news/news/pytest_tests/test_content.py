import pytest
from django.conf import settings

from news.forms import CommentForm

pytestmark = pytest.mark.django_db

NEWS_LIMIT = settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_count_limited(client, home_url, news_list):
    response = client.get(home_url)
    object_list = response.context["object_list"]
    assert object_list.count() == NEWS_LIMIT


def test_news_sorted_new_to_old(client, home_url, news_list):
    response = client.get(home_url)
    object_list = response.context["object_list"]

    dates = [obj.date for obj in object_list]
    expected = sorted(dates, reverse=True)
    assert dates == expected


def test_comments_sorted_old_to_new(client, detail_url, comments_list):
    response = client.get(detail_url)
    news_obj = response.context["news"]
    comments = news_obj.comment_set.all()

    dates = [obj.created for obj in comments]
    expected = sorted(dates)
    assert dates == expected


def test_anon_has_no_form(client, detail_url):
    response = client.get(detail_url)
    assert "form" not in response.context


def test_auth_has_form(author_client, detail_url):
    response = author_client.get(detail_url)
    assert "form" in response.context
    assert isinstance(response.context["form"], CommentForm)
