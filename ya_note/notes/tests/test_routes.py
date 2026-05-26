from http import HTTPStatus

from notes.tests.base import (
    BaseTestCase, NOTES_HOME_URL, NOTES_LIST_URL, NOTES_SUCCESS_URL,
    NOTES_ADD_URL, NOTES_DETAIL_URL, NOTES_EDIT_URL, NOTES_DELETE_URL,
    USERS_LOGIN_URL, USERS_SIGNUP_URL, USERS_LOGOUT_URL
)


class TestRoutes(BaseTestCase):
    """Тестирование доступности страниц."""

    def test_pages_availability_for_anonymous_user(self):
        """Главная страница доступна анонимному пользователю."""
        response = self.anonymous_client.get(NOTES_HOME_URL)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_authenticated_user(self):
        """Аутентифицированному пользователю доступны notes/, done/, add/."""
        urls = [
            ('notes:list', NOTES_LIST_URL),
            ('notes:success', NOTES_SUCCESS_URL),
            ('notes:add', NOTES_ADD_URL),
        ]
        for name, url in urls:
            with self.subTest(name=name):
                response = self.author_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_note_pages_availability_for_author(self):
        """Страницы заметки, удаления и редактирования доступны автору."""
        urls = [
            ('notes:detail', NOTES_DETAIL_URL),
            ('notes:edit', NOTES_EDIT_URL),
            ('notes:delete', NOTES_DELETE_URL),
        ]
        for name, url in urls:
            with self.subTest(name=name):
                response = self.author_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_note_pages_availability_for_other_user(self):
        """Другой пользователь получает 404 при попытке доступа к заметке."""
        urls = [
            ('notes:detail', NOTES_DETAIL_URL),
            ('notes:edit', NOTES_EDIT_URL),
            ('notes:delete', NOTES_DELETE_URL),
        ]
        for name, url in urls:
            with self.subTest(name=name):
                response = self.reader_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_redirect_for_anonymous_client(self):
        """Анонимный пользователь перенаправляется на страницу логина."""
        urls = [
            ('notes:list', NOTES_LIST_URL),
            ('notes:success', NOTES_SUCCESS_URL),
            ('notes:add', NOTES_ADD_URL),
            ('notes:detail', NOTES_DETAIL_URL),
            ('notes:edit', NOTES_EDIT_URL),
            ('notes:delete', NOTES_DELETE_URL),
        ]
        for name, url in urls:
            with self.subTest(name=name):
                redirect_url = f'{USERS_LOGIN_URL}?next={url}'
                response = self.anonymous_client.get(url)
                self.assertRedirects(response, redirect_url)

    def test_availability_for_all_users(self):
        """Страницы регистрации, входа и выхода доступны всем."""
        users = [
            self.anonymous_client,
            self.author_client,
            self.reader_client
        ]

        urls_get = [
            ('users:login', USERS_LOGIN_URL),
            ('users:signup', USERS_SIGNUP_URL),
        ]

        for user in users:
            for name, url in urls_get:
                with self.subTest(user=user.__class__.__name__, name=name):
                    response = user.get(url)
                    self.assertEqual(response.status_code, HTTPStatus.OK)

        for user in users:
            with self.subTest(
                user=user.__class__.__name__, name='users:logout'
            ):
                response = user.post(USERS_LOGOUT_URL)
                self.assertIn(
                    response.status_code,
                    [HTTPStatus.OK, HTTPStatus.FOUND]
                )
