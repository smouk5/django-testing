from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone

from news.forms import CommentForm
from news.models import Comment, News


@pytest.mark.django_db
class TestContent:
    def test_news_count_on_homepage_not_more_than_10(self, client):
        for i in range(11):
            News.objects.create(title=f"News {i}", text="Text")

        url = reverse("news:home")
        response = client.get(url)
        object_list = list(response.context["object_list"])
        assert len(object_list) <= 10

    def test_news_sorted_from_new_to_old(self, client):
        now = timezone.now()
        older = News.objects.create(title="Old", text="Text")
        newer = News.objects.create(title="New", text="Text")

        pairs = (
            (older, now - timedelta(days=1)),
            (newer, now),
        )
        for obj, dt in pairs:
            if hasattr(obj, "date"):
                obj.date = dt
                obj.save()
            elif hasattr(obj, "created"):
                obj.created = dt
                obj.save()
            elif hasattr(obj, "pub_date"):
                obj.pub_date = dt
                obj.save()

        url = reverse("news:home")
        response = client.get(url)
        object_list = list(response.context["object_list"])

        assert object_list[0].id == newer.id
        assert object_list[-1].id == older.id

    def test_comments_sorted_old_to_new_on_detail(self, client, author, news):
        now = timezone.now()

        old_comment = Comment.objects.create(
            news=news,
            author=author,
            text="old",
        )
        new_comment = Comment.objects.create(
            news=news,
            author=author,
            text="new",
        )

        pairs = (
            (old_comment, now - timedelta(hours=1)),
            (new_comment, now),
        )
        for obj, dt in pairs:
            if hasattr(obj, "created"):
                obj.created = dt
                obj.save()
            elif hasattr(obj, "created_at"):
                obj.created_at = dt
                obj.save()
            elif hasattr(obj, "date"):
                obj.date = dt
                obj.save()

        url = reverse("news:detail", args=(news.id,))
        response = client.get(url)

        
        if "comments" in response.context:
            comments = list(response.context["comments"])
        else:
            comments = list(response.context["news"].comment_set.all())

        assert comments[0].id == old_comment.id
        assert comments[-1].id == new_comment.id

    def test_anonymous_has_no_comment_form(self, client, news):
        url = reverse("news:detail", args=(news.id,))
        response = client.get(url)
        assert "form" not in response.context

    def test_authorized_has_comment_form(self, author_client, news):
        url = reverse("news:detail", args=(news.id,))
        response = author_client.get(url)
        assert "form" in response.context
        assert isinstance(response.context["form"], CommentForm)
