from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='author', password='pass')
        cls.other_user = User.objects.create_user(username='reader', password='pass')

        cls.note = Note.objects.create(
            title='Заметка автора',
            text='Текст',
            slug='author-note',
            author=cls.user
        )

        cls.home_url = reverse('notes:home')
        cls.list_url = reverse('notes:list')
        cls.add_url = reverse('notes:add')
        cls.success_url = reverse('notes:success')

        cls.detail_url = reverse('notes:detail', args=(cls.note.slug,))
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))

        cls.login_url = reverse('users:login')

    def test_homepage_available_for_anonymous_user(self):
        response = self.client.get(self.home_url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_available_for_authenticated_user(self):
        self.client.force_login(self.user)
        for url in (self.list_url, self.add_url, self.success_url):
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_detail_edit_delete_available_only_for_author(self):
        # Автор — доступ есть
        self.client.force_login(self.user)
        for url in (self.detail_url, self.edit_url, self.delete_url):
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

        # Другой пользователь — 404
        self.client.force_login(self.other_user)
        for url in (self.detail_url, self.edit_url, self.delete_url):
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_anonymous_user_redirected_to_login(self):
        protected_urls = (
            self.list_url, self.add_url, self.success_url,
            self.detail_url, self.edit_url, self.delete_url,
        )
        for url in protected_urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.FOUND)
                self.assertRedirects(response, f'{self.login_url}?next={url}')

    def test_auth_pages_available_for_all_users(self):
        signup_url = reverse('users:signup')
        login_url = reverse('users:login')
        logout_url = reverse('users:logout')

        # signup и login доступны по GET
        for url in (signup_url, login_url):
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

        # logout: маршрут доступен всем, но GET может быть запрещён (405) — это нормально
        response = self.client.get(logout_url)
        self.assertIn(
            response.status_code,
            (HTTPStatus.OK, HTTPStatus.FOUND, HTTPStatus.METHOD_NOT_ALLOWED)
        )
