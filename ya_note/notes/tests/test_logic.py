from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note

User = get_user_model()


class TestLogic(TestCase):
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
        cls.add_url = reverse("notes:add")
        cls.edit_url = reverse("notes:edit", args=(cls.note.slug,))
        cls.delete_url = reverse("notes:delete", args=(cls.note.slug,))
        cls.detail_url = reverse("notes:detail", args=(cls.note.slug,))

    def test_auth_can_create_note(self):
        self.client.force_login(self.author)
        before = Note.objects.count()

        data = {"title": "Новая", "text": "Текст", "slug": "new-note"}
        response = self.client.post(self.add_url, data=data)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(Note.objects.count(), before + 1)

    def test_anon_cant_create_note(self):
        before = Note.objects.count()
        data = {"title": "Новая", "text": "Текст", "slug": "new-note-2"}
        response = self.client.post(self.add_url, data=data)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(Note.objects.count(), before)

    def test_unique_slug_required(self):
        self.client.force_login(self.author)
        before = Note.objects.count()

        data = {"title": "Другая", "text": "Текст", "slug": self.note.slug}
        response = self.client.post(self.add_url, data=data)

        self.assertEqual(Note.objects.count(), before)
        form = response.context["form"]
        self.assertIn("slug", form.errors)
        self.assertEqual(form.errors["slug"][0], self.note.slug + WARNING)

    def test_slug_autocreated_if_empty(self):
        self.client.force_login(self.author)
        before = Note.objects.count()

        title = "Заметка без слага"
        data = {"title": title, "text": "Текст", "slug": ""}
        self.client.post(self.add_url, data=data)

        self.assertEqual(Note.objects.count(), before + 1)
        created = Note.objects.order_by("-id").first()
        expected = slugify(title)[:100]
        self.assertEqual(created.slug, expected)

    def test_author_can_edit_delete_own(self):
        self.client.force_login(self.author)

        data = {"title": "Обновили", "text": "Новый", "slug": self.note.slug}
        response = self.client.post(self.edit_url, data=data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

        self.note.refresh_from_db()
        self.assertEqual(self.note.title, "Обновили")

        before = Note.objects.count()
        response = self.client.post(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(Note.objects.count(), before - 1)

    def test_user_cant_edit_delete_foreign(self):
        self.client.force_login(self.reader)

        data = {"title": "Взлом", "text": "Текст", "slug": self.note.slug}
        response = self.client.post(self.edit_url, data=data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

        response = self.client.post(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
