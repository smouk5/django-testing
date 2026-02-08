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
        cls.author = User.objects.create_user(username="author", password="pass")
        cls.reader = User.objects.create_user(username="reader", password="pass")

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

    def test_authorized_user_can_create_note(self):
        self.client.force_login(self.author)
        before = Note.objects.count()

        form_data = {"title": "Новая", "text": "Текст", "slug": "new-note"}
        response = self.client.post(self.add_url, data=form_data)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(Note.objects.count(), before + 1)

    def test_anonymous_user_cannot_create_note(self):
        before = Note.objects.count()
        form_data = {"title": "Новая", "text": "Текст", "slug": "new-note-2"}
        response = self.client.post(self.add_url, data=form_data)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(Note.objects.count(), before)

    def test_cannot_create_two_notes_with_same_slug(self):
        self.client.force_login(self.author)
        before = Note.objects.count()

        form_data = {"title": "Другая", "text": "Текст", "slug": self.note.slug}
        response = self.client.post(self.add_url, data=form_data)

        self.assertEqual(Note.objects.count(), before)
        form = response.context["form"]
        self.assertIn("slug", form.errors)
        self.assertEqual(form.errors["slug"][0], self.note.slug + WARNING)

    def test_slug_created_automatically_if_empty(self):
        self.client.force_login(self.author)
        before = Note.objects.count()

        title = "Заметка без слага"
        form_data = {"title": title, "text": "Текст", "slug": ""}
        self.client.post(self.add_url, data=form_data)

        self.assertEqual(Note.objects.count(), before + 1)
        created = Note.objects.order_by("-id").first()
        self.assertEqual(created.slug, slugify(title)[:100])

    def test_author_can_edit_and_delete_own_note(self):
        self.client.force_login(self.author)

        edit_data = {"title": "Обновили", "text": "Новый текст", "slug": self.note.slug}
        response = self.client.post(self.edit_url, data=edit_data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

        self.note.refresh_from_db()
        self.assertEqual(self.note.title, "Обновили")

        before = Note.objects.count()
        response = self.client.post(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(Note.objects.count(), before - 1)

    def test_user_cannot_edit_or_delete_other_users_note(self):
        self.client.force_login(self.reader)

        edit_data = {
            "title": "Взлом",
            "text": "Текст",
            "slug": self.note.slug,
        }
        response = self.client.post(self.edit_url, data=edit_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

        response = self.client.post(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
