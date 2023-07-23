import pytest
from http import HTTPStatus
from pytest_django.asserts import assertRedirects
from django.urls import reverse


@pytest.mark.django_db
def test_home_availability_for_anonymous_user(client):
    url = reverse('news:home')
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_detail_availability_for_anonymous_user(client, news):
    url = reverse('news:detail', args=(news.pk,))
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, kwargs',
    (
        ('news:delete', pytest.lazy_fixture('pk_for_kwargs')),
        ('news:edit', pytest.lazy_fixture('pk_for_kwargs')),
    ),
)
def test_pages_availability_for_auth_user(author_client, name, kwargs):
    url = reverse(name, kwargs=kwargs)
    response = author_client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, kwargs',
    (
        ('news:delete', pytest.lazy_fixture('pk_for_kwargs')),
        ('news:edit', pytest.lazy_fixture('pk_for_kwargs')),
    ),
)
def test_redirects(client, name, kwargs):
    url = reverse(name, kwargs=kwargs)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK),
        (pytest.lazy_fixture('vasua_client'), HTTPStatus.NOT_FOUND),
    ),
)
@pytest.mark.parametrize(
    'name, kwargs',
    (
        ('news:delete', pytest.lazy_fixture('pk_for_kwargs')),
        ('news:edit', pytest.lazy_fixture('pk_for_kwargs')),
    ),
)
def test_pages_availability_for_different_users(
    parametrized_client, name, kwargs, expected_status
):
    url = reverse(name, kwargs=kwargs)
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name', ('news:home', 'users:login', 'users:logout', 'users:signup')
)
def test_pages_availability_for_anonymous_user(client, name):
    url = reverse(name)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK
