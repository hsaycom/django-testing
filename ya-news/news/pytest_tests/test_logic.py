import pytest

from news.models import Comment
from conftest import FORM_DATA, BAD_FORM_DATA

pytestmark = pytest.mark.django_db


def test_anonymous_user_cannot_create_comment(client, news, detail_url):
    """Анонимный пользователь не может отправить комментарий."""
    comments_count = Comment.objects.count()
    client.post(detail_url(news.id), data=FORM_DATA)
    assert Comment.objects.count() == comments_count


def test_authorized_user_can_create_comment(author_client, news, detail_url):
    """Авторизованный пользователь может отправить комментарий."""
    comments_count = Comment.objects.count()
    author_client.post(detail_url(news.id), data=FORM_DATA)
    assert Comment.objects.count() == comments_count + 1


def test_comment_with_bad_words_not_created(author_client, news, detail_url):
    """Если комментарий содержит запрещённые слова, он не будет опубликован."""
    comments_count = Comment.objects.count()
    author_client.post(detail_url(news.id), data=BAD_FORM_DATA)

    # Комментарий не должен быть создан
    assert Comment.objects.count() == comments_count


def test_author_can_edit_own_comment(author_client, comment, edit_url):
    """Авторизованный пользователь может редактировать свои комментарии."""
    new_text = 'Обновлённый текст комментария'
    response = author_client.post(
        edit_url(comment.id), data={'text': new_text}
    )
    assert response.status_code == 302
    comment.refresh_from_db()
    assert comment.text == new_text


def test_author_can_delete_own_comment(author_client, comment, delete_url):
    """Авторизованный пользователь может удалять свои комментарии."""
    response = author_client.post(delete_url(comment.id))
    assert response.status_code == 302
    assert not Comment.objects.filter(id=comment.id).exists()


def test_cannot_edit_other_users_comment(
        not_author_client, comment, edit_url
):
    """Авторизованный пользователь не может редактировать чужие комментарии."""
    original_text = comment.text
    response = not_author_client.post(
        edit_url(comment.id), data={'text': 'Попытка'}
    )
    assert response.status_code == 404
    comment.refresh_from_db()
    assert comment.text == original_text


def test_cannot_delete_other_users_comment(
        not_author_client, comment, delete_url
):
    """Авторизованный пользователь не может удалять чужие комментарии."""
    response = not_author_client.post(delete_url(comment.id))
    assert response.status_code == 404
    assert Comment.objects.filter(id=comment.id).exists()
