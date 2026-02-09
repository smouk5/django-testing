from http import HTTPStatus

from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note
from notes.tests.base import BaseNoteTestCase


class TestLogic(BaseNoteTestCase):
    def test_auth_can_create_note(self):
        before = Note.objects.count()

        data = {
            "title": "Новая",
            "text": "Текст",
            "slug": "new-note",
        }
        response = self.author_client.post(self.add_url, data=data)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(Note.objects.count(), before + 1)

        created = Note.objects.get(slug="new-note")
        self.assertEqual(created.title, data["title"])
        self.assertEqual(created.text, data["text"])
        self.assertEqual(created.slug, data["slug"])
        self.assertEqual(created.author, self.author)

    def test_anon_cant_create_note(self):
        before = Note.objects.count()

        data = {
            "title": "Новая",
            "text": "Текст",
            "slug": "new-note-2",
        }
        response = self.anon_client.post(self.add_url, data=data)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(Note.objects.count(), before)

    def test_unique_slug_required(self):
        before = Note.objects.count()

        data = {
            "title": "Другая",
            "text": "Текст",
            "slug": self.note.slug,
        }
        response = self.author_client.post(self.add_url, data=data)

        self.assertEqual(Note.objects.count(), before)
        form = response.context["form"]
        self.assertIn("slug", form.errors)
        self.assertEqual(form.errors["slug"][0], self.note.slug + WARNING)

    def test_slug_autocreated_if_empty(self):
        Note.objects.all().delete()

        title = "Заметка без слага"
        data = {
            "title": title,
            "text": "Текст",
            "slug": "",
        }
        response = self.author_client.post(self.add_url, data=data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

        created = Note.objects.get()
        self.assertEqual(created.title, title)
        self.assertEqual(created.slug, slugify(title))

    def test_author_can_edit_own_note(self):
        before = Note.objects.get(pk=self.note.pk)

        data = {
            "title": "Обновили",
            "text": "Новый текст",
            "slug": "updated-slug",
        }
        response = self.author_client.post(self.edit_url, data=data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

        after = Note.objects.get(pk=self.note.pk)
        self.assertEqual(after.title, data["title"])
        self.assertEqual(after.text, data["text"])
        self.assertEqual(after.slug, data["slug"])
        self.assertEqual(after.author, before.author)

    def test_author_can_delete_own_note(self):
        before = Note.objects.count()

        response = self.author_client.post(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(Note.objects.count(), before - 1)

    def test_user_cant_edit_foreign_note(self):
        before = Note.objects.get(pk=self.note.pk)

        data = {
            "title": "Взлом",
            "text": "Текст",
            "slug": self.note.slug,
        }
        response = self.reader_client.post(self.edit_url, data=data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

        after = Note.objects.get(pk=self.note.pk)
        self.assertEqual(after.title, before.title)
        self.assertEqual(after.text, before.text)
        self.assertEqual(after.slug, before.slug)
        self.assertEqual(after.author, before.author)

    def test_user_cant_delete_foreign_note(self):
        before_count = Note.objects.count()

        response = self.reader_client.post(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), before_count)
