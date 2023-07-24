import pytest
from http import HTTPStatus
from django.urls import reverse
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_user_cannot_comment(client, news):
    url = reverse('news:detail', args=[news.pk])
    response = client.post(url)

    response = client.post(url, data={'text': 'Комментарий от анонима'})
    assert response.status_code == HTTPStatus.FOUND

    assert not Comment.objects.filter(
        news=news.pk, text='Комментарий от анонима'
    ).exists()


@pytest.mark.django_db
def test_authenticated_user_can_comment(author_client, news, author):
    url = reverse('news:detail', args=[news.pk])
    response = author_client.post(url)

    response = author_client.post(
        url, data={'text': 'Комментарий от пользователя'}
    )
    assert response.status_code == HTTPStatus.FOUND

    assert Comment.objects.filter(
        news=news.pk, author=author, text='Комментарий от пользователя'
    ).exists()


@pytest.mark.django_db
def test_comment_warring_text_for_authenticated_user(author_client, news):
    url = reverse('news:detail', args=[news.pk])

    response = author_client.post(url, data={'text': 'негодяй редиска'})
    assert response.status_code == HTTPStatus.OK

    form = response.context['form']
    assert 'text' in form.errors
    assert 'Не ругайтесь!' in form.errors['text']


@pytest.mark.django_db
def test_authenticated_user_can_edit_comment(author_client, comment, author):
    url = reverse('news:edit', kwargs={'pk': comment.pk})
    response = author_client.post(url)

    response = author_client.post(
        url,
        data={
            'comment': comment.pk,
            'author': author,
            'text': 'Коммент отредоктироваван атором',
        },
    )
    assert response.status_code == HTTPStatus.FOUND

    comment.refresh_from_db()
    assert Comment.objects.filter(
        news=comment.pk, author=author, text='Коммент отредоктироваван атором'
    ).exists()


@pytest.mark.django_db
def test_authenticated_user_can_delete_comment(author_client, comment):
    url = reverse('news:delete', kwargs={'pk': comment.pk})
    response = author_client.get(url)
    assert response.status_code == HTTPStatus.OK
    assert 'comment' in response.context

    response = author_client.post(url)
    assert response.status_code == HTTPStatus.FOUND

    assert not Comment.objects.filter(pk=comment.pk).exists()


@pytest.mark.django_db
def test_authenticated_user_cannot_edit_comment(vasua_client, comment):
    url = reverse('news:edit', kwargs={'pk': comment.pk})
    response = vasua_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.django_db
def test_authenticated_user_cannot_delete_comment(vasua_client, comment):
    url = reverse('news:delete', kwargs={'pk': comment.pk})
    response = vasua_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
