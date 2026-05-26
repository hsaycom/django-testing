import pytest
from http import HTTPStatus

pytestmark = pytest.mark.django_db


def test_home_page_available_for_anonymous_user(client, home_url):
    """Главная страница доступна анонимному пользователю."""
    response = client.get(home_url)
    assert response.status_code == HTTPStatus.OK


def test_news_detail_page_available_for_anonymous_user(
        client, news, detail_url
):
    """Страница отдельной новости доступна анонимному пользователю."""
    response = client.get(detail_url(news.id))
    assert response.status_code == HTTPStatus.OK


def test_edit_and_delete_pages_available_for_author(
        author_client, comment, edit_url, delete_url
):
    """Страницы удаления и редактирования доступны автору комментария."""
    response = author_client.get(edit_url(comment.id))
    assert response.status_code == HTTPStatus.OK

    response = author_client.get(delete_url(comment.id))
    assert response.status_code == HTTPStatus.OK


def test_edit_and_delete_pages_redirect_for_anonymous(
        client, comment, login_url, edit_url, delete_url
):
    """Анонимный пользователь перенаправляется на страницу логина."""
    for url_func in [edit_url, delete_url]:
        url = url_func(comment.id)
        redirect_url = f'{login_url}?next={url}'
        response = client.get(url)
        assert response.status_code == HTTPStatus.FOUND
        assert response.url == redirect_url


def test_edit_and_delete_pages_return_404_for_not_author(
        not_author_client, comment, edit_url, delete_url
):
    """Пользователь не может зайти на страницы чужих комментариев."""
    response = not_author_client.get(edit_url(comment.id))
    assert response.status_code == HTTPStatus.NOT_FOUND

    response = not_author_client.get(delete_url(comment.id))
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_auth_pages_available_for_anonymous_user(
        client, login_url, signup_url, logout_url
):
    """Страницы регистрации, входа и выхода доступны всем."""
    response = client.get(login_url)
    assert response.status_code == HTTPStatus.OK

    response = client.get(signup_url)
    assert response.status_code == HTTPStatus.OK

    response = client.post(logout_url)
    assert response.status_code in [HTTPStatus.OK, HTTPStatus.FOUND]
