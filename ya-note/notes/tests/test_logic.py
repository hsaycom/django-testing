from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse

from notes.models import Note
from notes.tests.base import (
    BaseTestCase, NOTES_ADD_URL, NOTES_SUCCESS_URL,
    NOTES_EDIT_URL, NOTES_DELETE_URL
)

User = get_user_model()


class TestLogic(BaseTestCase):
    """Тестирование логики работы с заметками."""

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.note_data = {
            'title': 'Новая заметка',
            'text': 'Текст новой заметки',
            'slug': 'new-note-slug'
        }
        cls.note_data_without_slug = {
            'title': 'Заголовок для автослага',
            'text': 'Текст заметки'
        }

    def setUp(self):
        super().setUp()
        self.anonymous_client = Client()

    def test_authenticated_user_can_create_note(self):
        """Залогиненный пользователь может создать заметку."""
        response = self.author_client.post(
            NOTES_ADD_URL, data=self.note_data
        )
        self.assertRedirects(response, NOTES_SUCCESS_URL)
        self.assertEqual(Note.objects.count(), 1)

        new_note = Note.objects.get()
        self.assertEqual(new_note.title, self.note_data['title'])
        self.assertEqual(new_note.text, self.note_data['text'])
        self.assertEqual(new_note.slug, self.note_data['slug'])
        self.assertEqual(new_note.author, self.author)

    def test_anonymous_user_cannot_create_note(self):
        """Анонимный пользователь не может создать заметку."""
        response = self.anonymous_client.post(
            NOTES_ADD_URL, data=self.note_data
        )
        login_url = reverse('users:login')
        redirect_url = f'{login_url}?next={NOTES_ADD_URL}'
        self.assertRedirects(response, redirect_url)
        self.assertEqual(Note.objects.count(), 0)

    def test_cannot_create_two_notes_with_same_slug(self):
        """Невозможно создать две заметки с одинаковым slug."""
        self.author_client.post(NOTES_ADD_URL, data=self.note_data)
        self.assertEqual(Note.objects.count(), 1)

        second_note_data = self.note_data.copy()
        second_note_data['title'] = 'Другая заметка'
        response = self.author_client.post(
            NOTES_ADD_URL, data=second_note_data
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form'].errors)
        self.assertEqual(Note.objects.count(), 1)

    def test_slug_auto_generation(self):
        """Slug автоматически формируется, если не заполнен."""
        self.author_client.post(
            NOTES_ADD_URL, data=self.note_data_without_slug
        )
        self.assertEqual(Note.objects.count(), 1)

        new_note = Note.objects.get()
        expected_slug = 'zagolovok-dlya-avtoslaga'
        self.assertEqual(new_note.slug, expected_slug)
        self.assertEqual(new_note.title, self.note_data_without_slug['title'])
        self.assertEqual(new_note.text, self.note_data_without_slug['text'])
        self.assertEqual(new_note.author, self.author)

    def test_author_can_edit_own_note(self):
        """Пользователь может редактировать свои заметки."""
        self.author_client.post(NOTES_ADD_URL, data=self.note_data)
        note = Note.objects.get()
        edit_url = NOTES_EDIT_URL(note.slug)
        response = self.author_client.post(
            edit_url, data=self.note_data
        )
        self.assertRedirects(response, NOTES_SUCCESS_URL)

        updated_note = Note.objects.get(id=note.id)
        self.assertEqual(updated_note.title, self.note_data['title'])
        self.assertEqual(updated_note.text, self.note_data['text'])
        self.assertEqual(updated_note.author, self.author)
        self.assertEqual(Note.objects.count(), 1)

    def test_author_can_delete_own_note(self):
        """Пользователь может удалять свои заметки."""
        self.author_client.post(NOTES_ADD_URL, data=self.note_data)
        self.assertEqual(Note.objects.count(), 1)

        note = Note.objects.get()
        delete_url = NOTES_DELETE_URL(note.slug)
        response = self.author_client.post(delete_url)
        self.assertRedirects(response, NOTES_SUCCESS_URL)
        self.assertEqual(Note.objects.count(), 0)

    def test_cannot_edit_other_users_note(self):
        """Пользователь не может редактировать чужие заметки."""
        self.author_client.post(NOTES_ADD_URL, data=self.note_data)
        note = Note.objects.get()
        edit_url = NOTES_EDIT_URL(note.slug)
        response = self.reader_client.post(
            edit_url, data=self.note_data
        )
        self.assertEqual(response.status_code, 404)

        unchanged_note = Note.objects.get(id=note.id)
        self.assertEqual(unchanged_note.title, self.note_data['title'])
        self.assertEqual(unchanged_note.text, self.note_data['text'])
        self.assertEqual(unchanged_note.author, self.author)
        self.assertEqual(Note.objects.count(), 1)

    def test_cannot_delete_other_users_note(self):
        """Пользователь не может удалять чужие заметки."""
        self.author_client.post(NOTES_ADD_URL, data=self.note_data)
        self.assertEqual(Note.objects.count(), 1)

        note = Note.objects.get()
        delete_url = NOTES_DELETE_URL(note.slug)
        response = self.reader_client.post(delete_url)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(Note.objects.count(), 1)

        unchanged_note = Note.objects.get(id=note.id)
        self.assertEqual(unchanged_note.title, self.note_data['title'])
        self.assertEqual(unchanged_note.text, self.note_data['text'])
        self.assertEqual(unchanged_note.author, self.author)
