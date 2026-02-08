from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class TestContent(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='author', password='pass')
        cls.other_user = User.objects.create_user(username='other', password='pass')

        cls.user_note = Note.objects.create(
            title='Заметка 1',
            text='Текст 1',
            slug='note-1',
            author=cls.user
        )
        cls.other_note = Note.objects.create(
            title='Чужая заметка',
            text='Текст 2',
            slug='note-2',
            author=cls.other_user
        )

        cls.list_url = reverse('notes:list')
        cls.add_url = reverse('notes:add')
        cls.edit_url = reverse('notes:edit', args=(cls.user_note.slug,))

    def test_note_in_object_list_in_context(self):
        self.client.force_login(self.user)
        response = self.client.get(self.list_url)
        self.assertIn(self.user_note, response.context['object_list'])

    def test_other_user_notes_not_in_list(self):
        self.client.force_login(self.user)
        response = self.client.get(self.list_url)
        self.assertNotIn(self.other_note, response.context['object_list'])

    def test_create_and_edit_pages_have_form(self):
        self.client.force_login(self.user)
        for url in (self.add_url, self.edit_url):
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
