import pytest

from news.models import Comment
from conftest import FORM_DATA, BAD_FORM_DATA

pytestmark = pytest.mark.django_db

NEW_COMMENT_TEXT = 'Обновлённый текст комментария'


def test_anonymous_user_cannot_create_comment(client, news, detail_url):
    """Анонимный пользователь не может отправить комментарий."""
    comments_count = Comment.objects.count()
    client.post(detail_url(news.id), data=FORM_DATA)
    assert Comment.objects.count() == comments_count


def test_authorized_user_can_create_comment(
        author_client, author, news, detail_url
):
    """Авторизованный пользователь может отправить комментарий."""
    comments_count = Comment.objects.count()
    author_client.post(detail_url(news.id), data=FORM_DATA)
    assert Comment.objects.count() == comments_count + 1

    # Проверяем, что комментарий создался с правильными полями
    new_comment = Comment.objects.last()
    assert new_comment.text == FORM_DATA['text']
    assert new_comment.author == author
    assert new_comment.news == news


def test_comment_with_bad_words_not_created(author_client, news, detail_url):
    """Если комментарий содержит запрещённые слова, он не будет опубликован."""
    comments_count = Comment.objects.count()
    author_client.post(detail_url(news.id), data=BAD_FORM_DATA)

    # Комментарий не должен быть создан
    assert Comment.objects.count() == comments_count


def test_author_can_edit_own_comment(author_client, comment, edit_url):
    """Авторизованный пользователь может редактировать свои комментарии."""
    response = author_client.post(
        edit_url(comment.id), data={'text': NEW_COMMENT_TEXT}
    )
    assert response.status_code == 302

    # Получаем свежую запись из базы
    updated_comment = Comment.objects.get(id=comment.id)
    assert updated_comment.text == NEW_COMMENT_TEXT
    assert updated_comment.author == comment.author
    assert updated_comment.news == comment.news
    assert Comment.objects.count() == 1


def test_author_can_delete_own_comment(author_client, comment, delete_url):
    """Авторизованный пользователь может удалять свои комментарии."""
    comments_count = Comment.objects.count()
    response = author_client.post(delete_url(comment.id))
    assert response.status_code == 302
    assert Comment.objects.count() == comments_count - 1
    assert not Comment.objects.filter(id=comment.id).exists()


def test_cannot_edit_other_users_comment(
        not_author_client, comment, edit_url
):
    """Авторизованный пользователь не может редактировать чужие комментарии."""
    response = not_author_client.post(
        edit_url(comment.id), data={'text': 'Попытка'}
    )
    assert response.status_code == 404

    # Проверяем, что запись не изменилась
    unchanged_comment = Comment.objects.get(id=comment.id)
    assert unchanged_comment.text == comment.text
    assert unchanged_comment.author == comment.author
    assert unchanged_comment.news == comment.news
    assert Comment.objects.count() == 1


def test_cannot_delete_other_users_comment(
        not_author_client, comment, delete_url
):
    """Авторизованный пользователь не может удалять чужие комментарии."""
    comments_count = Comment.objects.count()

    response = not_author_client.post(delete_url(comment.id))
    assert response.status_code == 404
    assert Comment.objects.count() == comments_count

    # Проверяем, что запись не изменилась
    unchanged_comment = Comment.objects.get(id=comment.id)
    assert unchanged_comment.text == comment.text
    assert unchanged_comment.author == comment.author
    assert unchanged_comment.news == comment.news
