from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class BaseTestCase(TestCase):
    """Базовый класс для всех тестов."""

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create_user(username='Автор')
        cls.reader = User.objects.create_user(username='Читатель')
        # Создаём заметку для тестов
        from notes.models import Note
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст заметки',
            slug='note-slug',
            author=cls.author
        )

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(self.author)
        self.reader_client = Client()
        self.reader_client.force_login(self.reader)
        self.anonymous_client = Client()


# Константы с URL
NOTES_HOME_URL = reverse('notes:home')
NOTES_LIST_URL = reverse('notes:list')
NOTES_ADD_URL = reverse('notes:add')
NOTES_SUCCESS_URL = reverse('notes:success')
NOTES_DETAIL_URL = reverse('notes:detail', args=('note-slug',))
NOTES_EDIT_URL = reverse('notes:edit', args=('note-slug',))
NOTES_DELETE_URL = reverse('notes:delete', args=('note-slug',))

# Константы с URL для пользователей
USERS_LOGIN_URL = reverse('users:login')
USERS_SIGNUP_URL = reverse('users:signup')
USERS_LOGOUT_URL = reverse('users:logout')
