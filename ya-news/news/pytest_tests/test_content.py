import pytest
from django.conf import settings

from news.forms import CommentForm

pytestmark = pytest.mark.django_db

# Глобальные константы
NEWS_COUNT_ON_HOME_PAGE = getattr(settings, 'NEWS_COUNT_ON_HOME_PAGE', 10)


def test_news_count_on_home_page(client, list_of_news, home_url):
    """Количество новостей на главной странице — не более 10."""
    response = client.get(home_url)
    object_list = response.context['object_list']
    assert object_list.count() <= NEWS_COUNT_ON_HOME_PAGE


def test_news_order_by_date_desc(client, list_of_news, home_url):
    """Новости отсортированы от самой свежей к самой старой."""
    response = client.get(home_url)
    object_list = response.context['object_list']
    dates = [news.date for news in object_list]
    assert dates == sorted(dates, reverse=True)


def test_comments_order_by_date_asc(
        client, news, list_of_comments, detail_url
):
    """Комментарии отсортированы в хронологическом порядке."""
    response = client.get(detail_url(news.id))
    comments = response.context['news'].comment_set.all()
    created_dates = [comment.created for comment in comments]
    assert created_dates == sorted(created_dates)


def test_comment_form_for_anonymous_user(client, news, detail_url):
    """Анонимному пользователю недоступна форма для отправки."""
    response = client.get(detail_url(news.id))
    assert 'form' not in response.context


def test_comment_form_for_authorized_user(author_client, news, detail_url):
    """Авторизованному пользователю доступна форма для отправки."""
    response = author_client.get(detail_url(news.id))
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)


def test_no_form_on_news_page_without_news(client, detail_url):
    """Если новости не существует, форма комментария не отображается."""
    response = client.get(detail_url(99999))
    assert response.status_code == 404
