from http import HTTPStatus

from notes.tests.base import BaseNoteTestCase


class TestRoutes(BaseNoteTestCase):
    def test_home_available_for_anon(self):
        response = self.client.get(self.home_url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_available_for_auth_user(self):
        for url in (self.list_url, self.add_url, self.success_url):
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_detail_edit_delete_only_for_author(self):
        for url in (self.detail_url, self.edit_url, self.delete_url):
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

        for url in (self.detail_url, self.edit_url, self.delete_url):
            with self.subTest(url=url):
                response = self.reader_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_anon_redirected_to_login(self):
        protected_urls = (
            self.list_url,
            self.add_url,
            self.success_url,
            self.detail_url,
            self.edit_url,
            self.delete_url,
        )
        for url in protected_urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.FOUND)
                self.assertRedirects(response, f"{self.login_url}?next={url}")

    def test_auth_pages_available_for_all(self):
        for url in (self.signup_url, self.login_url):
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_logout_available_for_anon(self):
        response = self.client.post(self.logout_url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "registration/logout.html")
