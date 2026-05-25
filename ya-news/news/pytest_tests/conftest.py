import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test import Client

from news.models import News, Comment

User = get_user_model()

# Глобальные константы
FORM_DATA = {'text': 'Новый комментарий'}
BAD_FORM_DATA = {'text': 'Текст с запрещённым словом'}


@pytest.fixture
def author():
    """Автор комментария."""
    return User.objects.create_user(username='Автор')


@pytest.fixture
def not_author():
    """Другой пользователь."""
    return User.objects.create_user(username='Не автор')


@pytest.fixture
def author_client(author):
    """Клиент для автора комментария."""
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    """Клиент для другого пользователя."""
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def news():
    """Новость."""
    return News.objects.create(
        title='Заголовок новости',
        text='Текст новости'
    )


@pytest.fixture
def comment(author, news):
    """Комментарий автора к новости."""
    return Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария'
    )


@pytest.fixture
def list_of_news():
    """Список из 15 новостей для проверки пагинации."""
    news_list = [
        News(
            title=f'Новость {i}',
            text=f'Текст новости {i}',
            date=f'2024-01-{i + 1:02d}'
        )
        for i in range(15)
    ]
    News.objects.bulk_create(news_list)
    return News.objects.all()


@pytest.fixture
def list_of_comments(news, author, not_author):
    """Список комментариев к новости для проверки сортировки."""
    comments = [
        Comment(
            news=news,
            author=author if i % 2 == 0 else not_author,
            text=f'Комментарий {i}',
            created=f'2024-01-{i + 1:02d} 12:00:00'
        )
        for i in range(5)
    ]
    Comment.objects.bulk_create(comments)
    return Comment.objects.all()


# ========== URL FIXTURES ==========

@pytest.fixture
def home_url():
    """URL главной страницы."""
    return reverse('news:home')


@pytest.fixture
def detail_url():
    """URL страницы отдельной новости."""
    return lambda news_id: reverse('news:detail', args=(news_id,))


@pytest.fixture
def login_url():
    """URL страницы входа."""
    return reverse('users:login')


@pytest.fixture
def signup_url():
    """URL страницы регистрации."""
    return reverse('users:signup')


@pytest.fixture
def logout_url():
    """URL страницы выхода."""
    return reverse('users:logout')


@pytest.fixture
def edit_url():
    """URL редактирования комментария."""
    return lambda comment_id: reverse('news:edit', args=(comment_id,))


@pytest.fixture
def delete_url():
    """URL удаления комментария."""
    return lambda comment_id: reverse('news:delete', args=(comment_id,))
