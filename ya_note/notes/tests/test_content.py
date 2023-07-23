
from django.urls import reverse
from django.test import TestCase
from django.contrib.auth import get_user_model

from notes.models import Note


User = get_user_model()


class TestContent(TestCase):
    LIST_URL = reverse('notes:list')

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Тьюринг')
        cls.note = Note.objects.create(
            title='Заголовок', text='Текст', author=cls.author
        )

    def test_individual_note_in_context(self):
        self.client.force_login(self.author)

        response = self.client.get(self.LIST_URL)
        self.assertEqual(response.status_code, 200)

        object_list = response.context['object_list']
        self.assertIn(self.note, object_list)

    def test_forg_not_org(self):
        another_user = User.objects.create(username='Мария Кьюри')
        another_note = Note.objects.create(
            title='Радиация',
            text='Первая женщина что ее открыла',
            author=another_user,
        )
        self.client.force_login(another_user)
        response = self.client.get(self.LIST_URL)
        self.assertEqual(response.status_code, 200)

        object_list = response.context['object_list']
        self.assertIn(another_note, object_list)
        self.assertNotIn(self.note, object_list)


class TestEditNote(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Тесла')
        cls.news = Note.objects.create(
            title='Тестовая новость',
            text='Просто текст.',
            slug=1,
            author=cls.author,
        )
        cls.edit_url = reverse('notes:edit', args=(cls.news.id,))

    def test_authorized_client_has_form(self):
        self.client.force_login(self.author)
        response = self.client.get(self.edit_url)
        self.assertIn('form', response.context)


class TestAddNote(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Пух')
        cls.news = Note.objects.create(
            title='Тестовая новость', text='Просто текст.', author=cls.author
        )
        cls.add_url = reverse('notes:add')

    def test_anonymous_client_has_no_form(self):
        self.client.force_login(self.author)
        response = self.client.get(self.add_url)
        self.assertIn('form', response.context)
