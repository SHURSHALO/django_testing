from http import HTTPStatus

import pytest
from django.urls import reverse

from news.models import News
from yanews.settings import NEWS_COUNT_ON_HOME_PAGE
from news.forms import CommentForm


@pytest.mark.django_db
def test_home_page_news_count(client):
    all_news = [
        News(title=f'Новость {index}', text='Просто текст.')
        for index in range(NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    News.objects.bulk_create(all_news)

    url = reverse('news:home')
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK
    assert len(response.context['object_list']) == NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_home_page_news_order(client):
    url = reverse('news:home')
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK

    news_list = response.context['object_list']
    sorted_news = News.objects.order_by('date')

    assert list(news_list) == list(sorted_news)


def test_comments_order_on_news_detail(client, comment):
    pk_for_news = 1
    url = reverse('news:detail', args=[pk_for_news])
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK

    comment_list = response.context['object'].comment_set.all()

    assert list(comment_list) == list(comment_list.order_by('created'))


@pytest.mark.django_db
def test_comment_form_unavailable_for_anonymous_user(client, news):
    url = reverse('news:detail', args=[news.pk])
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK
    assert not isinstance(response.context.get('form'), CommentForm)


@pytest.mark.django_db
def test_comment_form_available_for_authenticated_user(author_client, news):
    url = reverse('news:detail', args=[news.pk])
    response = author_client.get(url)
    assert response.status_code == HTTPStatus.OK
    assert isinstance(response.context['form'], CommentForm)
