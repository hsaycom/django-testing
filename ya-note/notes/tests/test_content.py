from notes.models import Note
from .base import BaseTestCase, NOTES_LIST_URL, NOTES_ADD_URL, NOTES_EDIT_URL


class TestContent(BaseTestCase):
    """Тестирование контента страниц."""

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.note = Note.objects.create(
            title='Заметка автора',
            text='Текст заметки автора',
            slug='author-note',
            author=cls.author
        )

    def test_note_in_context_on_list_page(self):
        """Заметка передаётся в object_list в словаре context."""
        response = self.author_client.get(NOTES_LIST_URL)
        object_list = response.context['object_list']
        self.assertIn(self.note, object_list)
        self.assertEqual(object_list.count(), 1)

    def test_notes_for_author(self):
        """В список заметок автора попадает только его заметка."""
        response = self.author_client.get(NOTES_LIST_URL)
        author_notes = response.context['object_list']
        self.assertEqual(author_notes.count(), 1)
        self.assertIn(self.note, author_notes)

    def test_notes_for_reader(self):
        """У читателя нет заметок в списке."""
        response = self.reader_client.get(NOTES_LIST_URL)
        reader_notes = response.context['object_list']
        self.assertEqual(reader_notes.count(), 0)

    def test_forms_on_create_and_edit_pages(self):
        """На страницы создания и редактирования передаются формы."""
        urls = [
            ('notes:add', NOTES_ADD_URL),
            ('notes:edit', NOTES_EDIT_URL(self.note.slug)),
        ]
        for name, url in urls:
            with self.subTest(name=name):
                response = self.author_client.get(url)
                self.assertIn('form', response.context)
