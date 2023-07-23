import pytest
from datetime import date
from news.models import News, Comment


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_client(author, client):
    client.force_login(author)
    return client


@pytest.fixture
def vasua(django_user_model):
    return django_user_model.objects.create(username='Вася')


@pytest.fixture
def vasua_client(vasua, client):
    client.force_login(vasua)
    return client


@pytest.fixture
def news():
    news = News.objects.create(
        title='Заголовок', text='Текст новости', date=date(2023, 5, 14)
    )
    return news


@pytest.fixture
def comment(author, news):
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария',
    )
    return comment


@pytest.fixture
def pk_for_kwargs(comment):
    return {'pk': comment.pk}
