import pytest
from http import HTTPStatus
from django.urls import reverse
from datetime import date
from news.models import News, Comment


@pytest.mark.django_db
def test_home_page_news_count(client):
    for i in range(15):
        News.objects.create(title=f'Заголовок {i}', text=f'Текст новости {i}')

    url = reverse('news:home')
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK
    assert len(response.context['object_list']) <= 10


@pytest.mark.django_db
def test_home_page_news_order(client):
    news1 = News.objects.create(
        title='Заголовок 1', text='Текст новости 1', date=date(1990, 7, 30)
    )
    news2 = News.objects.create(
        title='Заголовок 2', text='Текст новости 2', date=date(2001, 6, 15)
    )
    news3 = News.objects.create(
        title='Заголовок 3', text='Текст новости 3', date=date(1945, 9, 2)
    )

    url = reverse('news:home')
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK

    news_list = response.context['object_list']
    assert news_list[0] == news2
    assert news_list[1] == news1
    assert news_list[2] == news3


def test_comments_order_on_news_detail(
    client, comment, news, pk_for_kwargs, author
):
    comments_data = [
        {'text': 'Комментарий 1', 'created': date(1945, 9, 2)},
        {'text': 'Комментарий 2', 'created': date(2001, 9, 11)},
        {'text': 'Комментарий 3', 'created': date(1703, 5, 16)},
    ]

    for comment_data in comments_data:
        Comment.objects.create(
            news=news,
            author=author,
            text=comment_data['text'],
            created=comment_data['created'],
        )

    url = reverse('news:detail', kwargs=pk_for_kwargs)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK

    comment_list = response.context['object'].comment_set.all()

    for i in range(1, len(comment_list)):
        assert comment_list[i].created >= comment_list[i - 1].created


@pytest.mark.django_db
def test_comment_form_unavailable_for_anonymous_user(client, news):
    url = reverse('news:detail', args=[news.pk])
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK
    assert 'form' not in response.context


@pytest.mark.django_db
def test_comment_form_available_for_authenticated_user(author_client, news):
    url = reverse('news:detail', args=[news.pk])
    response = author_client.get(url)
    assert response.status_code == HTTPStatus.OK
    assert 'form' in response.context
