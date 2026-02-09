from notes.forms import NoteForm
from notes.tests.base import BaseNoteTestCase


class TestContent(BaseNoteTestCase):
    def test_note_in_list_for_author(self):
        response = self.author_client.get(self.list_url)
        object_list = response.context["object_list"]
        self.assertIn(self.note, object_list)

    def test_note_not_in_list_for_reader(self):
        response = self.reader_client.get(self.list_url)
        object_list = response.context["object_list"]
        self.assertNotIn(self.note, object_list)

    def test_pages_contain_form(self):
        pages = (
            self.add_url,
            self.edit_url,
        )
        for url in pages:
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertIn("form", response.context)
                self.assertIsInstance(response.context["form"], NoteForm)
