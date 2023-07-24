from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from notes.models import Note


User = get_user_model()


class TestRoutes(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.reader = User.objects.create(username='Читатель простой')
        cls.note = Note.objects.create(
            title='Заголовок', text='Текст', slug=1, author=cls.author
        )
        cls.user = User.objects.create(username='Мимо Крокодил')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)

    def test_home_page(self):
        url = '/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_note_edit_and_delete(self):
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for name in ('edit', 'delete', 'note'):
                with self.subTest(user=user, name=name):
                    url = f'/{name}/{self.note.id}/'
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        login_url = '/auth/login/'
        for name in ('edit', 'delete', 'note'):
            with self.subTest(name=name):
                url = f'/{name}/{self.note.id}/'
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

        for name in ('add', 'notes', 'done'):
            with self.subTest(name=name):
                url = f'/{name}/'
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

    def test_pages_availability(self):
        urls = (
            ('auth/login'),
            ('auth/logout'),
            ('auth/signup'),
        )
        for name in urls:
            with self.subTest(name=name):
                url = f'/{name}/'
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_add_notes_done(self):
        urls = ('add', 'notes', 'done')
        for name in urls:
            with self.subTest(name=name):
                url = f'/{name}/'
                response = self.auth_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
