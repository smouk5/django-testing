from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class BaseNoteTestCase(TestCase):
    """База для всех unittest-тестов YaNote."""

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create_user(
            username="author",
            password="pass",
        )
        cls.reader = User.objects.create_user(
            username="reader",
            password="pass",
        )

        cls.note = Note.objects.create(
            title="Заметка автора",
            text="Текст",
            slug="author-note",
            author=cls.author,
        )

        # Реверсы — один раз, здесь.
        cls.home_url = reverse("notes:home")
        cls.list_url = reverse("notes:list")
        cls.add_url = reverse("notes:add")
        cls.success_url = reverse("notes:success")

        cls.detail_url = reverse("notes:detail", args=(cls.note.slug,))
        cls.edit_url = reverse("notes:edit", args=(cls.note.slug,))
        cls.delete_url = reverse("notes:delete", args=(cls.note.slug,))

        cls.signup_url = reverse("users:signup")
        cls.login_url = reverse("users:login")
        cls.logout_url = reverse("users:logout")

        # Клиенты — заранее, без force_login в тестах.
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)

        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
