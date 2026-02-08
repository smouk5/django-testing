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
        cls.user = User.objects.create_user(username='author', password='pass')
        cls.other_user = User.objects.create_user(username='other', password='pass')

        cls.add_url = reverse('notes:add')
        cls.login_url = reverse('users:login')

        cls.note = Note.objects.create(
            title='Заметка автора',
            text='Текст',
            slug='author-note',
            author=cls.user
        )
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))

    def test_authenticated_user_can_create_note(self):
        self.client.force_login(self.user)
        notes_before = Note.objects.count()

        form_data = {'title': 'Новая', 'text': 'Текст', 'slug': 'new-note'}
        response = self.client.post(self.add_url, data=form_data)

        self.assertEqual(Note.objects.count(), notes_before + 1)
        created = Note.objects.get(slug='new-note')
        self.assertEqual(created.author, self.user)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_anonymous_user_cannot_create_note(self):
        notes_before = Note.objects.count()

        form_data = {'title': 'Анонимная', 'text': 'Текст', 'slug': 'anon-note'}
        response = self.client.post(self.add_url, data=form_data)

        self.assertEqual(Note.objects.count(), notes_before)
        self.assertRedirects(response, f'{self.login_url}?next={self.add_url}')

    def test_cannot_create_two_notes_with_same_slug(self):
        self.client.force_login(self.user)

        form_data = {'title': 'Ещё одна', 'text': 'Текст', 'slug': self.note.slug}
        response = self.client.post(self.add_url, data=form_data)

        # При ошибке валидации форма возвращается со статусом 200 и ошибками
        self.assertEqual(response.status_code, HTTPStatus.OK)
        form = response.context['form']
        self.assertIn(self.note.slug + WARNING, form.errors['slug'])

    def test_slug_created_automatically_if_empty(self):
        self.client.force_login(self.user)

        title = 'Заметка без слага'
        form_data = {'title': title, 'text': 'Текст', 'slug': ''}
        self.client.post(self.add_url, data=form_data)

        expected_slug = slugify(title)[:100]
        self.assertTrue(Note.objects.filter(slug=expected_slug).exists())

    def test_user_can_edit_and_delete_own_note(self):
        self.client.force_login(self.user)

        # edit
        new_data = {'title': 'Изменено', 'text': 'Новый текст', 'slug': self.note.slug}
        response = self.client.post(self.edit_url, data=new_data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

        self.note.refresh_from_db()
        self.assertEqual(self.note.title, 'Изменено')
        self.assertEqual(self.note.text, 'Новый текст')

        # delete
        notes_before = Note.objects.count()
        response = self.client.post(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(Note.objects.count(), notes_before - 1)

    def test_user_cannot_edit_or_delete_other_users_notes(self):
        self.client.force_login(self.other_user)

        response = self.client.get(self.edit_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

        response = self.client.get(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
